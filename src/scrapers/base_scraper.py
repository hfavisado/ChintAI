from abc import ABC, abstractmethod
from typing import List
from ..models.property import Property

class BaseScraper(ABC):
    def __init__(self):
        self.base_url = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    @abstractmethod
    async def search_properties(self, **kwargs) -> List[Property]:
        """
        Search for properties based on given criteria
        """
        pass

    @abstractmethod
    async def get_property_details(self, url: str) -> Property:
        """
        Get detailed information about a specific property
        """
        pass

    def _validate_property(self, property_data: dict) -> bool:
        """
        Validate if a property meets the mandatory criteria
        """
        required_fields = [
            'price',
            'floor_area',
            'floor',
            'nearest_station',
            'station_distance',
            'address',
            'building_material',
            'gas_type'
        ]
        
        # Check if all required fields are present
        if not all(field in property_data for field in required_fields):
            return False

        # Validate specific criteria
        if property_data['floor_area'] < 65:
            return False
        if property_data['floor'] < 2:
            return False
        if property_data['station_distance'] > 10:
            return False
        if property_data['building_material'].lower() != 'reinforced_concrete':
            return False
        if property_data['gas_type'].lower() != 'city_gas':
            return False

        return True 