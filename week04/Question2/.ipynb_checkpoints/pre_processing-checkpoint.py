import json
import re

with open("Question2/data/content.json", "r", encoding="utf-8") as f:
    documents = json.load(f)


# setup cac stopword
with open("Question2/data/vietnamese-stopwords.txt", "r", encoding="utf-8") as f:
    stopwords = set(line.strip() for line in f if line.strip())


prossed_docs = []

for doc in documents:
    # Lowercase
    text = doc.lower()

    # loai bo dau cau
    text = re.sub(r'[^\w\s]', ' ', text)

    # tokenization
    tokens = text.split()

    # stopword
    tokens = [t for t in tokens if t not in stopwords]

    prossed_docs.append(tokens)

# lưu vào file json
with open("Question2/data/prossed_data.json", "w", encoding="utf-8") as f:
    json.dump(prossed_docs, f, ensure_ascii=False, indent=4)

print("Kết quả sau preprocessing:")
print(prossed_docs[0][:50])     