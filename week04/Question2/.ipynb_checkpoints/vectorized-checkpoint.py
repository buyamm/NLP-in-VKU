import json

with open("Question2/data/prossed_data.json", "r", encoding="utf-8") as f:
    documents = json.load(f)


# Xay dung vocab
vocab = set()
for doc in documents:
    vocab.update(doc)

vocab = sorted(vocab)
print(f"Kích thước vocab: {len(vocab)}")
print(f"10 từ đầu tiên trong vocab: {vocab[:10]}")
print(f"10 từ cuối cùng trong vocab: {vocab[-10:]}")

# Lay 10 tu xuat hien nhieu nhat
from collections import Counter
word_counts = Counter(word for doc in documents for word in doc)
top10_words = word_counts.most_common(10)
print("10 từ xuất hiện nhiều nhất:")
for word, count in top10_words:
    print(f"{word}: {count} lần")   


# Vector one-hot
# tao mapping tu word -> index
word_to_index = {word: idx for idx, word in enumerate(vocab)}
# tao vector one-hot cho moi document
one_hot_vectors = []
def word_to_one_hot(word):
    vector = [0] * len(vocab)
    if word in word_to_index:
        index = word_to_index[word]
        vector[index] = 1
    return vector

print("Vector one-hot cho 10 từ phổ biến trong vocab:") 
for word, _ in top10_words:
    one_hot = word_to_one_hot(word)
    print(f"{word}: {one_hot[:20]}...") 



# Tao vocab chua 10 tu pho bien nhat
top10_vocab = [word for word, _ in top10_words]
print(f"Vocab từ 10 từ phổ biến nhất: {top10_vocab}")
word_to_index_top10 = {word: idx for idx, word in enumerate(top10_vocab)}
def word_to_one_hot_top10(word):
    vector = [0] * len(top10_vocab)
    if word in word_to_index_top10:
        index = word_to_index_top10[word]
        vector[index] = 1
    return vector

print("Vector one-hot cho 10 từ phổ biến trong vocab:") 
for word, _ in top10_words:
    one_hot = word_to_one_hot_top10(word)
    print(f"{word}: {one_hot}") 



# Bag of Words
def document_to_bow_vector(document):
    vector = [0] * len(vocab)
    for word in document:
        if word in word_to_index:
            index = word_to_index[word]
            vector[index] += 1
    return vector

# Vector BoW cho document dau tien
bow_vector = document_to_bow_vector(documents[0])
print(f"Vector BoW cho document đầu tiên: {bow_vector[:20]}...")
print("Word to index mapping (20 words):")
for word, index in list(word_to_index.items())[:20]:
    print(f"{word}: {index}")