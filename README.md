# 📌 DailyKotlinTip

**DailyKotlinTip** is an automated Python script that uses the [OpenAI API](https://platform.openai.com/) to generate a new Kotlin tip each day, then publishes it to a public [RSS feed](https://oliviermarteaux.github.io/DailyKotlinTip/rss.xml) via [GitHub Pages](https://pages.github.com/).

> 📡 [Subscribe to the RSS feed](https://oliviermarteaux.github.io/DailyKotlinTip/rss.xml)

---

## ✨ Features

- ✅ Automatically generates a new Kotlin tip every day using ChatGPT
- 🧠 Tips follow Jetpack Compose best practices and Android development patterns
- 💡 Includes title, explanation, and code snippet with styled HTML
- 🔁 Daily automation via GitHub Actions (or manual execution)
- 📄 Tips are saved as standalone HTML files
- 🌐 RSS feed auto-updated for feed readers (Inoreader, Feedly, etc.)

---

## 📂 Repository Structure

```
DailyKotlinTip/
├── articles/           # HTML files for each tip
├── rss.xml             # Auto-generated RSS feed
├── index.html          # Web index of all tips
├── update_rss.py       # Python script to request + update RSS
└── .github/workflows/  # GitHub Actions for automation
```

---

## 🚀 How It Works

1. Fetch previous tip titles from `rss.xml`
2. Ask ChatGPT for a new Kotlin tip (excluding previous ones)
3. Save tip to `articles/YYYYMMDDhhmmss.html`
4. Append a new `<item>` to the RSS feed
5. Update `index.html` with all article links
6. Auto-commit and publish to GitHub Pages

---

## ⚙️ Requirements

- Python 3.8+
- `openai`
- `python-dateutil`
- OpenAI API key (`OPENAI_API_KEY` environment variable)

Install dependencies:

```bash
pip install openai python-dateutil
```

---

## 🧪 Run Manually

```bash
export OPENAI_API_KEY=your_key_here
python update_rss.py
```

---

## 🔄 Automate with GitHub Actions

A GitHub workflow is included to run the script daily at 08:00 Paris time:

```yaml
on:
  schedule:
    - cron: '0 6 * * *'  # 08:00 Paris = 06:00 UTC
  workflow_dispatch:
```

To use:
1. Add your OpenAI key as a repository secret named `OPENAI_API_KEY`
2. Enable GitHub Pages (e.g., from `main` branch or `docs` folder)

---

## 📡 Feed Reader Integration

Use any feed reader like:

- [Inoreader](https://inoreader.com/)
- [Feedly](https://feedly.com/)
- [NetNewsWire](https://netnewswire.com/)
- [Kill the Newsletter](https://kill-the-newsletter.com/)

Paste the RSS URL:

```
https://oliviermarteaux.github.io/DailyKotlinTip/rss.xml
```

> ⚠️ **Note:** Some RSS readers (like Inoreader) may cache feed content and not reflect updates immediately.  
> If you don’t see the latest tip, try refreshing manually or wait a few hours.

---
