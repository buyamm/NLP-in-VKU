import re
import csv
import json
import time
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://vku.udn.vn/vi/doi-ngu-giang-vien/"

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"(?:\+?84|0)(?:\d[\s.-]?){8,10}"

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

driver = init_driver()

def get_html(url):
    try:
        driver.get(url)
        time.sleep(2)
        return driver.page_source
    except Exception as e:
        print(f"[Error] Không tải được {url}: {e}")
        return ""

def find_related_links(base_url, limit=10):
    links = set()
    base_domain = urlparse(base_url).netloc

    for el in driver.find_elements(By.TAG_NAME, "a"):
        href = el.get_attribute("href")
        if not href:
            continue
        if urlparse(href).netloc == base_domain:
            links.add(href)
        if len(links) >= limit:
            break

    return list(links)

def extract_contacts(html):
    emails = list(set(re.findall(EMAIL_REGEX, html)))
    phones = list(set(
        re.sub(r"[\s.-]", "", p) for p in re.findall(PHONE_REGEX, html)
    ))
    return emails, phones

def main():
    print(f"Crawling: {BASE_URL}")
    get_html(BASE_URL)

    urls = find_related_links(BASE_URL)
    urls.insert(0, BASE_URL)

    results = []

    for url in urls:
        print(f"→ {url}")
        html = get_html(url)
        emails, phones = extract_contacts(html)

        results.append({
            "url": url,
            "emails": emails,
            "phones": phones
        })

    # ==== LƯU JSON ====
    with open("contacts_vku.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("Đã lưu contacts_vku.json")

if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()
