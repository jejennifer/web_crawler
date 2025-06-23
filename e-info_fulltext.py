from turtle import title
import requests, bs4, pandas as pd, textwrap, re, time
from pathlib import Path

HEADERS  = {"User-Agent": "Mozilla/5.0"}

def get_soup(url):
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    r.encoding = "utf-8"
    return bs4.BeautifulSoup(r.text, "lxml")

def clean_body(soup):
    body = soup.select_one("article[id^='node-content-'] .field-name-field--1 .field-item")
    if not body:
        raise RuntimeError("找不到正文區")

    CSS_TRASH = [
         ".align-center figcaption",  # 圖片說明
         ".share-buttons",            # 分享列
         ".field-label",              # 「延伸閱讀」標題
         "ul > li > a[href*='/node/']"  # 延伸閱讀項目 (可依需求調)
    ]
    for css in CSS_TRASH:
        for n in body.select(css):
            n.decompose()

    return body

def safe_filename(name):
    cleaned = re.sub(r'[\\/:*?"<>|]', "_", name.strip())
    return cleaned                  # 轉安全檔名

OUTPUT_DIR = Path(__file__).parent / "output" / "e-info"

def save_txt(title: str, url: str, content: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)             # 若不存在就建立
    slug = "".join(c if c.isalnum() else "_" for c in title)[:80]
    filepath = OUTPUT_DIR / f"{slug}.txt"

    with filepath.open("w", encoding="utf-8") as f:
        f.write(f"{title}\n\n{content}")#f.write(f"{title}\n{url}\n\n{content}")

    print(f"Saved to {filepath.relative_to(Path.cwd())}")

def main():
    BASE_DIR = Path(__file__).parent
    excel_path = BASE_DIR.parent / "01.網頁初步文章篩選" / "e-info_減碳新生活.xlsx"

    df = pd.read_excel(excel_path)

    for i, row in df.iterrows():
        url   = row["網址"]

        try:
            soup  = get_soup(url)
            body  = clean_body(soup)
            paras = [p.get_text(" ", strip=True) for p in body.find_all("p") if p.get_text(strip=True)]
            full  = "\n".join(paras)

            h1 = soup.select_one("h1.title")
            title = h1.get_text(" ", strip=True) if h1 else "no-title"
            print(f"({i+1}/{len(df)}) {title}")

            save_txt(title, url, full)

            print("【預覽 120 字】", textwrap.shorten(full, 120, placeholder=" …"))
            time.sleep(1)
        except Exception as e:
            print(f"Error on {url}: {e}")

# #單篇文章測試
# def run_single(url: str):
#     soup = get_soup(url)

#     # 標題
#     h1 = soup.select_one("h1.title")
#     title = h1.get_text(" ", strip=True) if h1 else "no-title"

#     # 正文
#     body  = clean_body(soup)  
    
#     full_text = "\n".join(
#     line.strip()
#     for line in body.get_text("\n").splitlines()
#     if line.strip()
#     )

#     # 存檔
#     save_txt(title, url, full_text)
#     print("===== 標題 =====")
#     print(title)
#     print("\n===== Preview 120 chars =====")
#     print(textwrap.shorten(full_text, 120, placeholder=" …"))

# def main():
#     TEST_URL = "https://e-info.org.tw/node/241392"   # 先填一篇單篇網址
#     run_single(TEST_URL)

if __name__ == "__main__":
    main()