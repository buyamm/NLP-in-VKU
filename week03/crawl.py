from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time

from underthesea import classify, sent_tokenize, ner, word_tokenize

PLACE_KEYWORDS = {
    "danang": ["đà nẵng", "son tra", "bà nà", "mỹ khê"],
    "hanoi": ["hà nội", "hoàn kiếm", "ba đình", "hồ gươm"],
    "quangbinh": ["quảng bình", "phong nha", "kẻ bàng"]
}




def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

def crawl_article_links(num_links):
    driver = init_driver()
    wait = WebDriverWait(driver, 10)

    driver.get("https://vnexpress.net/du-lich/diem-den/viet-nam")

    links = set()

    while len(links) < num_links:
        time.sleep(2)

        articles = driver.find_elements(By.CSS_SELECTOR, "article h2 a")

        for a in articles:
            href = a.get_attribute("href")
            if href and href.startswith("https://vnexpress.net"):
                links.add(href)
            if len(links) >= num_links:
                break


        # click trang sau
        try:
            next_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "a.next-page")
                )
            )
            driver.execute_script("arguments[0].click();", next_btn)
        except NoSuchElementException:
            print("Không còn trang")
            break

    driver.quit()

    with open("artical_link.txt", "w", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")

    print(f"Đã lưu {len(links)} link")

def get_article_content(driver, url):
    driver.get(url)
    time.sleep(2)

    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1.title-detail").text
    except:
        title = ""

    try:
        paragraphs = driver.find_elements(
            By.CSS_SELECTOR, "article.fck_detail p"
        )
        content = " ".join([p.text for p in paragraphs])
    except:
        content = ""

    return title, content

def sentence_tokenize(content):
    return sent_tokenize(content)

def name_entity_recognition(sentence):
    ''' 
        result = (word, pos, chunk, ner_tag)
        ner_tag = 'O' → không phải entity

        B-XXX → bắt đầu entity loại XXX
        I-XXX → tiếp tục entity loại XXX
    '''

    result = ner(sentence)
    entities, buf, etype = [], [], None

    for w, _, _, tag in result:
        if tag.startswith('B-'):
            if buf:
                entities.append({'text': ' '.join(buf), 'ner_tag': etype})
            buf, etype = [w], tag[2:]
        elif tag.startswith('I-'):
            buf.append(w)
        elif buf:
            entities.append({'text': ' '.join(buf), 'ner_tag': etype})
            buf, etype = [], None

    if buf:
        entities.append({'text': ' '.join(buf), 'ner_tag': etype})
        
    return entities

    

def connect_words(sentence):
    return word_tokenize(sentence, format="text")




def detect_place(content):
    content = content.lower()
    for place, keywords in PLACE_KEYWORDS.items():
        for kw in keywords:
            if kw in content:
                return place
    return None




def detect_category(title):
    CATEGORY_MAP = {
    "c": "Chính trị",
    "e": "Kinh tế",
    "l": "Pháp luật",
    "s": "Thể thao",
    "g": "Giáo dục",
    "h": "Sức khỏe"
    }

    try:
        label = classify(title)[0][0]
        return CATEGORY_MAP.get(label, "Khác")
    except:
        return "Khác"



import json
from collections import defaultdict

def process_articles():
    driver = init_driver()

    results = {
        "danang": defaultdict(list),
        "hanoi": defaultdict(list),
        "quangbinh": defaultdict(list)
    }



    with open("artical_link.txt", "r", encoding="utf-8") as f:
        links = f.read().splitlines()

    for url in links:
        try:
            sentences = []

            title, content = get_article_content(driver, url)
            if not content:
                continue

            place = detect_place(content)
            if not place:
                continue

            category = detect_category(title)

            sentences_result = sentence_tokenize(content)

            for s in sentences_result:
                s_ner = name_entity_recognition(s)
                s_connected = connect_words(s)
                sentences.append({
                    "text": s,
                    "connecting_words": s_connected,
                    "entities": s_ner
                })

            results[place][category].append({
                "title": title,
                "url": url,
                "content": content,
                "sentences": sentences
            })

        except Exception as e:
            print("Lỗi:", url, e)

    driver.quit()

    for place, data in results.items():
        if data:
            with open(f"{place}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            print(f"Không có dữ liệu {place}")

if __name__ == "__main__":
    crawl_article_links(num_links=100)
    process_articles()
