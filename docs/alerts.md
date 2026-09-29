# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: High end-to-end latency
- Severity: warning
- Duration: 10 phút
- Kênh thông báo: Slack `#llm-platform-alerts`
- SLI/SLO liên quan: fast_successful_requests; P95 phải không vượt 3.000 ms.
- Điều kiện và thời gian duy trì: P95 của `response_sent.latency_ms` > 3.000 ms trong 10 phút.
- Ảnh hưởng tới người dùng: phản hồi chậm, dễ timeout hoặc bị bỏ dở.
- Ba bước kiểm tra đầu tiên: (1) xem panel latency/TTFT theo feature; (2) lọc `response_sent` chậm và lấy `correlation_id`; (3) mở trace cùng ID, so sánh retrieval với generation.
- Mitigation tạm thời: giảm concurrency hoặc route sang fallback nhanh; nếu retrieval là nút thắt thì dùng cached/general fallback.
- Owner: `llm-platform-oncall`

## Alert 2

- Tên: Elevated request failure rate
- Severity: critical
- Duration: 5 phút
- Kênh thông báo: Slack `#llm-platform-alerts`
- SLI/SLO liên quan: error rate guardrail ≤ 2%.
- Điều kiện và thời gian duy trì: `request_failed / request_received * 100` > 2% trong 5 phút.
- Ảnh hưởng tới người dùng: request không nhận được câu trả lời thành công.
- Ba bước kiểm tra đầu tiên: (1) xem breakdown `error_type` và retrieval success; (2) lấy correlation ID của request lỗi; (3) mở trace cùng ID và xác định observation lỗi.
- Mitigation tạm thời: bật fallback retrieval, giảm traffic tới dependency lỗi hoặc rollback thay đổi prompt/model gần nhất.
- Owner: `llm-platform-oncall`

## Alert 3

- Tên: Quality proxy degradation
- Severity: warning
- Duration: 15 phút
- Kênh thông báo: Slack `#llm-quality-alerts`
- SLI/SLO liên quan: mean quality proxy ≥ 0,75.
- Điều kiện và thời gian duy trì: trung bình `response_sent.quality_score` < 0,75 trong 15 phút.
- Ảnh hưởng tới người dùng: câu trả lời có thể thiếu ngữ cảnh hoặc không hữu ích dù request thành công.
- Ba bước kiểm tra đầu tiên: (1) so sánh quality theo feature và prompt label/version; (2) lấy correlation ID có score thấp; (3) kiểm tra trace retrieval documents, generation tokens và prompt metadata.
- Mitigation tạm thời: rollback label `production` về prompt đã xác minh, sau đó kiểm tra corpus/retrieval coverage.
- Owner: `llm-quality-owner`
