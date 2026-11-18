"""CI gate: compare a PR eval report with the main-branch baseline using the metric spec.

    python -m lab9.gate --pr reports/eval_workflow.json --baseline reports/baseline_v1.json

exit 0 = merge, exit 1 = blocked. Safety metrics: max 0, no averaging away.
Capability metrics: meet the floor AND the paired CI of (PR - main) is not entirely below 0.
Thresholds may only get stricter on the same eval-set version (ratchet).
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from lab8.console import utf8_stdio
from lab9 import stats
from lab9.eval import SPEC, aggregate, load_spec, per_item
from lab9.graders import GRADERS


def integrity_check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> list[str]:
    """M7 (Expert): refuse to compare reports that cannot be trusted. Return a list of problems
    (empty = trustworthy). A gate that passes a broken report is worse than no gate.
    Must catch at least:
      - any metric value in pr["metrics"] that is NaN or inf
      - len(pr["rows"]) != manifest items x len(manifest seeds)   (dropped / duplicated rows)
      - the (item_id, seed) set of PR differs from the baseline's (cherry-picked seeds/items)
      - pr["evaluator_failures"] non-empty, or a row whose value for a graded spec metric is
        None (a crashed grader silently scores as "missing" and drops out of the mean)
      - base_spec given and a threshold in spec is LOOSER than in base_spec for the same
        eval-set version (ratchet: max may not rise, min may not fall, a blocking metric may
        not become non-blocking, a metric may not disappear; the same for spec["slices"],
        including dropping no_significant_drop)
      - an item's slice tags in PR rows differ from the baseline's (relabelling an item out of a
        slice hides its regression from the slice gate)"""
    problems: list[str] = []
    metrics = pr.get("metrics")
    if not isinstance(metrics, dict):
        problems.append("metrics missing or malformed")
        metrics = {}
    for metric, value in metrics.items():
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))
                                  or not math.isfinite(value)):
            problems.append(f"metric {metric} is not a finite number")
    if not isinstance(pr.get("evaluator_failures"), list):
        problems.append("evaluator_failures missing or malformed")
    elif pr["evaluator_failures"]:
        problems.append("evaluator_failures non-empty")

    rows = pr.get("rows")
    base_rows = base.get("rows")
    manifest = pr.get("manifest")
    if not isinstance(manifest, dict):
        problems.append("manifest missing or malformed")
        manifest = {}
    seeds = manifest.get("seeds")
    items = manifest.get("items")
    if not isinstance(rows, list) or not isinstance(base_rows, list):
        problems.append("rows missing or malformed")
        return problems
    if (not isinstance(seeds, list) or not seeds or
            any(isinstance(seed, bool) or not isinstance(seed, int) for seed in seeds) or
            len(seeds) != len(set(seeds))):
        problems.append("manifest seeds missing, invalid or duplicated")
    if not isinstance(items, int) or isinstance(items, bool) or items < 1:
        problems.append("manifest items invalid")
    if isinstance(seeds, list) and isinstance(items, int) and len(rows) != items * len(seeds):
        problems.append("row count does not match manifest items × seeds")

    def pairs(report_rows: list[dict]) -> list[tuple[str, int]]:
        found = []
        for row in report_rows:
            if (not isinstance(row, dict) or not isinstance(row.get("item_id"), str) or
                    isinstance(row.get("seed"), bool) or not isinstance(row.get("seed"), int)):
                problems.append("row has invalid item_id or seed")
                continue
            found.append((row["item_id"], row["seed"]))
        return found

    pr_pairs, base_pairs = pairs(rows), pairs(base_rows)
    if len(set(pr_pairs)) != len(pr_pairs):
        problems.append("duplicate (item_id, seed) row")
    if set(pr_pairs) != set(base_pairs):
        problems.append("PR (item_id, seed) set differs from baseline")
    if isinstance(items, int) and len({item for item, _ in pr_pairs}) != items:
        problems.append("unique item count differs from manifest")
    if isinstance(seeds, list) and any(seed not in seeds for _, seed in pr_pairs):
        problems.append("row seed missing from manifest")

    graded = [m["id"] for m in spec.get("metrics", []) if m.get("id") in GRADERS]
    needs_cost = any(m["id"] == "cost_per_success" for m in spec.get("metrics", []))
    scores_valid = costs_valid = True
    for row in rows:
        if not isinstance(row, dict):
            scores_valid = costs_valid = False
            continue
        for metric in graded:
            if not isinstance(row.get(metric), bool):
                problems.append(f"row {row.get('item_id')}@{row.get('seed')} has invalid {metric}")
                scores_valid = False
                break
        if needs_cost or "cost" in row:
            cost = row.get("cost")
            if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not math.isfinite(cost):
                problems.append(f"row {row.get('item_id')}@{row.get('seed')} has invalid cost")
                costs_valid = False
    if rows and scores_valid and costs_valid and all("cost" in row for row in rows):
        recomputed = aggregate(rows, graded, k_values=spec.get("pass_k", []))
        for metric, expected in recomputed.items():
            actual = metrics.get(metric)
            if expected is None:
                if actual is not None:
                    problems.append(f"metric {metric} differs from rows")
            elif not isinstance(actual, (int, float)) or not math.isfinite(actual) or not math.isclose(
                    actual, expected, rel_tol=0, abs_tol=5e-5):
                problems.append(f"metric {metric} differs from rows")
    base_by_pair = {(r["item_id"], r["seed"]): r for r in base_rows if isinstance(r, dict)
                    and isinstance(r.get("item_id"), str) and isinstance(r.get("seed"), int)}
    for row in rows:
        if not isinstance(row, dict):
            continue
        key = (row.get("item_id"), row.get("seed"))
        if not isinstance(key[0], str) or not isinstance(key[1], int):
            continue
        tags = row.get("slices")
        if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
            problems.append(f"invalid slice tags for {key[0]}@{key[1]}")
            continue
        old = base_by_pair.get(key)
        if old is not None and set(tags) != set(old.get("slices") or []):
            problems.append(f"slice tags changed for {key[0]}@{key[1]}")

    if base_spec is not None:
        if spec.get("eval_set_version") != base_spec.get("eval_set_version"):
            problems.append("eval_set_version changed without a matching baseline")
        for field, key_fn in (("metrics", lambda x: x["id"]),
                              ("slices", lambda x: (x["name"], x["metric"]))):
            current = {key_fn(x): x for x in spec.get(field, [])}
            for old in base_spec.get(field, []):
                key = key_fn(old)
                if key not in current:
                    problems.append(f"{field} {key} removed")
                    continue
                new = current[key]
                old_rule = old.get("threshold", {}) if field == "metrics" else old
                new_rule = new.get("threshold", {}) if field == "metrics" else new
                if old.get("blocking") and not new.get("blocking"):
                    problems.append(f"{field} {key} no longer blocking")
                if old_rule.get("no_significant_drop") and not new_rule.get("no_significant_drop"):
                    problems.append(f"{field} {key} removed no_significant_drop")
                for bound in ("min", "max", "max_increase"):
                    if bound not in old_rule:
                        continue
                    value = new_rule.get(bound)
                    if not isinstance(value, (int, float)) or not math.isfinite(value):
                        problems.append(f"{field} {key} removed {bound}")
                    elif ((bound == "min" and value < old_rule[bound]) or
                          (bound != "min" and value > old_rule[bound])):
                        problems.append(f"{field} {key} loosened {bound}")
    return problems


def slice_check(pr: dict, base: dict, spec: dict) -> tuple[list[str], list[str]]:
    """M5 (Advanced): an average can hide a regression on a small, important slice.
    For each entry of spec["slices"] ({"name", "metric", "min"?, "no_significant_drop"?, "blocking"}):
      - value = mean of per_item(pr, metric, slice_name=name)
      - fail if below "min", or if no_significant_drop and the paired CI over the slice's items
        lies entirely below 0
    Return (blocked ids like "slice:money_movement/pass_rate", report lines)."""
    blocked: list[str] = []
    lines: list[str] = []
    bs = spec.get("bootstrap", {})
    for rule in spec.get("slices", []):
        name, metric = rule["name"], rule["metric"]
        slice_id = f"slice:{name}/{metric}"
        pr_items = per_item(pr, metric, slice_name=name)
        base_items = per_item(base, metric, slice_name=name)
        value = sum(pr_items.values()) / len(pr_items) if pr_items else None
        verdict = "ok"
        notes = []
        if value is None:
            verdict = "missing"
        elif "min" in rule and value < rule["min"]:
            verdict = "fail"
        if rule.get("no_significant_drop"):
            if not pr_items or pr_items.keys() != base_items.keys():
                verdict = "missing"
                notes.append("paired slice items differ")
            else:
                keys = sorted(pr_items)
                delta, lo, hi = stats.paired_bootstrap(
                    [pr_items[k] for k in keys], [base_items[k] for k in keys],
                    n_resamples=bs.get("n_resamples", 1000),
                    rng=bs.get("rng", 2027),
                    confidence=bs.get("confidence", 0.95),
                )
                notes.append(f"Δ {delta:+.3f} CI [{lo:+.3f}, {hi:+.3f}]")
                if hi < 0:
                    verdict = "fail"
        if verdict != "ok" and rule.get("blocking"):
            blocked.append(slice_id)
        label = {"ok": "ok", "missing": "MISSING"}.get(
            verdict, "BLOCK" if rule.get("blocking") else "warn")
        lines.append(f"  {slice_id:<32} {value!s:<8} min={rule.get('min')!s:<5} "
                     f"{' '.join(notes):<28} {label}")
    return blocked, lines


def check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> tuple[list[str], list[str]]:
    pr_manifest, base_manifest = pr.get("manifest"), base.get("manifest")
    if not isinstance(pr_manifest, dict) or not isinstance(base_manifest, dict):
        return ["integrity"], ["  INTEGRITY manifest missing or malformed"]
    pr_sha, base_sha = pr_manifest.get("eval_set_sha"), base_manifest.get("eval_set_sha")
    if not isinstance(pr_sha, str) or not pr_sha or not isinstance(base_sha, str) or not base_sha:
        return ["integrity"], ["  INTEGRITY eval_set_sha missing or malformed"]
    if pr_sha != base_sha:
        return ["eval_set_sha"], ["  EVAL SET differs from the baseline's: re-run the baseline on the same eval set"]
    problems = integrity_check(pr, base, spec, base_spec)
    if problems:
        return ["integrity"], [f"  INTEGRITY {p}" for p in problems]
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for m in spec["metrics"]:
        mid, th, val = m["id"], m.get("threshold", {}), pr["metrics"].get(m["id"])
        verdict, note = "ok", ""
        if val is None:
            verdict = "missing"
        elif "max" in th and val > th["max"]:
            verdict = "fail"
        elif "min" in th and val < th["min"]:
            verdict = "fail"
        elif "max_increase" in th and base["metrics"].get(mid):
            if val > base["metrics"][mid] * (1 + th["max_increase"]):
                verdict = "fail"
        if th.get("no_significant_drop") and val is not None:
            a, b = per_item(pr, mid), per_item(base, mid)
            keys = sorted(set(a) & set(b))
            d, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                                               n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027))
            note = f"Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
            if hi < 0:
                verdict = "fail"
        if verdict != "ok" and m.get("blocking"):
            blocked.append(mid)
        label = {"ok": "ok", "missing": "MISSING"}.get(verdict, "BLOCK" if m.get("blocking") else "warn")
        lines.append(f"  {mid:<22} {val!s:<8} {json.dumps(th):<40} {note:<28} {label}")
    if spec.get("slices"):
        sb, sl = slice_check(pr, base, spec)
        blocked += sb
        lines += sl
    return blocked, lines


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(prog="lab9.gate")
    ap.add_argument("--pr", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--spec", default=str(SPEC))
    ap.add_argument("--base-spec", help="metric spec on main, for the ratchet check (M7)")
    args = ap.parse_args(argv)
    pr = json.loads(Path(args.pr).read_text(encoding="utf-8"))
    base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    base_spec = load_spec(Path(args.base_spec)) if args.base_spec else None
    blocked, lines = check(pr, base, load_spec(Path(args.spec)), base_spec)
    manifest = pr.get("manifest") if isinstance(pr.get("manifest"), dict) else {}
    print(f"gate: PR {pr.get('run_id', '<missing>')} vs main {base.get('run_id', '<missing>')} "
          f"· eval set {manifest.get('eval_set_sha', '<missing>')}")
    print("\n".join(lines))
    if blocked:
        print(f"exit 1 — blocked: {', '.join(blocked)}")
        return 1
    print("exit 0 — merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
