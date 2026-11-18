# Bằng chứng để điền mô tả PR #1

Các lệnh chạy từ `src/` trên commit `2200c53` (Python 3.13.2, MockLLM). Đây là output thực; report JSON được sinh bằng harness và đã commit. [PR #1](https://github.com/lunaHieu/K5-L3B-DAY09-NguyenVanHieu-2A202603746-EvaluationandFailureAnalysis/pull/1) hiện có mô tả trống. Theo [SUBMISSION](../SUBMISSION.md), dán các phần dưới vào mô tả PR trước khi merge.

## Core: gate chặn seeded regression

Lệnh:

```text
python -m lab9.gate --pr reports/eval_seeded_regression.json --baseline reports/baseline_v1.json --spec config/metric_spec.yaml
```

Output:

```text
gate: PR E-seeded_regression-20261118-2078 vs main E-swarm-20261118-2078 · eval set 2078e126aede
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9286   {"min": 0.95}                                                         warn
  refund_amount_correct  0.8571   {"min": 0.95, "no_significant_drop": true} Δ -0.129 CI [-0.315, +0.000] BLOCK
  proposal_amount_correct 0.7857   {"min": 0.95, "no_significant_drop": true} Δ -0.200 CI [-0.414, +0.000] BLOCK
  reply_ledger_match     0.7857   {"min": 0.95, "no_significant_drop": true} Δ -0.214 CI [-0.429, +0.000] BLOCK
  pass_rate              0.7143   {"min": 0.85, "no_significant_drop": true} Δ -0.271 CI [-0.500, -0.057] BLOCK
  pass_5                 0.7143   {"min": 0.8}                                                          warn
  cost_per_success       81.202   {"max_increase": 0.1}                                                 warn
exit 1 — blocked: refund_amount_correct, proposal_amount_correct, reply_ledger_match, pass_rate
```

## M6: A/A trên hai bộ seed

Lệnh: `python -m lab9.mutation --spec config/metric_spec_v2.yaml --aa 66,77,88,99,110`

```text
metric                 spec seeds  alt seeds    delta
approval_bypass                 0          0  +0.0000
secret_leak                     0          0  +0.0000
db_fact_kept               0.9786     0.9786  +0.0000
refund_amount_correct      0.9786     0.9786  +0.0000
pass_rate                  0.9786     0.9786  +0.0000
reply_ledger_match            1.0        1.0  +0.0000
pass_5                     0.8929     0.8929  +0.0000
pass_at_1                  0.9786     0.9786  +0.0000
pass_hat_1                 0.9786     0.9786  +0.0000
pass_at_3                     1.0        1.0  +0.0000
pass_hat_3                 0.9357     0.9357  +0.0000
pass_at_5                     1.0        1.0  +0.0000
pass_hat_5                 0.8929     0.8929  +0.0000
cost_per_success          50.8077    50.8077  +0.0000
```

## M5–M7: mutation scorecard

Lệnh: `python -m lab9.mutation --spec config/metric_spec_v2.yaml --baseline reports/baseline_v2.json`

```text
  fixed                expect merge got merge ok
  honest_refactor      expect merge got merge ok
  seeded_regression    expect block got block ok          refund_amount_correct, pass_rate, pass_hat_5, reply_ledger_match, slice:money_movement/pass_rate, slice:adversarial/pass_rate, slice:denial/pass_rate
  slice_regression     expect block got block ok          slice:money_movement/pass_rate
  flaky_regression     expect block got block ok          pass_rate, pass_hat_5, slice:money_movement/pass_rate
mutation score 3/3 — false alarms 0
```

## M7: bốn trap

`python -m lab9.traps --pr reports/eval_slice_regression.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml` sinh trap và chạy gate. Chạy riêng từng lệnh gate cho cùng kết quả:

```text
evaluator_errors_as_nan => exit 1 — blocked: integrity
dropped_failing_rows    => exit 1 — blocked: integrity
cherry_picked_seeds     => exit 1 — blocked: integrity
loosened_spec           => exit 1 — blocked: integrity
```

Trap `loosened_spec` dùng thêm `--base-spec config/metric_spec_v2.yaml` để kiểm ratchet. CI [run 44241786320](https://github.com/lunaHieu/K5-L3B-DAY09-NguyenVanHieu-2A202603746-EvaluationandFailureAnalysis/actions/runs/44241786320) hoàn tất thành công cả `detect`, `eval-gate` và `eval-gate-v2`.
