# Phần mềm Kiểm toán

Phần mềm hỗ trợ quản lý và thực hiện quy trình kiểm toán.

## Cài đặt

```bash
# Clone repository
git clone https://github.com/your-username/audit-software.git

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

## Cấu trúc dự án

```plaintext
src/
├── modules/
│   ├── job/
│   └── utils/
├── views/
└── models/
```

## Phiên bản

- v1.0.0: Tính năng cơ bản (tạo/mở job)
- v1.1.0: Thêm giao diện người dùng 