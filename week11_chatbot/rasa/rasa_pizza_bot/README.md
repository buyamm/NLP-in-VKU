# 🍕 PizzaBot – Rasa 3.x

Chatbot đặt pizza xây dựng bằng Rasa Open Source 3.x.  
Tài liệu này bao gồm: khái niệm cơ bản, hướng dẫn cài đặt, cấu trúc project, lưu ý quan trọng và giải đáp câu hỏi lý thuyết.

---

## 1. Các khái niệm cơ bản

### Intent
Ý định của người dùng – bot cần nhận ra người dùng **muốn làm gì**.

| Intent | Ý nghĩa |
|---|---|
| `greet` | Chào hỏi |
| `goodbye` | Tạm biệt |
| `order_pizza` | Muốn đặt pizza |
| `inform` | Cung cấp thông tin (size, topping) |
| `affirm` | Xác nhận (yes/yeah) |
| `deny` | Từ chối (no/nope) |

### Entity
Thông tin cụ thể được trích xuất từ câu nói của người dùng.

Ví dụ: `"I want a [medium](pizza_size) pizza with [cheese](pizza_topping)"`
- `medium` → **entity value** (giá trị thực tế trong câu)
- `pizza_size` → **entity type** (loại thông tin)
- `[medium](pizza_size)` → **annotated entity** (cú pháp Rasa)

Cú pháp chuẩn: `[value](entity_type)`

### Slot
Bộ nhớ tạm của bot trong một cuộc hội thoại.  
Slot lưu lại entity đã trích xuất để dùng trong response hoặc logic sau.

### Response (utter_*)
Câu trả lời mẫu của bot, khai báo trong `domain.yml`.  
Có thể dùng slot variable: `"Your {pizza_size} pizza with {pizza_topping}"`

### Story
Kịch bản hội thoại mẫu – dạy bot biết **luồng hội thoại** nào là hợp lệ.

### Rule
Quy tắc cứng – luôn luôn đúng, không phụ thuộc ngữ cảnh.  
Ví dụ: khi user nói `goodbye` → luôn trả lời `utter_goodbye`.

---

## 2. Cấu trúc file

```
rasa_pizza_bot/
├── config.yml          # Pipeline NLU + Policy
├── domain.yml          # Intents, entities, slots, responses, actions
├── data/
│   ├── nlu.yml         # Training data: intent + entity examples
│   ├── stories.yml     # Luồng hội thoại mẫu
│   └── rules.yml       # Quy tắc cứng
├── endpoints.yml       # Kết nối action server (nếu dùng custom action)
└── models/             # Model sau khi train (tự sinh)
```

---

## 3. Môi trường & Cài đặt

### Môi trường Docker (Rasa Pro 3.16.x)

Nếu bạn đang dùng Docker image có sẵn Rasa Pro 3.16.x (Python 3.10):

```bash
# Kiểm tra version
rasa --version
# Rasa Pro Version: 3.16.5a1 | Python: 3.10.12

# Không cần cài thêm gì – Rasa đã có trong image
```

### Cài đặt thủ công (nếu không dùng Docker)

Yêu cầu: Python **3.10** (Rasa Pro 3.16 yêu cầu Python 3.10+)

```bash
pip install -U pip
pip install rasa          # cài bản mới nhất
# hoặc cụ thể: pip install rasa==3.6.19  (Rasa Open Source)
```

### Khởi tạo project

```bash
cd rasa_pizza_bot
rasa init --no-prompt
```

> `--no-prompt` bỏ qua các câu hỏi tương tác, tạo project NLU-based mặc định.  
> Nếu muốn CALM: `rasa init --template calm` (cần LLM/API key)

### ⚠️ Rasa Pro 3.16 – NLU-based vs CALM

Rasa Pro 3.x có **2 kiến trúc**:

| | NLU-based | CALM |
|---|---|---|
| Config | `DIETClassifier` + `TEDPolicy` | `CompactLLMCommandGenerator` + `FlowPolicy` |
| Data | `nlu.yml` + `stories.yml` | `flows.yml` |
| Cần LLM? | ❌ Không | ✅ Có (OpenAI, Llama...) |
| Phù hợp | Bài học, không cần API | Production với LLM |

Project này dùng **NLU-based** – vẫn được hỗ trợ đầy đủ trên Rasa Pro 3.16.

---

## 4. Train bot

Sau khi chỉnh sửa bất kỳ file nào trong `data/` hoặc `domain.yml`:

