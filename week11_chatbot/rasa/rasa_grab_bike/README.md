# GrabBot – Chatbot Đặt Xe (Rasa)

Chatbot mô phỏng chức năng đặt xe đơn giản bằng Rasa (tiếng Việt).

## Cấu trúc project

```
rasa_grab_bike/
├── config.yml          # Cấu hình NLU pipeline và policies
├── domain.yml          # Intents, entities, slots, responses
└── data/
    ├── nlu.yml         # Training data (intent + entity examples + synonyms)
    ├── stories.yml     # Luồng hội thoại mẫu
    └── rules.yml       # Quy tắc cứng (greet, goodbye, cancel, fallback)
```

## Intents

| Intent         | Mô tả                          |
|----------------|-------------------------------|
| `greet`        | Chào hỏi                      |
| `book_ride`    | Yêu cầu đặt xe                |
| `inform`       | Cung cấp thông tin (địa điểm, loại xe) |
| `confirm`      | Xác nhận chuyến đi            |
| `cancel`       | Hủy chuyến                    |
| `goodbye`      | Tạm biệt                      |

## Entities

| Entity          | Mô tả        | Ví dụ                        |
|-----------------|-------------|------------------------------|
| `from_location` | Điểm đi     | Sơn Trà, bến xe, VKU         |
| `to_location`   | Điểm đến    | sân bay, Ngũ Hành Sơn        |
| `vehicle_type`  | Loại xe     | xe máy, ô tô 4 chỗ, ô tô 7 chỗ |

## Synonyms

- `xe máy` ← motorbike, xe moto, xe 2 bánh, grab bike
- `ô tô 4 chỗ` ← car, ô tô, xe hơi, xe 4 chỗ, sedan
- `ô tô 7 chỗ` ← xe 7 chỗ, xe van, minivan

## Cách chạy

```bash
# 1. Vào thư mục project
cd rasa_grab_bike

# 2. Train model
rasa train

# 3. Chạy chatbot
rasa shell
```

## Ví dụ hội thoại

```
User: xin chào
Bot:  Xin chào! Tôi là GrabBot 🚗 Tôi có thể giúp bạn đặt xe. Bạn muốn đặt xe không?

User: tôi muốn đặt xe
Bot:  Bạn muốn đi từ đâu?

User: Sơn Trà
Bot:  Bạn muốn đi đến đâu?

User: VKU
Bot:  Bạn muốn đi loại xe gì? (xe máy / ô tô 4 chỗ / ô tô 7 chỗ)

User: xe máy
Bot:  ✅ Đã đặt xe thành công!
      🚩 Điểm đi: Sơn Trà
      🏁 Điểm đến: VKU
      🚗 Loại xe: xe máy
      Vui lòng chờ tài xế đến đón bạn!
```
