import json

# đọc file json
with open("Question2/data/danang.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# lấy content
contents = []
for category in data:
    for article in data[category]:
        contents.append(article["content"])

# lưu vào file txt
with open("Question2/data/content.json", "w", encoding="utf-8") as f:
    json.dump(contents, f, ensure_ascii=False, indent=4)