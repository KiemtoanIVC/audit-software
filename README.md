# Audit Software

Phần mềm hỗ trợ kiểm toán với các tính năng:
- Quản lý Job kiểm toán
- Tính toán mức trọng yếu (MTY)
- Xử lý báo cáo tài chính
- Các tiện ích kiểm toán khác

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/your-username/audit-software.git
cd audit-software
```

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

3. Chạy chương trình:
```bash
python main.py
```

## Tính năng

- Tạo/Mở Job kiểm toán
- Load và xử lý BCTC từ file XML
- Tính toán mức trọng yếu
- Quản lý mẫu biểu kiểm toán
- Các tiện ích hỗ trợ

## Công nghệ sử dụng

- Python 3.x
- PyQt6
- XML processing

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
