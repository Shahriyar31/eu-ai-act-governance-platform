import os
import json
import time
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

# The three regulations we want — official EUR-Lex URLs
REGULATIONS = [
    {
        "name": "eu_ai_act",
        "title": "EU AI Act (Regulation EU 2024/1689)",
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32024R1689"
    },
    {
        "name": "gdpr",
        "title": "GDPR (Regulation EU 2016/679)",
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679"
    },
    {
        "name": "eu_data_act",
        "title": "EU Data Act (Regulation EU 2023/2854)",
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32023R2854"
    }
]

def scrape_regulation(regulation: dict) -> str:
    print(f"Scraping {regulation['title']}...")

    result = app.scrape_url(
        regulation["url"],
        params={
            "formats": ["markdown"],
            "onlyMainContent": True
        }
    )

    # newer SDK returns a dict, not an object
    # print the keys so we can see exactly what came back
    if isinstance(result, dict):
        print(f"Response keys: {list(result.keys())}")
        content = result.get("markdown") or result.get("content") or ""
    else:
        content = result.markdown

    if not content:
        print(f"WARNING: empty content for {regulation['name']}")
        print(f"Full response: {result}")
        return ""

    print(f"Got {len(content)} characters for {regulation['name']}")
    return content

def save_regulation(name: str, content: str):
    # save raw markdown so we never need to scrape again
    os.makedirs("data/regulations", exist_ok=True)
    filepath = f"data/regulations/{name}.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved to {filepath}")

def main():
    for regulation in REGULATIONS:
        try:
            content = scrape_regulation(regulation)
            save_regulation(regulation["name"], content)
            # be polite to the server — wait 2 seconds between requests
            time.sleep(2)
        except Exception as e:
            print(f"Failed to scrape {regulation['name']}: {e}")

    print("\nDone. All regulations saved to data/regulations/")

if __name__ == "__main__":
    main()