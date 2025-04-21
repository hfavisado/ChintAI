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
            
            # Extract image URL from cassetteitem_object-item
            image_element = item.find("div", class_="cassetteitem_object-item")
            image_url = None
            if image_element:
                img_tag = image_element.find("img", class_="js-noContextMenu js-linkImage js-scrollLazy js-adjustImg")
                if img_tag and "rel" in img_tag.attrs:
                    # Get the URL from the rel attribute
                    image_url = img_tag["rel"]
                    # Ensure the URL is complete
                    if image_url.startswith("//"):
                        image_url = f"https:{image_url}"
                    elif not image_url.startswith("http"):
                        image_url = f"https://{image_url}"
            
            # Extract details from each column
            details = {}
            detail_cols = item.find_all("li", class_=lambda x: x and x.startswith("cassetteitem_detail-col"))
            for col in detail_cols:
                # Extract just the number from the class name
                col_num = col["class"][0].split("-")[-1].replace("col", "")
                text = col.text.strip()
                
                # Split multi-line text and create separate entries
                lines = text.split('\n')
                if len(lines) > 1:
                    for i, line in enumerate(lines, 1):
                        details[f"detail{col_num}-{i}"] = line.strip()
                else:
                    details[f"detail{col_num}"] = text
            
            properties.append({
                "title": title,
                "image_url": image_url,
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

    def save_to_html(self, properties: List[Dict], output_file: str):
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SUUMO Rental Properties</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .property-card {{
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                    padding: 20px;
                    display: flex;
                    gap: 20px;
                }}
                .property-image {{
                    flex: 0 0 300px;
                    height: 200px;
                    overflow: hidden;
                    border-radius: 4px;
                }}
                .property-image img {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                }}
                .property-info {{
                    flex: 1;
                }}
                .property-title {{
                    font-size: 1.5em;
                    margin-bottom: 15px;
                    color: #333;
                }}
                .property-details {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                    gap: 10px;
                }}
                .detail-item {{
                    background-color: #f8f8f8;
                    padding: 8px;
                    border-radius: 4px;
                }}
                .detail-label {{
                    font-weight: bold;
                    color: #666;
                }}
                h1 {{
                    color: #333;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .last-updated {{
                    text-align: center;
                    color: #666;
                    margin-bottom: 30px;
                }}
            </style>
        </head>
        <body>
            <h1>SUUMO Rental Properties</h1>
            <div class="last-updated">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        """
        
        for prop in properties:
            html_content += f"""
            <div class="property-card">
                <div class="property-image">
                    <img src="{prop['image_url']}" alt="{prop['title']}">
                </div>
                <div class="property-info">
                    <h2 class="property-title">{prop['title']}</h2>
                    <div class="property-details">
            """
            
            for detail_key, detail in prop['details'].items():
                html_content += f"""
                        <div class="detail-item">
                            <div class="detail-label">{detail_key}</div>
                            <div class="detail-value">{detail}</div>
                        </div>
                """
            
            html_content += """
                    </div>
                </div>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

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
            
        # Save to HTML
        html_file = os.path.join(output_dir, "suumo_properties.html")
        scraper.save_to_html(properties, html_file)
        
        print(f"Found {len(properties)} properties and saved to {markdown_file}, {json_file}, and {html_file}")
    except Exception as e:
        print(f"Error during scraping: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 