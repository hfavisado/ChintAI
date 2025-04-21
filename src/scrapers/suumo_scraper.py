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

    def parse_properties(self, html: str) -> tuple[List[Dict], str]:
        soup = BeautifulSoup(html, 'html.parser')
        properties = []
        
        # Extract page title from ui-section-header
        page_title = "SUUMO Rental Properties"  # Default title
        header = soup.find("div", class_="ui-section-header")
        if header:
            page_title = header.text.strip()
        
        # Find all cassette items (each represents a building)
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
                    if not image_url.startswith("http"):
                        image_url = f"https:{image_url}" if image_url.startswith("//") else f"https://{image_url}"
            
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

            # Extract information from cassetteitem_other table
            other_table = item.find("table", class_="cassetteitem_other")
            units = []
            if other_table:
                # Get all property rows (each represents a unit)
                property_rows = other_table.find_all("tr", class_="js-cassette_link")
                for row in property_rows:
                    # Get all cells in this row
                    cells = row.find_all("td")
                    if len(cells) >= 7:  # Ensure we have all expected cells
                        # Floor (3rd cell)
                        floor = cells[2].text.strip()
                        
                        # Rent and management fee (4th cell)
                        rent_cell = cells[3]
                        rent = rent_cell.find("span", class_="cassetteitem_other-emphasis").text.strip() if rent_cell.find("span", class_="cassetteitem_other-emphasis") else "N/A"
                        management_fee = rent_cell.find("span", class_="cassetteitem_price--administration").text.strip() if rent_cell.find("span", class_="cassetteitem_price--administration") else "N/A"
                        
                        # Deposit and key money (5th cell)
                        deposit_cell = cells[4]
                        deposit = deposit_cell.find("span", class_="cassetteitem_price--deposit").text.strip() if deposit_cell.find("span", class_="cassetteitem_price--deposit") else "N/A"
                        key_money = deposit_cell.find("span", class_="cassetteitem_price--gratuity").text.strip() if deposit_cell.find("span", class_="cassetteitem_price--gratuity") else "N/A"
                        
                        # Layout and area (6th cell)
                        layout_cell = cells[5]
                        layout = layout_cell.find("span", class_="cassetteitem_madori").text.strip() if layout_cell.find("span", class_="cassetteitem_madori") else "N/A"
                        area = layout_cell.find("span", class_="cassetteitem_menseki").text.strip() if layout_cell.find("span", class_="cassetteitem_menseki") else "N/A"
                        
                        # Create unit entry
                        unit_details = {
                            "floor": floor,
                            "rent": rent,
                            "management_fee": management_fee,
                            "security_deposit": deposit,
                            "key_money": key_money,
                            "layout": layout,
                            "area": area
                        }
                        units.append(unit_details)
            
            # Create building entry with its units
            properties.append({
                "title": title,
                "image_url": image_url,
                "details": details,
                "units": units
            })
        
        return properties, page_title

    def save_to_markdown(self, properties: List[Dict], page_title: str, output_file: str):
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {page_title}\n\n")
            f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for prop in properties:
                f.write(f"## {prop['title']}\n\n")
                if prop['image_url']:
                    f.write(f"![Property Image]({prop['image_url']})\n\n")
                
                f.write("**Building Details:**\n")
                for detail_key, detail in prop['details'].items():
                    f.write(f"- {detail_key}: {detail}\n")
                
                if prop['units']:
                    f.write("\n**Available Units:**\n")
                    for i, unit in enumerate(prop['units'], 1):
                        f.write(f"\n### Unit {i}\n")
                        f.write(f"- Floor: {unit['floor']}\n")
                        f.write(f"- Rent: {unit['rent']}\n")
                        f.write(f"- Management Fee: {unit['management_fee']}\n")
                        f.write(f"- Security Deposit: {unit['security_deposit']}\n")
                        f.write(f"- Key Money: {unit['key_money']}\n")
                        f.write(f"- Layout: {unit['layout']}\n")
                        f.write(f"- Area: {unit['area']}\n")
                
                f.write("\n---\n\n")

    def save_to_html(self, properties: List[Dict], page_title: str, output_file: str):
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{page_title}</title>
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
                }}
                .property-header {{
                    display: flex;
                    gap: 20px;
                    margin-bottom: 20px;
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
                .building-details {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                    gap: 10px;
                    margin-bottom: 20px;
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
                .unit-details {{
                    background-color: #e8f4f8;
                    padding: 15px;
                    border-radius: 8px;
                    margin-top: 10px;
                }}
                .unit-details h3 {{
                    margin-top: 0;
                    color: #2c3e50;
                }}
                .unit-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                    gap: 10px;
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
            <h1>{page_title}</h1>
            <div class="last-updated">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        """
        
        for prop in properties:
            html_content += f"""
            <div class="property-card">
                <div class="property-header">
                    <div class="property-image">
                        <img src="{prop['image_url']}" alt="{prop['title']}">
                    </div>
                    <div class="property-info">
                        <h2 class="property-title">{prop['title']}</h2>
                        <div class="building-details">
            """
            
            # Add building details
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
            
            # Add unit details if they exist
            if prop['units']:
                for i, unit in enumerate(prop['units'], 1):
                    html_content += f"""
                    <div class="unit-details">
                        <h3>Unit {i}</h3>
                        <div class="unit-grid">
                    """
                    
                    unit_details = {
                        'floor': 'Floor',
                        'rent': 'Rent',
                        'management_fee': 'Management Fee',
                        'security_deposit': 'Security Deposit',
                        'key_money': 'Key Money',
                        'layout': 'Layout',
                        'area': 'Area'
                    }
                    
                    for key, label in unit_details.items():
                        html_content += f"""
                            <div class="detail-item">
                                <div class="detail-label">{label}</div>
                                <div class="detail-value">{unit[key]}</div>
                            </div>
                        """
                    
                    html_content += """
                        </div>
                    </div>
                    """
            
            html_content += """
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def save_to_json(self, properties: List[Dict], page_title: str, output_file: str):
        """Save properties data to a JSON file."""
        data = {
            "title": page_title,
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "properties": properties
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    async def main(self):
        """Main function to run the scraper."""
        async with aiohttp.ClientSession() as session:
            # Example URL for properties in Tokyo's Yamanote Line area
            url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?url=%2Fchintai%2Fichiran%2FFR301FC001%2F&ar=030&bs=040&pc=30&smk=&po1=25&po2=99&shkr1=03&shkr2=03&shkr3=03&shkr4=03&cb=0.0&ct=9999999&et=9999999&mb=0&mt=9999999&cn=9999999&ra=013&rn=0005"
            
            html = await self.fetch_page(session, url)
            properties, page_title = self.parse_properties(html)
            
            # Create output directory if it doesn't exist
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Save to different formats
            self.save_to_json(properties, page_title, os.path.join(output_dir, "suumo_properties.json"))
            self.save_to_markdown(properties, page_title, os.path.join(output_dir, "suumo_properties.md"))
            self.save_to_html(properties, page_title, os.path.join(output_dir, "suumo_properties.html"))

if __name__ == "__main__":
    scraper = SuumoScraper()
    asyncio.run(scraper.main()) 