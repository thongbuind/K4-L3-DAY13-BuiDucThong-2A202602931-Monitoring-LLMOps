# Báo cáo cá nhân — K4-L3A Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Bùi Đức Thông
- **MSSV:** 2A202602931
- **Lớp:** K4-L3A
- **Repository URL:** `git@github.com:thongbuind/K4-L3-DAY13-BuiDucThong-2A202602931-Monitoring-LLMOps.git`
- **Commit SHA cuối:**
- **Challenge ID:**
- **Tên project Langfuse cá nhân:** `day13-k4-l3a-2A202602931` (cần tự tạo trên Langfuse Cloud)

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.txt` |
| Log validator | `evidence/02-log-validator.txt` |
| Dashboard validator | `evidence/03-dashboard-validator.txt` |
| Structured log | `evidence/04-structured-log.txt` |
| PII redaction | `evidence/05-pii-redaction.txt` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.html` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | Chưa lưu baseline | 100/100 | 11 correlation IDs, 0 PII leaks |
| `validate_dashboard.py` | Chưa lưu baseline | 6/6 panel | Contract hợp lệ |
| `pytest` | Chưa lưu baseline | 22 passed | Chạy bằng Python 3.13 virtual environment |
| Số traces hợp lệ | 0 | Cần cấu hình Langfuse cá nhân | Không khai báo trace giả khi chưa có key/project |
| Số PII leak | Chưa đo baseline | 0 | Đã chạy request PII giả và validator |
| Latency P95 / TTFT P95 | Chưa đo baseline | 173 ms / 70 ms | Workload local 11 request |
| Retrieval success rate | Chưa đo baseline | 100% | Workload local 11 request |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Middleware xóa context cũ, dùng `x-request-id` nếu có hoặc sinh `req-<8-hex>`, bind vào `structlog`, trả qua `x-request-id` và lưu ở `request.state` để agent/traces dùng cùng ID.
- **Các metadata được ghi vào structured log:** `user_id_hash`, `session_id`, `feature`, `model`, `env`, cùng latency, TTFT, token, cost, quality và retrieval outcome ở event phù hợp.
- **Cách bảo đảm PII được scrub trước khi ghi:** Processor `scrub_event` duyệt đệ quy string/dict/list và chạy trước cả JSON renderer lẫn JSONL file writer. Raw user ID không được bind; chỉ SHA-256 hash rút gọn được log.
- **Cách kiểm chứng kết quả:** Xem `evidence/04-structured-log.txt`, `evidence/05-pii-redaction.txt` và `evidence/02-log-validator.txt`.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Cần thực hiện trong project `day13-k4-l3a-2A202602931` sau khi cấu hình key riêng; chụp trace list có ít nhất 10 trace. Hiện không có key/project nên không ghi trace ID giả.
- **Cấu trúc root/retrieval/generation observations:** `LabAgent.run` là root agent; code tạo child `retrieval` (`retriever`) và `llm-generation` (`generation`). Generation có model, sanitized prompt/input-output, usage tokens, cost và TTFT metadata.
- **Cách nối trace với log:** Cùng `correlation_id` được bind bởi middleware được đưa vào trace metadata và có trong `request_received`/`response_sent` log.
- **Prompt name:** `day13-chat` (cần tạo trong project Langfuse cá nhân).
- **Version/label baseline:** Cần tạo v1 với label `baseline` và `production` theo `docs/PROMPT_VERSIONING.md`.
- **Version/label candidate:** Cần tạo v2 với label `candidate` theo `docs/PROMPT_VERSIONING.md`.
- **Trace ID của mỗi version:** Chưa có — cần ghi ID thật sau khi chạy workload với hai label.
- **Cách promote và rollback `production`:** Chuyển `production` v1 → v2, restart API và chạy request; sau đó chuyển v2 → v1, restart API và chạy lại. Lưu ảnh/trace ID ở `evidence/09-prompt-versions.png` và `evidence/10-prompt-rollback.png`.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** `scripts/render_dashboard.py` đọc `data/logs.jsonl` và render sáu panel latency/TTFT, traffic, errors/retrieval, cost, tokens, quality. Runtime artifact: `evidence/11-dashboard-overview.html`.
- **SLO và lý do chọn:** `config/slo.yaml` đặt SLO successful responses dưới 3.000 ms là 99,5% trong 28 ngày; threshold này khớp panel latency và alert về trải nghiệm người dùng.
- **Cách tính error budget:** 0,5% tổng request trong cửa sổ 28 ngày, tương đương 50 bad events trên 10.000 request.
- **Ba alert và runbook tương ứng:** `config/alert_rules.yaml` và `docs/alerts.md` định nghĩa latency P95, error rate, quality proxy; cả ba có severity, duration, Slack channel, owner, condition và mitigation.

## 7. Điều tra challenge

- **Challenge ID:** Chưa có — chỉ Lab Coach được cấp `config/challenge.json` cho lớp K4-L3A.
- **Khoảng thời gian điều tra:** Chưa chạy challenge chính thức.
- **Triệu chứng từ metrics:** Chưa chạy challenge chính thức.
- **Log line và correlation ID liên quan:** Chưa chạy challenge chính thức.
- **Trace ID và span gây ảnh hưởng:** Chưa chạy challenge chính thức.
- **Root cause:** Chưa kết luận khi chưa có đủ metric → log → trace của challenge.
- **Fix action:** Sau khi challenge được cấp, xác minh span gây lỗi/chậm trước khi chọn mitigation theo runbook.
- **Preventive measure:** Sau khi xác định root cause, bổ sung guardrail/alert hoặc fallback tương ứng và chạy lại cùng workload để xác minh.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Scrub PII ở structlog processor trước cả file writer và JSON renderer để mọi sink nhận cùng dữ liệu đã redacted, thay vì trông chờ từng nơi log tự sanitize.
- **Một lỗi/blocker đã gặp:** Python 3.14 trên máy không tạo được environment do lỗi truststore; chuyển sang Python 3.13 và virtual environment riêng, sau đó cài dependencies khóa phiên bản thành công.
- **Cách tìm nguyên nhân và xử lý:** Đọc traceback của `ensurepip`, xác nhận Python 3.13 có sẵn, tạo lại environment rồi chạy toàn bộ test/validator trên environment đó.
- **Cách hiểu luồng Metrics → Logs → Traces:** Metrics/dashboards phát hiện triệu chứng và time window; logs thu hẹp request qua correlation ID; trace cùng ID phân rã thời gian/lỗi thành retrieval và generation để kết luận root cause.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** Prompt label cho phép deploy/rollback version không đổi source; token/cost phát hiện tăng chi phí bất thường; SLO biến trải nghiệm latency/success thành error budget và trigger alert có hành động cụ thể.
- **Điều quan trọng nhất đã học:** Một dashboard pass validator chưa đủ; kết luận incident phải nối một metric, log cùng correlation ID và trace có span cụ thể.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** Chưa có Langfuse project/key cá nhân và `config/challenge.json` do Lab Coach release, nên chưa thể tạo evidence trace/prompt/official incident hợp lệ.

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối — cập nhật SHA sau khi commit.
- [x] Tất cả artifact hiện có dùng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace — chờ challenge chính thức.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret — chờ project/key riêng.
- [x] Repository chạy lại được theo README; 22 tests pass, log validator 100/100 và dashboard validator 6/6.
- [x] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác trong artifact mới.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
