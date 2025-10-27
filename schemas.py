from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CountryResponse(BaseModel):
    id: int
    name: str
    capital: Optional[str]
    region: Optional[str]
    population: int
    currency_code: str
    exchange_rate: Optional[float]
    estimated_gdp: Optional[float]
    flag_url: Optional[str]
    last_refreshed_at: datetime
    
    class Config:
        from_attributes = True

class StatusResponse(BaseModel):
    total_countries: int
    last_refreshed_at: Optional[datetime]

class RefreshResponse(BaseModel):
    message: str
    # countries_processed: int
    # countries_updated: int
    # countries_created: int
    last_refreshed_at: datetime