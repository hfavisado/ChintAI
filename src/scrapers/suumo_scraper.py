import asyncio
from typing import List, Dict
import aiohttp
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from ..models.property import Property, PropertyType

class SuumoScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://suumo.jp"
        self.search_url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/"

    async def search_properties(self, **kwargs) -> List[Property]:
        """
        Search for properties on SUUMO based on given criteria
        """
        params = {
            'ar': '030',  # Tokyo 23 wards
            'bs': '040',  # Mansion type
            'pc': '30',   # Price up to 230k
            'po1': '25',  # Floor area from 65m2
            'po2': '99',  # Floor area to max
            'shkr1': '03',  # City gas
            'shkr2': '03',  # Reinforced concrete
            'shkr3': '03',  # 2nd floor or higher
            'shkr4': '03',  # Within 10 minutes to station
            'rn': '0005'   # Sort by new
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.search_url, params=params, headers=self.headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch properties: {response.status}")

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                properties = []

                # Find all property listings
                listings = soup.find_all('div', class_='cassetteitem')
                
                for listing in listings:
                    property_data = await self._parse_listing(listing)
                    if self._validate_property(property_data):
                        properties.append(Property(**property_data))

                return properties

    async def _parse_listing(self, listing) -> Dict:
        """
        Parse a single property listing
        """
        # Extract basic information
        title = listing.find('div', class_='cassetteitem_content-title').text.strip()
        address = listing.find('li', class_='cassetteitem_detail-col1').text.strip()
        
        # Extract price and floor area
        price_text = listing.find('span', class_='cassetteitem_price--rent').text.strip()
        price = float(price_text.replace('万円', '').replace(',', '')) * 10000
        
        floor_area_text = listing.find('span', class_='cassetteitem_menseki').text.strip()
        floor_area = float(floor_area_text.replace('m2', ''))
        
        # Extract station information
        station_info = listing.find('li', class_='cassetteitem_detail-col2').text.strip()
        station_parts = station_info.split('歩')
        nearest_station = station_parts[0].strip()
        station_distance = float(station_parts[1].replace('分', '').strip())
        
        # Extract floor
        floor_text = listing.find('span', class_='cassetteitem_floor').text.strip()
        floor = int(floor_text.split('階')[0])
        
        # Extract URL
        url = self.base_url + listing.find('a', class_='js-cassette_link')['href']

        return {
            'source': 'suumo',
            'property_type': PropertyType.RENT,
            'url': url,
            'title': title,
            'price': price,
            'floor_area': floor_area,
            'floor': floor,
            'nearest_station': nearest_station,
            'station_distance': station_distance,
            'address': address,
            'building_material': 'reinforced_concrete',
            'gas_type': 'city_gas'
        }

    async def get_property_details(self, url: str) -> Property:
        """
        Get detailed information about a specific property
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch property details: {response.status}")

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract additional details
                description = soup.find('div', class_='property_view_note').text.strip()
                image_url = soup.find('img', class_='property_view_object--item')['src']
                
                # Get direction (south-facing preference)
                direction = None
                direction_elem = soup.find('th', text='向き')
                if direction_elem:
                    direction = direction_elem.find_next('td').text.strip()

                # Get the basic property data
                property_data = await self._parse_listing(soup.find('div', class_='cassetteitem'))
                
                # Add the additional details
                property_data.update({
                    'description': description,
                    'image_url': image_url,
                    'direction': direction
                })

                return Property(**property_data) 