import asyncio
from scrapers.suumo_scraper import SuumoScraper
from models.property import Property
from typing import List
import json
from datetime import datetime

async def main():
    # Initialize scrapers
    suumo_scraper = SuumoScraper()
    
    # Get properties from all sources
    properties: List[Property] = []
    
    try:
        suumo_properties = await suumo_scraper.search_properties()
        properties.extend(suumo_properties)
    except Exception as e:
        print(f"Error scraping SUUMO: {str(e)}")

    # Sort properties by price
    properties.sort(key=lambda x: x.price)

    # Save results to a JSON file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump([p.dict() for p in properties], f, ensure_ascii=False, indent=2)

    print(f"Found {len(properties)} properties matching the criteria")
    print(f"Results saved to {filename}")

    # Print summary of results
    for prop in properties:
        print(f"\nTitle: {prop.title}")
        print(f"Price: ¥{prop.price:,.0f}/month")
        print(f"Floor Area: {prop.floor_area}m²")
        print(f"Floor: {prop.floor}F")
        print(f"Station: {prop.nearest_station} ({prop.station_distance}min)")
        print(f"Address: {prop.address}")
        if prop.direction:
            print(f"Direction: {prop.direction}")
        print(f"URL: {prop.url}")

if __name__ == "__main__":
    asyncio.run(main()) 