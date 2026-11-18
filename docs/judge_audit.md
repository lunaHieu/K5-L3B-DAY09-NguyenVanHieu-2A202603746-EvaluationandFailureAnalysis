# Judge audit — replay CSV công khai

Chạy từ `src/`:

```powershell
python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 10
python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5
```

FAIL là lớp dương: precision = lỗi judge báo đúng / mọi lỗi judge báo; recall = lỗi judge tìm thấy / mọi lỗi người gắn nhãn. FLOORS: κ≥0.6, P≥0.8, R≥0.7.

| Tiêu chí | n | TP / FP / FN / TN | κ | Precision | Recall | Fail rate quan sát → Rogan–Gladen | Quyết định |
|---|---:|---|---:|---:|---:|---|---|
| tone_ok | 100 | 24 / 4 / 6 / 66 | 0.757 | 0.857 | 0.800 | 0.28 → 0.30 | Đạt floors; có thể dùng cho tone sau audit và kiểm tra nhãn mới. |
| helpful | 100 | 9 / 0 / 21 / 70 | 0.375 | 1.000 | 0.300 | 0.09 → 0.30 | Không đạt κ và recall; loại khỏi release gate. |

## Audit bất đồng

Các kết luận dưới đây dựa trên `reply`, cột `note` và `human_failure` của CSV. Riêng việc tiền trong reply khớp ledger dựa trên số ledger nêu trong `note`; muốn kiểm chứng độc lập cần ledger gốc.

| # | Case | Judge / người | Ai đúng? | Sửa rubric, nhãn hoặc grader |
|---:|---|---|---|---|
| 1 | H-008 | PASS / FAIL | Người: “em”, “nha” quá suồng sã. | Nêu rõ cách xưng hô được phép trong khiếu nại; ví dụ “em/nha” là tone FAIL. |
| 2 | H-017 | PASS / FAIL | Người: “bạn ơi”, “nha” không phù hợp khách lớn tuổi. | Thêm ví dụ tone theo ngữ cảnh khách; không chỉ nhận diện câu lịch sự bề mặt. |
| 3 | H-029 | PASS / FAIL | Người: “không cần nhắn thêm” mang giọng ra lệnh. | Chấm toàn câu, thêm quy tắc cấm đuổi khách dù mở đầu bằng “Dạ”. |
| 4 | H-042 | FAIL / PASS | Người: câu ngắn nhưng đủ thông tin và lịch sự. | Không bắt buộc lời xin lỗi khi đã xác nhận refund rõ ràng. |
| 5 | H-051 | FAIL / PASS | Người: “refund” được CS LogiX chấp nhận. | Ghi thuật ngữ Anh Việt được phép; không phạt riêng từ “refund”. |
| 6 | H-063 | PASS / FAIL | Người: hứa hoàn thêm ngoài kết quả hệ thống. | Đánh dấu lời hứa ngoài ledger là FAIL; đối chiếu bằng code khi có số tiền. |
| 7 | H-070 | PASS / FAIL | Người: emoji cười không phù hợp khiếu nại. | Bổ sung ví dụ emoji bị cấm cho ngữ cảnh này. |
| 8 | H-081 | FAIL / PASS | Judge theo ghi chú CSV: nhãn người đọc nhầm ticket. | Kiểm tra lại claim và sửa nhãn người trước lần calibration tiếp theo. |
| 9 | H-088 | FAIL / PASS | Người: lặp “Dạ” do lỗi gõ nhẹ, không làm câu thiếu tôn trọng. | Cho phép lỗi gõ nhỏ không đổi nghĩa; thêm ca biên. |
| 10 | H-094 | PASS / FAIL | Người: câu mất dấu toàn bộ, không đạt chất lượng tiếng Việt. | Thêm ví dụ câu dịch máy/mất dấu; phân biệt một lỗi gõ với cả câu không dấu. |
| 11 | HL-015 | PASS / FAIL | Người: reply 55.000đ, `note` ghi ledger 40.000đ. | Helpful cần tính chính xác tiền; dùng code so reply với ledger, không dựa vào giọng văn. |
| 12 | HL-016 | PASS / FAIL | Người: reply dài và lịch sự nhưng 55.000đ ≠ ledger 35.000đ. | Không cho lời xin lỗi che lỗi tiền; đặt money check trước judge. |
| 13 | HL-020 | PASS / FAIL | Người: reply 90.000đ ≠ ledger 120.000đ. | Thêm negative example với số tiền thấp hơn ledger. |
| 14 | HL-047 | PASS / FAIL | Người: “Ok bạn” sai xưng hô. | Helpful phải bao gồm cách xưng hô theo tone rubric. |
| 15 | HL-100 | PASS / FAIL | Người: reply 55.000đ ≠ ledger 35.000đ. | Bổ sung ca câu ngắn, số tiền sai; tách grader số tiền bằng code. |

## Kết luận

Judge `helpful` bỏ sót 21/30 failure (FN=21), nên recall 0.300 và κ 0.375 đều dưới sàn. Precision 1.000 không bù được lỗi bỏ sót; không dùng tiêu chí này để chặn hay cho qua release. Judge `tone_ok` vượt ba sàn nhưng vẫn có 10 bất đồng, gồm một nhãn người cần sửa (H-081). Tiền và approval phải được chấm bằng code. Cả hai judge mới được kiểm trên dữ liệu replay công khai; trước khi dùng cho dữ liệu thật cần nhãn người độc lập và tập held-out mới.
