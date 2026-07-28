# 🚗 RideBot - Chatbot Đặt Xe Tiếng Việt

RideBot là chatbot đặt xe thông minh được xây dựng bằng **Rasa Open Source 3.x**, chạy hoàn toàn trong **Docker Container**.

---

## 📋 Yêu Cầu Hệ Thống

- [Docker](https://docs.docker.com/get-docker/) >= 20.x
- [Docker Compose](https://docs.docker.com/compose/install/) >= 2.x
- RAM tối thiểu: 4GB (khuyến nghị 8GB)
- Ổ cứng trống: ~5GB

### Cài đặt Docker (Ubuntu/Debian)

```bash
# Cài Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Cài Docker Compose plugin
sudo apt-get install docker-compose-plugin

# Kiểm tra
docker --version
docker compose version
```

---

## 📁 Cấu Trúc Project

```
ridebot/
│
├── actions/
│   ├── __init__.py
│   └── actions.py          # Custom Action: tính giá, lưu lịch sử
│
├── data/
│   ├── nlu.yml             # Dữ liệu training NLU tiếng Việt
│   └── rules.yml           # Rules điều hướng hội thoại
│
├── models/                 # Thư mục chứa model đã train (tự sinh)
│
├── config.yml              # Cấu hình pipeline NLU + Policies
├── credentials.yml         # Cấu hình kênh kết nối
├── domain.yml              # Domain: intents, slots, forms, responses
├── endpoints.yml           # Endpoint action server
├── Dockerfile              # Docker image cho Rasa server
├── docker-compose.yml      # Orchestration 2 services
├── requirements.txt        # Python dependencies
└── README.md               # Tài liệu này
```

---

## 🚀 Cách Chạy Project

### Bước 1: Clone / Tải project

```bash
cd ridebot
```

### Bước 2: Train model

Train model Rasa (cần chạy lần đầu hoặc khi thay đổi data):

```bash
# Cách 1: Train bằng Docker Compose profile
docker compose --profile train run --rm rasa_train

# Cách 2: Train trực tiếp bằng Rasa CLI (nếu có Rasa cài local)
rasa train
```

> ⏳ Quá trình train mất khoảng 3–10 phút tùy cấu hình máy.

### Bước 3: Khởi động toàn bộ hệ thống

```bash
docker compose up
```

Hoặc chạy nền (detached mode):

```bash
docker compose up -d
```

### Bước 4: Kiểm tra services đang chạy

```bash
docker compose ps
```

Kết quả mong đợi:
```
NAME                    STATUS    PORTS
ridebot_rasa            running   0.0.0.0:5005->5005/tcp
ridebot_action_server   running   0.0.0.0:5055->5055/tcp
```

### Bước 5: Dừng hệ thống

```bash
docker compose down
```

---

## 💬 Cách Test Chatbot

### Test qua REST API (curl)

```bash
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender": "user1", "message": "xin chào"}'
```

### Test qua Rasa Shell (interactive)

```bash
# Mở shell tương tác trong container rasa
docker compose exec rasa rasa shell
```

### Test qua Rasa Interactive

```bash
docker compose exec rasa rasa interactive
```

---

## 🗣️ Ví Dụ Hội Thoại

```
User:  xin chào
Bot:   Xin chào! Tôi là RideBot 🚗. Bạn muốn đặt xe đi đâu?

User:  tôi muốn đặt xe
Bot:   Bạn muốn đi từ đâu?

User:  VKU
Bot:   Bạn muốn đi đến đâu?

User:  sân bay
Bot:   Bạn muốn đi loại xe gì? Ví dụ: xe máy, ô tô, 4 chỗ, 7 chỗ.

User:  xe máy
Bot:   ✅ Đã đặt xe máy từ VKU đến sân bay.
       📍 Khoảng cách dự kiến: 8 km.
       💰 Giá dự kiến: 64,000đ.
       Cảm ơn bạn đã sử dụng RideBot! 🚗

User:  tạm biệt
Bot:   Tạm biệt! Hẹn gặp lại bạn lần sau nhé 👋
```

---

## 🗺️ Địa Điểm & Giá Cước

### Địa điểm hỗ trợ
| Địa điểm       |
|----------------|
| VKU            |
| Sân bay        |
| Cầu Rồng       |
| Bến xe         |
| Cầu Sông Hàn   |

### Bảng giá theo loại xe
| Loại xe | Giá/km    |
|---------|-----------|
| Xe máy  | 8,000đ    |
| Ô tô    | 12,000đ   |
| 4 chỗ   | 14,000đ   |
| 7 chỗ   | 18,000đ   |

### Khoảng cách mẫu
| Từ           | Đến      | Khoảng cách |
|--------------|----------|-------------|
| VKU          | Sân bay  | 8 km        |
| Cầu Rồng     | Bến xe   | 5 km        |
| VKU          | Bến xe   | 15 km       |
| Cầu Sông Hàn | Sân bay  | 3 km        |

> Các tuyến chưa có trong danh sách sẽ được tính mặc định **10 km**.

---

## 📊 Lịch Sử Đặt Xe

Mỗi lần đặt xe thành công, dữ liệu được lưu vào:

```
data/ride_history.csv
```

Định dạng CSV:
```
timestamp,from_location,to_location,vehicle_type,distance_km,total_price_vnd
2024-01-15 10:30:00,VKU,sân bay,xe máy,8,64000
```

---

## 🔧 Troubleshooting

### Lỗi: Model chưa được train
```
ERROR: No model found
```
**Giải pháp:** Chạy lại lệnh train model ở Bước 2.

### Lỗi: Action server không kết nối được
```
ERROR: Failed to connect to action server
```
**Giải pháp:** Kiểm tra container action_server đang chạy:
```bash
docker compose logs action_server
```

### Xem logs realtime
```bash
# Logs tất cả services
docker compose logs -f

# Logs riêng từng service
docker compose logs -f rasa
docker compose logs -f action_server
```

### Rebuild image sau khi thay đổi code
```bash
docker compose build --no-cache
docker compose up
```

---

## 🛠️ Phát Triển Thêm

### Thêm địa điểm mới
Chỉnh sửa dictionary `DISTANCES` trong `actions/actions.py`:
```python
DISTANCES = {
    ("địa điểm mới", "sân bay"): 12,
    ...
}
```

### Thêm loại xe mới
Chỉnh sửa dictionary `PRICE_PER_KM` trong `actions/actions.py`:
```python
PRICE_PER_KM = {
    "xe tải": 25_000,
    ...
}
```

### Thêm câu training
Chỉnh sửa `data/nlu.yml` và chạy lại `rasa train`.

---

## 📝 License

MIT License - Tự do sử dụng cho mục đích học tập và phát triển.
