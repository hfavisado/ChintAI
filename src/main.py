import asyncio
from scrapers.suumo_scraper import SuumoScraper
from typing import List
import json
from datetime import datetime
import os
import aiohttp

async def main():
    # Initialize scraper
    suumo_scraper = SuumoScraper()
    
    # URL to scrape
    url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&pc=30&smk=&po1=25&po2=99&sd=1&shkr1=03&shkr2=03&shkr3=03&shkr4=03&rn=0005&ra=013&cb=0.0&ct=9999999&ts=1&et=9999999&mb=65&mt=9999999&cn=9999999&fw2="
    
    try:
        async with aiohttp.ClientSession() as session:
            html = await suumo_scraper.fetch_page(session, url)
            properties, page_title = suumo_scraper.parse_properties(html)
        
        # Create output directory if it doesn't exist
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to markdown
        markdown_file = os.path.join(output_dir, "suumo_properties.md")
        suumo_scraper.save_to_markdown(properties, page_title, markdown_file)
        
        # Save to JSON
        json_file = os.path.join(output_dir, "suumo_properties.json")
        suumo_scraper.save_to_json(properties, page_title, json_file)
        
        # Save to HTML
        html_file = os.path.join(output_dir, "suumo_properties.html")
        suumo_scraper.save_to_html(properties, page_title, html_file)
        
        print(f"Found {len(properties)} properties and saved to {markdown_file}, {json_file}, and {html_file}")
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 