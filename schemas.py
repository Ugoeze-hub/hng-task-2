from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class CountryResponse(BaseModel):
    id: int
    name: str
    capital: Optional[str] = None
    region: Optional[str] = None
    population: int
    currency_code: Optional[str] = None
    exchange_rate: Optional[float] = None
    estimated_gdp: Optional[float] = None
    flag_url: Optional[str] = None
    last_refreshed_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat().replace('+00:00', 'Z')
        }
    )

    

class StatusResponse(BaseModel):
    total_countries: int
    last_refreshed_at: Optional[datetime] = None

    model_config = ConfigDict(json_encoders={
        datetime: lambda v: v.isoformat().replace('+00:00', 'Z')
    })

class RefreshResponse(BaseModel):
    message: str
    countries_stored: int
    last_refreshed_at: datetime

    model_config = ConfigDict(json_encoders={
        datetime: lambda v: v.isoformat().replace('+00:00', 'Z')
    })