from gensim.models import Word2Vec

sentences = []
with open("truyen_kieu_poem.txt", "r", encoding="utf-8") as file:
    for line in file:
        words = line.strip().lower().split()
        if words:
            sentences.append(words)

model = Word2Vec(sentences, vector_size=100, sg=0, min_count=1, window=3)

print(model.wv["kiều"])
print(model.wv.most_similar("kiều", topn=5))


word_counts = [(word, model.wv.get_vecattr(word, "count")) 
               for word in model.wv.key_to_index]

# Sắp xếp giảm dần
word_counts = sorted(word_counts, key=lambda x: x[1], reverse=True)


print("Top 10:")
for word, count in word_counts[:10]:
    print(f"{word}: {count}")


print(model.wv["người"])
print("Từ tương tự người:")
print(model.wv.most_similar("người", topn=5))