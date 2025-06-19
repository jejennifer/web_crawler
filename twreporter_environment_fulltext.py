import requests, bs4, pandas as pd, textwrap, re, time

URL      = "https://www.twreporter.org/a/after-a-formosan-black-bear-shot-dead-in-hualien-zhuoxi-2"
HEADERS  = {"User-Agent": "Mozilla/5.0"}

def get_soup(url):
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return bs4.BeautifulSoup(r.text, "lxml")

def clean_body(soup):
    body = soup.select_one("#article-body")
    if not body:
        raise RuntimeError("找不到 #article-body")

    CSS_TRASH = [
        # 工具列、募款、分類
        "#mobile-tool-bar", ".desktop-tools__ToolsBlock",
        ".metadata__CategorySetFlexBox-sc-1c3910m-0", ".donation-box__Container-sc-1uszvr7-0",
        ".license__Text-sc-1vtq5dr-0.iYYeim",

        # 相關文章整塊
        '[class^="article-page__RelatedBlock"]',

        # 內文插圖的 FigCaption
        "figcaption",
    ]
    for css in CSS_TRASH:
        for n in body.select(css):
            n.decompose()

    # 卡片殘留文字（摘要、日期）
    for n in body.select('[class^="card__Desc"], [class^="card__PublishedDate"]'):
        n.decompose()

    return body

def safe_filename(name):                  # 轉安全檔名
    return re.sub(r'[\\/:*?"<>|]', "_", name.strip())

def save_txt(title, url, content, date_str=None):
    fname = safe_filename(title) + ".txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"{'='*len(title)}\n{title}\n{'='*len(title)}\n")
        if date_str:
            f.write(f"（{date_str}）\n")
        f.write(f"{url}\n\n")
        f.write(content)
    print(f"✅ 已寫入 {fname}")

rows = []

# ---------- 抓 1 篇 ----------
soup  = get_soup(URL)
title = soup.select_one("meta[property='og:title']")["content"]

body  = clean_body(soup)
paras = [p.get_text(" ", strip=True) for p in body.find_all("p") if p.get_text(strip=True)]
full  = "\n".join(paras)

save_txt(title, URL, full)

print("\n【預覽 120 字】\n", textwrap.shorten(full, 120, placeholder=" …"))


