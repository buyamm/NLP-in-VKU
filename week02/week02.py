from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import json


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


# ================= PHASE 1 =================
def collect_links(limit=100):
    driver = init_driver()
    driver.get("https://dev.to")
    time.sleep(3)

    links = set()

    while len(links) < limit:
        articles = driver.find_elements(
            By.CSS_SELECTOR,
            "a.crayons-story__hidden-navigation-link"
        )

        for a in articles:
            link = a.get_attribute("href")
            if link and link.startswith("https://dev.to/"):
                links.add(link)
                if len(links) >= limit:
                    break

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
        time.sleep(2)

    driver.quit()

    with open("article_links.txt", "w", eLancoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")

    print(f"Collected {len(links)} article links")


# ================= PHASE 2 =================
def get_content(driver):
    try:
        return driver.find_element(
            By.ID, "article-body"
        ).text.strip()
    except:
        return ""


def get_comments(driver):
    comments_data = []

    comments = driver.find_elements(By.CSS_SELECTOR, "div.comment")

    for c in comments:
        try:
            author = c.find_element(
                By.CSS_SELECTOR, "button.profile-preview-card__trigger"
            ).text.strip()
        except:
            author = ""

        try:
            time_comment = c.find_element(
                By.CSS_SELECTOR, "a.comment-date>time").text.strip()
        except:
            time_comment = ""

        try:
            content = c.find_element(
                By.CSS_SELECTOR, "div.comment__body>p"
            ).text.strip()
        except:
            content = ""

        comments_data.append({
            "author": author,
            "time": time_comment,
            "content": content
        })

    return comments_data


def crawl(n):
    driver = init_driver()

    with open("article_links.txt", encoding="utf-8") as f:
        links = [line.strip() for line in f]

    articles_data = []

    for idx, link in enumerate(links[:n]):  
        print(f"Crawling {idx+1}: {link}")
        driver.get(link)
        time.sleep(3)

    
        article_content = get_content(driver)

        
        comments = get_comments(driver)

        article_data = {
            "title": driver.title.strip(),
            "link": link,
            "content": article_content,
            "number_comment": len(comments),
            "comments": comments
        }

        articles_data.append(article_data)

    driver.quit()

    # Save the data to a JSON file
    with open("data.json", "w", encoding="utf-8") as json_file:
        json.dump(articles_data, json_file, ensure_ascii=False, indent=4)

    print(f"Collected data for {len(articles_data)} articles")


# ================= MAIN =================
if __name__ == "__main__":
    n= 100
    collect_links(n)  
    crawl(n)