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

    def parse_properties(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'html.parser')
        properties = []
        
        # Find all cassette items (each represents a property)
        cassette_items = soup.find_all("div", class_="cassetteitem")
        
        for item in cassette_items:
            # Extract title
            title = item.find("div", class_="cassetteitem_content-title").text.strip()
            
            # Extract details from each column
            details = {}
            detail_cols = item.find_all("li", class_=lambda x: x and x.startswith("cassetteitem_detail-col"))
            for col in detail_cols:
                # Extract just the number from the class name
                col_num = col["class"][0].split("-")[-1].replace("col", "")
                details[f"detail{col_num}"] = col.text.strip()
            
            properties.append({
                "title": title,
                "details": details
            })
        
        return properties

    def save_to_markdown(self, properties: List[Dict], output_file: str):
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# SUUMO Rental Properties\n\n")
            f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for prop in properties:
                f.write(f"## {prop['title']}\n\n")
                f.write("**Details:**\n")
                for detail_key, detail in prop['details'].items():
                    f.write(f"- {detail_key}: {detail}\n")
                f.write("\n---\n\n")

async def main():
    url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&pc=30&smk=&po1=25&po2=99&sd=1&shkr1=03&shkr2=03&shkr3=03&shkr4=03&rn=0005&ra=013&cb=0.0&ct=9999999&ts=1&et=9999999&mb=65&mt=9999999&cn=9999999&fw2="
    
    scraper = SuumoScraper()
    
    try:
        async with aiohttp.ClientSession() as session:
            html = await scraper.fetch_page(session, url)
            properties = scraper.parse_properties(html)
        
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to markdown
        markdown_file = os.path.join(output_dir, "suumo_properties.md")
        scraper.save_to_markdown(properties, markdown_file)
        
        # Save to JSON
        json_file = os.path.join(output_dir, "suumo_properties.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(properties, f, ensure_ascii=False, indent=2)
        
        print(f"Found {len(properties)} properties and saved to {markdown_file} and {json_file}")
    except Exception as e:
        print(f"Error during scraping: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 