```bash
rasa train
```

Model được lưu vào thư mục `models/`.

---

## 5. Chat thử

```bash
rasa shell
```

Thử hội thoại:

```
hello
I want to order a pizza
medium
cheese
```

Hoặc một câu đầy đủ:

```
I want a large pizza with cheese and onion
```

Thoát: `/stop`

---

## 6. Lưu ý quan trọng

### ⚠️ Về YAML indentation
YAML rất nhạy cảm với **khoảng trắng (spaces)**. Không dùng tab, chỉ dùng spaces.  
Sai indentation → lỗi khi `rasa train`.

### ⚠️ Về annotated entity trong nlu.yml
```yaml
- I want a [medium](pizza_size) pizza with [cheese](pizza_topping)
```
- Phải có ít nhất **2–3 ví dụ có entity** để model học được.
- Entity value phải **khớp chính xác** với text trong câu.

### ⚠️ Về slot type `list`
`pizza_topping` dùng `type: list` vì user có thể chọn nhiều topping.  
Khi dùng `{pizza_topping}` trong response, Rasa sẽ in ra dạng list Python: `['cheese', 'onion']`.  
Để format đẹp hơn cần dùng **custom action** (Python).

### ⚠️ Về stories vs rules
- `stories.yml`: dạy bot **luồng hội thoại có ngữ cảnh** (ML-based).
- `rules.yml`: quy tắc **luôn đúng**, không phụ thuộc lịch sử hội thoại.
- Nên dùng `rules.yml` cho các hành vi đơn giản, cố định (greet, goodbye).

### ⚠️ Về config.yml
File `config.yml` khai báo **pipeline NLU** (cách xử lý text) và **policies** (cách chọn action).  
Không sửa nếu chưa hiểu rõ – dùng mặc định của `rasa init` là ổn cho bài tập.

### ⚠️ Phải `rasa train` lại sau mỗi lần sửa data
Rasa là ML-based: mọi thay đổi trong `nlu.yml`, `stories.yml`, `domain.yml` đều cần train lại để có hiệu lực.

---

## 7. Giải đáp câu hỏi lý thuyết

### Q1: Intent `order_pizza` dùng để làm gì?
`order_pizza` là nhãn phân loại ý định – bot dùng nó để nhận ra rằng người dùng **muốn đặt pizza**.  
Khi NLU model phân loại được intent này, Rasa Core sẽ tra cứu trong `stories.yml` / `rules.yml` để quyết định **action tiếp theo** (hỏi size, hỏi topping, hay xác nhận đơn hàng).

### Q2: Entity `pizza_size` và `pizza_topping` khác gì intent?
| | Intent | Entity |
|---|---|---|
| Là gì | Ý định tổng thể của câu | Thông tin cụ thể trong câu |
| Ví dụ | `order_pizza` | `medium`, `cheese` |
| Mục đích | Quyết định luồng hội thoại | Lưu vào slot để dùng sau |
| Số lượng/câu | 1 intent/câu | Nhiều entity/câu |

Nói đơn giản: intent = **"muốn gì"**, entity = **"muốn cái gì cụ thể"**.

### Q3: File `nlu.yml` và `stories.yml` khác nhau thế nào?
| | nlu.yml | stories.yml |
|---|---|---|
| Dạy bot | Hiểu ngôn ngữ tự nhiên | Điều hướng hội thoại |
| Nội dung | Ví dụ câu → intent/entity | Chuỗi intent → action |
| Dùng bởi | NLU model (phân loại) | Dialogue model (chọn action) |
| Ví dụ | `"I want pizza"` → `order_pizza` | `order_pizza` → `utter_ask_size` |

`nlu.yml` trả lời: **"Câu này có nghĩa gì?"**  
`stories.yml` trả lời: **"Sau khi hiểu câu đó, bot nên làm gì?"**

### Q4: Vì sao bot cần `rasa train` sau khi sửa dữ liệu?
Rasa dùng **machine learning** – bot không đọc file YAML trực tiếp khi chat.  
Thay vào đó, `rasa train` sẽ:
1. Đọc toàn bộ training data
2. Train NLU model (phân loại intent, trích xuất entity)
3. Train Dialogue model (học luồng hội thoại từ stories)
4. Lưu model đã train vào `models/`

Khi `rasa shell`, bot load model đã train – không phải file YAML.  
→ Sửa YAML mà không train lại = bot vẫn dùng model cũ, không có thay đổi.
