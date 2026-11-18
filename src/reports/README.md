# Report đánh giá Lab 9

Chạy các lệnh từ `src/`. Mỗi file JSON dưới đây do `python -m lab9.eval` sinh ra; không sửa tay. `src/reports/` nằm trong `.gitignore`, nên cần `git add -f` khi commit bằng chứng.

| File đã commit | Eval set | Shape | Mục đích |
| --- | --- | --- | --- |
| [baseline_v1.json](baseline_v1.json) | v1 | `swarm` | Baseline Core, 14 item × 5 seed |
| [eval_fixed.json](eval_fixed.json) | v1 | `fixed` | Gate cho qua |
| [eval_seeded_regression.json](eval_seeded_regression.json) | v1 | `seeded_regression` | Gate chặn `pass_rate` |
| [baseline_v2.json](baseline_v2.json) | v2 | `swarm` | Baseline Advanced/Expert, 28 item × 5 seed |
| [eval_fixed_v2.json](eval_fixed_v2.json) | v2 | `fixed` | Gate cho qua |
| [eval_honest_refactor.json](eval_honest_refactor.json) | v2 | `honest_refactor` | Kiểm tra không báo nhầm |
| [eval_slice_regression.json](eval_slice_regression.json) | v2 | `slice_regression` | Gate chặn slice `money_movement` |
| [eval_flaky_regression.json](eval_flaky_regression.json) | v2 | `flaky_regression` | Gate chặn `pass_hat_5` |

Sinh lại một report bằng `python -m lab9.eval --shape <shape> --spec config/metric_spec.yaml --out reports/<file>.json`; thay spec bằng `config/metric_spec_v2.yaml` cho v2. Chi tiết số liệu, CI và giới hạn quan sát nằm trong [eval card](../../docs/eval_card.md). Hai eval set được ghim CRLF trong [`.gitattributes`](../../.gitattributes) để SHA của baseline trùng trên Windows và CI Ubuntu.

`eval_pr.json` là report tạm của CI. `reports/traps/` do `lab9.traps` tạo để thử gate; các file này không phải baseline. Hướng dẫn `benchmark.json` và `crash.json` trong Day8 áp dụng cho bài Day8, không phải bằng chứng Lab9.
