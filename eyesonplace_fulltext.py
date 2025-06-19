import requests, bs4, pandas as pd, textwrap, re, time

URL      = "https://eyesonplace.net/2025/06/18/28085/"
HEADERS  = {"User-Agent": "Mozilla/5.0"}

def get_soup(url):
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return bs4.BeautifulSoup(r.text, "lxml")

def clean_body(soup):
    body = soup.select_one(".entry-content")
    if not body:
        raise RuntimeError("找不到.entry-content")

    CSS_TRASH = [
        ".wp-block-quote.is-layout-flow.wp-block-quote-is-layout-flow", ".m-a-box-container",
    ]
    for css in CSS_TRASH:
        for n in body.select(css):
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
title   = soup.select_one("h1.wp-block-post-title").get_text(strip=True)

body  = clean_body(soup)
paras = [p.get_text(" ", strip=True) for p in body.find_all("p") if p.get_text(strip=True)]
full  = "\n".join(paras)

save_txt(title, URL, full)

print("\n【預覽 120 字】\n", textwrap.shorten(full, 120, placeholder=" …"))


