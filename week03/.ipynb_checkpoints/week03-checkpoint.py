import re

if re.match('abc', "abcdef"):
    print("Match found")


 # ============ w ==========
word_regex = r'\w+'
print(re.match(word_regex, "hello 123"))
print(re.match(word_regex, "123"))


# ===================== ? * + . ================
string = "color colorful colourful colour oh! hhh! ooh! oooh! baa baaa baaaa begin begun begun began"
for s in re.findall(r'colou?r', string): # ?: co hoac khong
    print(s)

for s in re.findall(r'oo*h!', string):    # *: 0 or more
    print(s)


for s in re.findall(r'o+h!', string):    # +: 1 or more
    print(s)

for s in re.findall(r'baa+', string):    
    print(s)

for s in re.findall(r'beg.n', string):    # . : any character
    print(s)


# ==================== ^ $ ==================
pattern = r'