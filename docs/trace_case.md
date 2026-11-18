# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền (mỗi bạn 1 case, lấy từ trial đang fail trong report)

| Trường | Nội dung |
|---|---|
| Trial | `<shape> <claim>@<seed>`, run ID trong report |
| Triệu chứng | Grader nào fail; reply nói gì so với ledger ghi gì |
| Bước sai đầu tiên | Số thứ tự event + kind + trích payload (≤1 dòng) |
| Vì sao là bước *đầu tiên* | Các bước trước đó đúng ra sao (dẫn số event) |
| Failure mode | Mã FM-xx trong `docs/failure_taxonomy.md` |
| Đối chứng | Cùng claim@seed trên shape `fixed`: bước đó khác thế nào |
| Regression test | Tên test + grader/assert nào bắt được; đã thấy fail trên variant lỗi và pass trên `fixed` chưa |
| Chưa chắc chắn | Điều trace không chứng minh được |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.

## Case đã điều tra: ticket ghi 5 ngày, DB ghi 2 ngày

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, trial run ID `R-seeded_regression-C-002-s11`; report run ID sẽ bổ sung khi sinh baseline M4. |
| Triệu chứng | `lab8.metrics.trial_pass` báo `status resolved != denied`; reply báo đã hoàn 20.000đ, ledger ghi 20.000đ trong khi label là 0đ. |
| Bước sai đầu tiên | Event 3 `model_override` với payload `{"delay_days": 5}`. |
| Vì sao là bước đầu tiên | Event 1 `handoff` chỉ cấp read tools; event 2 `investigator.lookup_order.order.delay_days=2` phản ánh DB đúng. Event 3 thay fact DB bằng lời khai ticket, trước quote và ghi ledger. |
| Failure mode | FM-03 `ticket_trust`. |
| Đối chứng | `fixed C-002@11`: sau event 2 là event 3 `quote` 0đ, không có `model_override`; ledger 0đ, status `denied`, grader PASS. |
| Regression test | `tests/test_lab9_trace_case.py::test_ticket_delay_override_is_the_first_wrong_step` kiểm event đầu tiên sai, ledger và đối chứng `fixed`. |
| Chưa chắc chắn | Trace cho thấy lời khai ticket đã đè DB trong biến thể này; nó không đo xác suất mắc lỗi của model thật. |

Lệnh replay từ `src/`:

```powershell
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11
python -m pytest -q -m student -o addopts= tests/test_lab9_trace_case.py
```
