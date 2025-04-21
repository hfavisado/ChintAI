from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class PropertyType(str, Enum):
    RENT = "rent"
    PURCHASE = "purchase"

class Property(BaseModel):
    source: str
    property_type: PropertyType
    url: str
    title: str
    price: float
    floor_area: float = Field(ge=65)  # Minimum 65m2
    floor: int = Field(ge=2)  # Minimum 2nd floor
    nearest_station: str
    station_distance: float = Field(le=10)  # Maximum 10 minutes
    address: str
    building_material: str = "reinforced_concrete"
    gas_type: str = "city_gas"
    direction: Optional[str] = None  # Optional: south-facing preference
    description: Optional[str] = None
    image_url: Optional[str] = None
    posted_date: Optional[str] = None 