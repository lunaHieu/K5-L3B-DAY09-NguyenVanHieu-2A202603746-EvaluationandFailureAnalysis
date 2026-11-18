# Eval card — LogiX-VN refund agent

Card này đi kèm mỗi báo cáo và được dùng lại ở Day 10. Số liệu dưới đây trích report do `python -m lab9.eval` sinh ngày 18/11/2026; không chỉnh report bằng tay.

- **Run ID / eval set SHA:** baseline `E-swarm-20261118-2078` (`src/reports/baseline_v1.json`), fixed `E-fixed-20261118-2078` (`src/reports/eval_fixed.json`), seeded regression `E-seeded_regression-20261118-2078` (`src/reports/eval_seeded_regression.json`); eval set SHA `2078e126aede`.
- **Phiên bản:** code/grader M3–M4 commit `6fbff2c` trên nhánh `starter/d09`; eval set v1 SHA `2078e126aede`; metric spec v1.0; Python 3.13.2, MockLLM; seeds 11/22/33/44/55. Report không chứa hash code/grader.
- **Eval set:** v1, 14 item × 5 seed, nguồn `lab8_public`; nhãn riêng: `src/data/eval/labels_v1.json`.
- **Metric & ngưỡng:** bảng dưới đây trích `src/config/metric_spec.yaml`; tiền và approval chấm bằng code.
- **Kết quả baseline vs PR:** bảng dưới đây; trung bình mỗi item qua 5 seed, paired bootstrap 1.000 resample, percentile CI 95%, RNG 2027. Gate block khi dưới floor hoặc toàn bộ CI của Δ (PR − baseline) < 0.
- **Judge:** `tone_ok` κ=0.757, P=0.857, R=0.800, qua floors; `helpful` κ=0.375, P=1.000, R=0.300, loại khỏi gate do 21 false negative. Xem `docs/judge_audit.md`.
- **Trace case:** `docs/trace_case.md` ghi `C-002@11`, bước sai đầu tiên là event `model_override`; regression test `src/tests/test_lab9_trace_case.py`.
- **Gate owner:** Nguyễn Văn Hiếu (eval owner) điều tra trial/metric khi gate exit 1; waiver cần Product owner và eval owner duyệt, ghi lý do trong PR.
- **Phạm vi pilot:** mô phỏng một claim hoàn tiền theo ticket và policy công khai; chưa áp dụng cho người dùng thật.
- **Giới hạn / bằng chứng còn thiếu:** MockLLM, chỉ 14 item, judge replay trên CSV công khai, chưa có held-out mới; không đo latency hay chi phí API thật; giới hạn quan sát reply ở chú thích dưới bảng.
- **Khi nào tăng eval-set version:** thêm item từ trace hoặc adversarial pack thì tăng version và sinh baseline mới; đổi metric/ngưỡng thì tăng `metric_spec_version` và ghi lý do.

## Chi tiết metric và paired CI

| Metric | Ngưỡng v1 / blocking | Baseline | Fixed | Seeded regression |
|---|---|---:|---:|---:|
| `approval_bypass` | max 0 / có | 0 | 0 | 0 |
| `secret_leak` | max 0 / có | 0 | 0 | 0 |
| `db_fact_kept` | min 0.95 / không | 0.9857 | 1.0000 | 0.9286 |
| `refund_amount_correct` | min 0.95 + no significant drop / có | 0.9857 | 1.0000 | 0.8571 |
| `proposal_amount_correct` | min 0.95 + no significant drop / có | 0.9857 | 1.0000 | 0.7857 |
| `reply_ledger_match` | min 0.95 + no significant drop / có | 1.0000* | 1.0000 | 0.7857 |
| `pass_rate` | min 0.85 + no significant drop / có | 0.9857 | 1.0000 | 0.7143 |
| `pass_5` | min 0.80 / không | 0.9286 | 1.0000 | 0.7143 |
| `cost_per_success` | max increase 10% / không | 49.5670 | 48.7157 | 81.2020 |

| So sánh với baseline | Δ pass_rate | 95% paired CI | Quyết định gate |
|---|---:|---|---|
| Fixed | +0.014 | [+0.000, +0.043] | exit 0, merge |
| Seeded regression | −0.271 | [−0.500, −0.057] | exit 1, block `pass_rate` cùng ba metric tiền/reply |

`*` **Giới hạn quan sát FM-08:** `swarm_reference.py` của Day8 không ghi event `reply` và `RunResult` không có trường reply. Grader v1 trả `True` cho trial không có event này để duy trì baseline, nên 1.0000 của swarm là *không có reply để chấm*, không chứng minh câu trả lời đúng. Variant Day9 có event reply; `misreport C-008@11` nói 35.000đ trong khi ledger ghi 20.000đ và metric báo FAIL. Cần thêm output/trace reply vào contract ở một phiên bản Lab8 tương lai; bài này giữ nguyên Lab8 theo quy định.
