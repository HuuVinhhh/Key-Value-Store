# gRPC Key-Value Store

## Mô tả
Dự án này là một ứng dụng Key-Value Store phân tán sử dụng gRPC và Flask. Người dùng có thể thực hiện các thao tác như PUT, GET, DELETE và UPDATE trên dữ liệu key-value thông qua API.

## Các bước cài đặt và chạy dự án

###  Cài đặt Python

Đảm bảo bạn đã cài đặt Python 3.6 hoặc phiên bản cao hơn. Bạn có thể tải Python tại [python.org](https://www.python.org/downloads/).

###  Clone repository
git clone https://github.com/HuuVinhhh/Key-Value-Store.git

###  Tạo và kích hoạt môi trường ảo

1. Mở terminal hoặc command prompt và điều hướng tới thư mục chứa dự án.
2. Tạo môi trường ảo bằng lệnh sau:

   - **Windows**:
     ```bash
     python -m venv venv
     ```
   - **MacOS/Linux**:
     ```bash
     python3 -m venv venv
     ```

3. Kích hoạt môi trường ảo:

   - **Windows**:
     ```bash
     .\venv\Scripts\activate
     ```
   - **MacOS/Linux**:
     ```bash
     source venv/bin/activate
     ```
4. Kiểm tra Python đang dùng môi trường nào:
   - **Windows**:
     ```bash
     where python 
     ```
   - **MacOS/Linux**:
     ```bash
     which python
     ```

### Cài đặt các thư viện cần thiết
Sau khi kích hoạt môi trường ảo, cài đặt các thư viện yêu cầu trong tệp `requirements.txt` bằng lệnh sau:

```bash
pip install -r requirements.txt
```

### Thực hiện
Tại thời điểm này, bạn đã cài đặt tất cả các phụ thuộc, hãy thực hiện dự án của chúng tôi.

step 1: Server hosting.
    - Trong dự án này, chúng tôi đã mô phỏng một hệ thống mini, chỉ có 3 nút chạy trên 3 cổng khác nhau (`port [50051, 50052, 50053]`).
    - Bạn cần mở 3 cửa sổ đầu cuối tương ứng với mỗi máy chủ và chạy lệnh sau trong cả 3 cửa sổ.

```shell
python server.py [port]
```
Trong mỗi cửa sổ, nhập cổng tương ứng: `[50051, 50052, 50053] tương ứng.

Step 2: Client serving.

- Để thử nghiệm các chức năng , hãy chạy ứng dụng của máy khách bằng lệnh này

```shell
python application/app.py
```





