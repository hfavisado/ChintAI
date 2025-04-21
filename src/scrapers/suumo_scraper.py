import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
import json
import os

class SuumoScraper:
    def __init__(self):
        self.base_url = "https://suumo.jp"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> str:
        async with session.get(url, headers=self.headers) as response:
            html = await response.text()
            # Save raw HTML for debugging in the output directory
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            with open(os.path.join(output_dir, "raw.html"), "w", encoding="utf-8") as f:
                f.write(html)
            return html

    def parse_properties(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, 'html.parser')
        titles = []
        for title_element in soup.find_all("div", class_="cassetteitem_content-title"):
            title = title_element.text.strip()
            titles.append(title)
        return titles

    def save_to_markdown(self, titles: List[str], output_file: str):
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# SUUMO Rental Properties\n\n")
            f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for title in titles:
                f.write(f"- {title}\n")

async def main():
    url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&pc=30&smk=&po1=25&po2=99&sd=1&shkr1=03&shkr2=03&shkr3=03&shkr4=03&rn=0005&ra=013&cb=0.0&ct=9999999&ts=1&et=9999999&mb=65&mt=9999999&cn=9999999&fw2="
    
    scraper = SuumoScraper()
    
    try:
        async with aiohttp.ClientSession() as session:
            html = await scraper.fetch_page(session, url)
            titles = scraper.parse_properties(html)
        
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to markdown
        markdown_file = os.path.join(output_dir, "suumo_properties.md")
        scraper.save_to_markdown(titles, markdown_file)
        
        # Save to JSON
        json_file = os.path.join(output_dir, "suumo_properties.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(titles, f, ensure_ascii=False, indent=2)
        
        print(f"Found {len(titles)} properties and saved to {markdown_file} and {json_file}")
    except Exception as e:
        print(f"Error during scraping: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 