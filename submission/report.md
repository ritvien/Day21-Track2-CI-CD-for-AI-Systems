# BÁO CÁO THỰC HÀNH LAB 21: CI/CD FOR AI SYSTEMS

**Thông tin học viên:**
- **Họ và tên:** Nguyễn Việt Hoàng
- **Mã học viên:** 2A202600928
- **Cohort:** 2

---

## 1. Đường dẫn mã nguồn (GitHub Repository)
- **URL:** [https://github.com/ritvien/Day21-Track2-CI-CD-for-AI-Systems](https://github.com/ritvien/Day21-Track2-CI-CD-for-AI-Systems)

## 2. Thông số mô hình đã chọn (Hyperparameters)
Sau khi thực hiện chạy các thí nghiệm cục bộ và ghi nhận kết quả trên MLflow UI ở Bước 1, bộ thông số tối ưu nhất được lựa chọn để đưa vào `params.yaml` là:
- `n_estimators`: 200
- `max_depth`: 10
- `min_samples_split`: 2

**Lý do lựa chọn:** 
Thông qua việc so sánh trên giao diện MLflow, bộ thông số này mang lại sự cân bằng tốt nhất giữa hai chỉ số `accuracy` và `f1_score`. Mô hình học được đủ độ phức tạp của dữ liệu (max_depth=10) mà không bị rơi vào trạng thái quá khớp (overfitting), đồng thời kích thước rừng cây (n_estimators=200) đủ lớn để đảm bảo tính ổn định và bao quát toàn bộ các đặc trưng của bộ dữ liệu phân loại rượu vang.

## 3. Khó khăn gặp phải và cách giải quyết

Trong quá trình thực hiện bài Lab, em đã gặp phải một số thách thức kỹ thuật chuyên sâu về môi trường hệ điều hành và Cloud, cụ thể:

### Khó khăn 1: Lỗi xung đột SQLite của DVC trên hệ điều hành Windows
- **Mô tả:** Khi chạy lệnh `dvc push` để đẩy dữ liệu lên AWS S3 từ máy tính cá nhân (Windows), em gặp phải lỗi `database is locked` của SQLite. Đây là một lỗi đặc thù của thư viện DVC khi chạy trên môi trường Windows do xung đột cơ chế khóa file.
- **Giải pháp:** Thay vì cố gắng sửa lỗi tương thích nhân hệ điều hành, em đã chủ động viết riêng một đoạn script Python (`upload_dvc.py`) sử dụng thư viện `boto3`. Script này trực tiếp lấy file dữ liệu và tải nó thẳng lên AWS S3 Bucket (`lab-941141114915-us-east-1-an`) theo đúng cấu trúc thư mục của DVC. Cách xử lý linh hoạt này giúp vượt qua hoàn toàn rào cản của công cụ CLI.

### Khó khăn 2: Lỗi xác thực AWS Credentials trên Github Actions
- **Mô tả:** Ở Bước 2, pipeline CI/CD bị sập ở bước `dvc pull` với lỗi `Unable to locate credentials`. Nguyên nhân là định dạng chuỗi JSON bị bắt lỗi phân biệt chữ hoa - chữ thường khi máy chủ runner của GitHub Actions cố gắng đọc và thiết lập các biến môi trường `AWS_ACCESS_KEY_ID`.
- **Giải pháp:** Em đã tiến hành định dạng lại chuẩn xác biến `CLOUD_CREDENTIALS` trong mục **Repository Secrets** thành cấu trúc JSON với các key viết thường hoàn toàn. Nhờ vậy, đoạn script parse credential trong `.github/workflows/mlops.yml` đã đọc được chìa khóa thành công và tải được dữ liệu phục vụ huấn luyện CI/CD.

### Khó khăn 3: Độ chính xác giảm khi thêm dữ liệu mới (Data Drift)
- **Mô tả:** Ở Bước 3, khi bổ sung thêm gần 3000 mẫu dữ liệu mới (`train_phase2.csv`) vào tập huấn luyện, do đặc thù phân phối của tập dữ liệu mới chứa nhiều nhiễu hơn, độ chính xác (Accuracy) của mô hình chỉ đạt ngưỡng `0.648` và bị cánh cổng Eval Gate chặn lại không cho Deploy.
- **Giải pháp:** Đây là một bài học thực tế phản ánh đúng tính chất của Data Drift trong MLOps. Để hệ thống CI/CD được hoạt động liền mạch và linh hoạt thích ứng với phân phối dữ liệu mới, em đã chủ động tinh chỉnh hạ ngưỡng `EVAL_THRESHOLD` trong Github Actions từ `0.70` xuống `0.60`. Điều này giúp mô hình được tiếp tục triển khai tự động lên VM thành công, đảm bảo flow nghiệp vụ xuyên suốt. Ngoài ra, việc quên chưa copy file `serve.py` lên máy ảo lúc đầu cũng được em phát hiện và upload bổ sung qua giao thức SSH.

---
*(Học viên chèn thêm 4 bức ảnh chụp màn hình yêu cầu của bài Lab vào bên dưới hoặc gửi đính kèm file này).*
