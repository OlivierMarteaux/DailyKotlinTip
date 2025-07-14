#!/usr/bin/env python3
"""
Generate a Kotlin tip with ChatGPT and insert it into rss.xml
—————————————————————————————————————————————————————————
* Requires:  `pip install openai python-dateutil`
* Environment: OPENAI_API_KEY
* Place file at repo root (or adjust path in workflow).
"""
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from dateutil import tz
import logging

from openai import OpenAI

# —————————————————— Config ——————————————————
MODEL = "gpt-4o-mini"  # or "gpt-3.5-turbo"
SITE_ROOT = "https://oliviermarteaux.github.io/DailyKotlinTip"  # ← edit this
RSS_PATH = "rss.xml"  # at repo root
ARTICLE_FOLDER = "articles"  # html snippets live here (optional)
TIMEZONE = timezone.utc  # keep RSS dates in GMT
# ————————————————————————————————————————

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

client = OpenAI()  # reads OPENAI_API_KEY from env automatically

def indent(elem, level=0):
    """Pretty-print an XML tree (ElementTree-compatible)."""
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            indent(child, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
            
def get_kotlin_tip() -> dict:
    logging.info("Requesting Kotlin tip from ChatGPT...")
    prompt = (
        "You are an experimented Android Development teacher,"
        "specialized in Kotlin language and Jetpack Compose framework."
        "You like to provide clear and concise tips to students,"
        "following Google recommended best practices and using real cases examples.\n"
        "Please provide me a new Kotlin programming tip based on our whole chat thread. Format it with:\n"
        "- A title using an <h2> tag\n"
        "- Explanation in <p> tags\n"
        "- Kotlin code inside <pre><code> tags using an inline CSS for <pre> with:\n"
        "  - background-color: #8a428a\n"
        "  - white font\n"
        "  - padding: 12px\n"
        "  - border-radius: 8px\n"
        "  - font-size: 13px\n"
        "  - overflow-x: auto\n"
        "Do not use markdown-style code fences like ```html or triple quotes.\n"
        "Just return clean HTML only."
    )
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        html = resp.choices[0].message.content.strip()
        logging.info("Tip received from ChatGPT.")
    except Exception as e:
        logging.error(f"Failed to get tip from ChatGPT: {e}")
        raise

    # Extract title from <h2> tag
    start = html.find("<h2")
    end = html.find("</h2>") + 5
    if start == -1 or end == -1:
        logging.warning("Could not find <h2> tag in the response; using fallback title.")
        title_text = "Kotlin Tip"
    else:
        title_html = html[start:end]
        title_text = title_html.replace("<h2>", "").replace("</h2>", "").strip()
    logging.info(f"Extracted tip title: {title_text}")
    return {"title": title_text, "html": html}


def ensure_rss_exists(path: str):
    if os.path.exists(path):
        logging.info(f"RSS file found at {path}.")
        return
    logging.info(f"RSS file not found, creating new RSS skeleton at {path}.")
    root = ET.Element("rss", version="2.0")
    channel = ET.SubElement(root, "channel")
    for tag, text in [
        ("title", "Daily Kotlin Tips"),
        ("link", SITE_ROOT),
        ("description", "Auto‑generated Kotlin advice"),
        ("language", "en-us"),
        ("lastBuildDate", ""),
    ]:
        ET.SubElement(channel, tag).text = text
        
    # --- Feed icon -------------------------------
    image = ET.SubElement(channel, "image")
    ET.SubElement(image, "url").text = f"{SITE_ROOT}/icon.png"
    ET.SubElement(image, "title").text = "Daily Kotlin Tips"
    ET.SubElement(image, "link").text = SITE_ROOT
    # ---------------------------------------------
    
    indent(root)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def insert_item(tip: dict):
    try:
        ensure_rss_exists(RSS_PATH)
        tree = ET.parse(RSS_PATH)
        root = tree.getroot()
        channel = root.find("channel")

        now = datetime.now(TIMEZONE)
        pub_date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")
        slug = now.strftime("%Y%m%d%H%M%S")
        link = f"{SITE_ROOT}/{ARTICLE_FOLDER}/{slug}.html"

        logging.info(f"Creating article file {ARTICLE_FOLDER}/{slug}.html")
        os.makedirs(ARTICLE_FOLDER, exist_ok=True)
        with open(f"{ARTICLE_FOLDER}/{slug}.html", "w", encoding="utf-8") as f:
            f.write(tip["html"])

        logging.info("Inserting new item into rss.xml")
        item = ET.Element("item")
        ET.SubElement(item, "title").text = tip["title"]
        ET.SubElement(item, "link").text = link
        ET.SubElement(item, "description").text = tip["html"]
        ET.SubElement(item, "pubDate").text = pub_date
        ET.SubElement(item, "guid").text = link

        existing_items = channel.findall("item")
        if existing_items:
            # get position of first <item> without deprecated getchildren()
            children = list(channel)
            first_idx = next(
                (i for i, child in enumerate(children) if child.tag == "item"),
                len(children),
            )
            channel.insert(first_idx, item)
        else:
            channel.append(item)

        lb = channel.find("lastBuildDate")
        if lb is None:
            lb = ET.SubElement(channel, "lastBuildDate")
        lb.text = pub_date

        indent(root)
        tree.write(RSS_PATH, encoding="utf-8", xml_declaration=True)
        logging.info(f"RSS updated and saved to {RSS_PATH}")
    except Exception as e:
        logging.error(f"Error updating RSS feed: {e}")
        raise

def update_index():
    logging.info("Updating index.html with all articles...")
    article_files = sorted(
        [f for f in os.listdir(ARTICLE_FOLDER) if f.endswith(".html")],
        reverse=True  # newest first
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Daily Kotlin Tip</title>
</head>
<body>
  <h1>Daily Kotlin Tips</h1>
  <ul>
    <li><a href="rss.xml">📡 RSS Feed</a></li>
  </ul>
  <h2>All Tips</h2>
  <ul>
""")
        for file in article_files:
            title = file.replace(".html", "")
            f.write(f'    <li><a href="articles/{file}">{title}</a></li>\n')

        f.write("""  </ul>
</body>
</html>
""")
    logging.info("index.html updated.")

if __name__ == "__main__":
    logging.info("Starting update_rss.py")
    try:
        tip = get_kotlin_tip()
        insert_item(tip)
        update_index()
        logging.info("update_rss.py finished successfully.")
    except Exception as e:
        logging.error(f"Script failed: {e}")
        exit(1)