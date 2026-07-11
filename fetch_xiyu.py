import requests
from bs4 import BeautifulSoup
import re
import json
import datetime
import os

COLUMN_URL = "https://www.peopleweekly.cn/html/zt/xiyu/index.html"
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xiyu.json")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    # 抓取栏目页
    resp = requests.get(COLUMN_URL, headers=headers, timeout=15)
    resp.raise_for_status()
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')

    today = datetime.datetime.now().strftime("%Y%m%d")

    # 查找习语文章链接
    all_links = soup.find_all('a', href=re.compile(r'.*xiyu.*\.html'))
    article_link = None

    for link in all_links:
        href = link.get('href')
        if href and today in href:
            article_link = href
            break

    if not article_link and all_links:
        article_link = all_links[0].get('href')

    if not article_link:
        raise Exception("未找到习语文章链接")

    # 补全链接
    if not article_link.startswith('http'):
        if article_link.startswith('/'):
            article_link = "https://www.peopleweekly.cn" + article_link
        else:
            article_link = "https://www.peopleweekly.cn/" + article_link.lstrip('./')

    print(f"文章链接: {article_link}")

    # 抓取文章
    art_resp = requests.get(article_link, headers=headers, timeout=15)
    art_resp.encoding = 'utf-8'
    art_soup = BeautifulSoup(art_resp.text, 'html.parser')

    # 提取标题
    title = "今日习语"
    for sel in ['h1', '.article-title', '.title', '.content-title', 'header h1']:
        tag = art_soup.select_one(sel)
        if tag and tag.get_text().strip():
            title = tag.get_text().strip()
            break

    # 提取正文
    body = ""
    for sel in ['.article-content', '.content', 'article', '.text', '.article-body', '.content-body']:
        tag = art_soup.select_one(sel)
        if tag:
            for el in tag(["script", "style", "div", "span", "a"]):
                el.decompose()
            text = tag.get_text(separator='\n', strip=True)
            text = re.sub(r'\n\s*\n', '\n\n', text)
            if text and len(text) > 50:
                body = text
                break

    if not body:
        paragraphs = art_soup.find_all('p')
        body = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

    if not body:
        body = "暂时无法获取今日内容，请稍后刷新。"

    data = {
        "title": title,
        "body": body.strip(),
        "url": article_link,
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"习语获取成功: {title}")
    print(f"已保存到 {OUTPUT_FILE}")

except Exception as e:
    print(f"获取失败: {e}")
    # 失败时写入错误信息
    error_data = {
        "title": "今日习语",
        "body": "暂时无法获取今日内容，请稍后刷新。",
        "url": "",
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "error": str(e)
    }
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(error_data, f, ensure_ascii=False, indent=2)
