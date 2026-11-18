# Tài liệu và bằng chứng Lab 9

Đọc [README](../README.md), [CHECKPOINTS](../CHECKPOINTS.md), [RUBRIC](../RUBRIC.md) và [SUBMISSION](../SUBMISSION.md) để biết yêu cầu gốc. Các tài liệu dưới đây là phần bài làm của nhánh `starter/d09`.

| Mục | Tài liệu | Bằng chứng có thể chạy lại |
| --- | --- | --- |
| M1 | [Failure taxonomy](failure_taxonomy.md) | `python -m lab9.evalset --check` |
| M2 | [Judge audit](judge_audit.md) | `python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 10` và lệnh `judge_helpful_public.csv` trong tài liệu |
| M3 | [Trace case](trace_case.md), [eval card](eval_card.md) | `python -m pytest -q -m student -o addopts= -k "lab9 and not advanced"` |
| M4 | [Eval card](eval_card.md), [PRD v1.1](PRD_v1.1.md) | [Baseline v1](../src/reports/baseline_v1.json), [fixed](../src/reports/eval_fixed.json), [seeded regression](../src/reports/eval_seeded_regression.json) |
| M5–M7 | [Eval card, mục v2](eval_card.md) | [Baseline v2](../src/reports/baseline_v2.json), [hướng dẫn report](../src/reports/README.md), `python -m lab9.mutation --spec config/metric_spec_v2.yaml --baseline reports/baseline_v2.json`, `python -m lab9.traps --pr reports/eval_slice_regression.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml` |

[Bằng chứng để điền mô tả PR](pr_evidence.md) gồm output gate, A/A, scorecard và bốn trap theo `SUBMISSION.md`.

Các lệnh Python chạy từ `src/` sau khi cài `requirements.txt` và `requirements-lab9.txt`. Report JSON trong bảng được sinh bằng `lab9.eval`; không sửa tay. CI của [PR #1](https://github.com/lunaHieu/K5-L3B-DAY09-NguyenVanHieu-2A202603746-EvaluationandFailureAnalysis/pull/1) đã chạy xanh ở commit `2200c53` (Core và v2). Việc review/merge là bước nộp bài còn lại theo [SUBMISSION](../SUBMISSION.md).

`src/README.md` là hướng dẫn Day8 được chép cùng `src/`; các tài liệu nghiệp vụ và contract Day8 nằm trong [repo Day8 gốc](https://github.com/VinUni-AI20k/K5-Day8-From-Workflows-to-Agents/tree/main/docs). Bài Day9 giữ nguyên `src/lab8/` theo đề.
