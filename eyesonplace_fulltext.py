import requests, bs4, pandas as pd, textwrap, re, time
from pathlib import Path

#URL      = "https://eyesonplace.net/2025/06/18/28085/"
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

OUTPUT_DIR = Path(__file__).parent / "output" / "eyesonplace"

def save_txt(title: str, url: str, content: str) -> None:
    """將文章存成 UTF-8 .txt，檔名用 slug 化的 title。"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)             # 若不存在就建立
    slug = "".join(c if c.isalnum() else "_" for c in title)[:80]
    filepath = OUTPUT_DIR / f"{slug}.txt"

    with filepath.open("w", encoding="utf-8") as f:
        f.write(f"{title}\n\n{content}")#f.write(f"{title}\n{url}\n\n{content}")

    print(f"✅ Saved to {filepath.relative_to(Path.cwd())}")

def main():
    BASE_DIR = Path(__file__).parent
    excel_path = BASE_DIR.parent / "01.網頁初步文章篩選" / "eyesonplace_韌性與調適.xlsx"

    df = pd.read_excel(excel_path)

    for i, row in df.iterrows():
        url   = row["網址"]
        title = row["標題"]

        try:
            print(f"\n({i+1}/{len(df)}) {title}")
            soup  = get_soup(url)
            body  = clean_body(soup)
            paras = [p.get_text(" ", strip=True) for p in body.find_all("p") if p.get_text(strip=True)]
            full  = "\n".join(paras)

            save_txt(title, url, full)

            print("【預覽 120 字】", textwrap.shorten(full, 120, placeholder=" …"))
            time.sleep(1)
        except Exception as e:
            print(f"Error on {url}: {e}")

if __name__ == "__main__":
    main()


