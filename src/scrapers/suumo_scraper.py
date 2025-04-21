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

    def parse_property(self, cassette_item) -> Dict:
        try:
            # Extract property title
            title = cassette_item.find("div", class_="cassetteitem_content-title").text.strip()
            
            # Extract property details
            details = cassette_item.find("div", class_="cassetteitem_detail").text.strip()
            
            # Extract all available rooms
            rooms = []
            room_elements = cassette_item.find_all("tr", class_="js-cassette_link")
            
            for room in room_elements:
                room_data = {
                    "floor": room.find("td", class_="cassetteitem_other-cell1").text.strip(),
                    "price": room.find("td", class_="cassetteitem_other-cell2").text.strip(),
                    "layout": room.find("td", class_="cassetteitem_other-cell3").text.strip(),
                    "size": room.find("td", class_="cassetteitem_other-cell4").text.strip(),
                    "url": self.base_url + room.find("a")["href"]
                }
                rooms.append(room_data)
            
            return {
                "title": title,
                "details": details,
                "rooms": rooms
            }
        except Exception as e:
            print(f"Error parsing property: {e}")
            return None

    async def scrape_properties(self, url: str) -> List[Dict]:
        async with aiohttp.ClientSession() as session:
            html = await self.fetch_page(session, url)
            soup = BeautifulSoup(html, 'html.parser')
            
            properties = []
            cassette_items = soup.find_all("div", class_="cassetteitem")
            
            for item in cassette_items:
                property_data = self.parse_property(item)
                if property_data:
                    properties.append(property_data)
            
            return properties

    def save_to_markdown(self, properties: List[Dict], output_file: str):
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# SUUMO Rental Properties\n\n")
            f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for prop in properties:
                f.write(f"## {prop['title']}\n\n")
                f.write(f"**Details:** {prop['details']}\n\n")
                
                f.write("### Available Rooms:\n\n")
                for room in prop['rooms']:
                    f.write(f"- **Floor:** {room['floor']}\n")
                    f.write(f"  - **Price:** {room['price']}\n")
                    f.write(f"  - **Layout:** {room['layout']}\n")
                    f.write(f"  - **Size:** {room['size']}\n")
                    f.write(f"  - **URL:** {room['url']}\n\n")
                f.write("---\n\n")

async def main():
    url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&pc=30&smk=&po1=25&po2=99&sd=1&shkr1=03&shkr2=03&shkr3=03&shkr4=03&rn=0005&ra=013&cb=0.0&ct=9999999&ts=1&et=9999999&mb=65&mt=9999999&cn=9999999&fw2="
    
    scraper = SuumoScraper()
    properties = await scraper.scrape_properties(url)
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "suumo_properties.md")
    
    scraper.save_to_markdown(properties, output_file)
    print(f"Scraped {len(properties)} properties and saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main()) 