from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
import models
from models import Country, Base
from database import get_db, engine
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import requests
import os
import random
import datetime
from schemas import CountryResponse, StatusResponse, RefreshResponse
from PIL import Image, ImageDraw, ImageFont

app = FastAPI()

Base.metadata.create_all(bind=engine)

COUNTRIES_API = os.getenv("COUNTRIES_API")
EXCHANGE_API = os.getenv("EXCHANGE_API")

os.makedirs("cache", exist_ok=True)

def validate_country_data(country_data: dict[str, any]):
    errors = {}
    name = country_data.get("name")
    if name is None or not isinstance(name, str) or not name.strip():
        errors["name"] = "is required"

    population = country_data.get("population")
    if population is None:
        errors["population"] = "is required"
    elif not isinstance(population, int) or population < 0:
        errors["population"] = "must be a positive integer"

    currencies = country_data.get("currencies")
    if currencies is None:
        errors["currencies"] = "is required"
    elif not isinstance(currencies, list):
        errors["currencies"] = "must be an array"

    if errors:
        raise HTTPException(
            status_code=400,
            detail={"error": "Validation failed", "details": errors}
        )

def generate_summary_image(db: Session):
    try:

        total_countries = db.query(Country).count()
        top_countries = db.query(Country).order_by(Country.estimated_gdp.desc()).limit(5).all()
        last_refreshed = db.query(Country).order_by(Country.last_refreshed_at.desc()).first()

        image = Image.new('RGB', (600, 400), color='white')#this is like my background
        draw = ImageDraw.Draw(image)#and this calls draw

        #for my fonts
        title_font = ImageFont.truetype("arial.ttf", 24) 
        med_font = ImageFont.truetype("arial.ttf", 18)
        small_font = ImageFont.truetype("arial.ttf", 14)

        draw.text((10, 10), f"Total Countries: {total_countries}", fill='black')

        draw.text((10, 40), "Top 5 Countries by Estimated GDP:", fill='black')

        y_pos = 70
        for i, country in enumerate(top_countries, 1):
            gdp = f"${country.estimated_gdp:,.2f}" if country.estimated_gdp else "N/A"
            draw.text((20, y_pos), f"{i}. {country.name}: {gdp}", fill='black')
            y_pos += 30

        if last_refreshed:
            draw.text((20, 250), f"Last Refreshed At: {last_refreshed.last_refreshed_at.strftime('%Y-%m-%d %H:%M:%S')}", fill='black')

        image.save("cache/summary.png")
        return True
    
    except Exception as e:
        print(f"Image generation failed: {e}") 
        return False




@app.post("/countries/refresh", response_model=RefreshResponse)
def fetch_countries(db: Session = Depends(get_db)):
    try:
        #testing if the api link is working
        try:
            countries_response = requests.get(COUNTRIES_API, timeout=30)
            countries_response.raise_for_status()
            countries_data = countries_response.json()
        except requests.exceptions.Timeout:
            raise HTTPException(
                status_code=503,
                detail={"error": "External data source unavailable", "details": "Could not fetch data from Countries API"}
            )
        
        #testing if the exchange api link is working
        try:
            exchange_response = requests.get(EXCHANGE_API, timeout=30)
            exchange_response.raise_for_status()
            exchange_data = exchange_response.json()
        except requests.exceptions.Timeout:
            raise HTTPException(
                status_code=503,
                detail={"error": "External data source unavailable", "details": "Could not fetch data from Exchange API"}
            )
    
        last_refreshed_at = datetime.datetime.now(datetime.timezone.utc)
        
        #trying to get the rates for each currency
        if isinstance(exchange_data, dict) :
            exchange_rates = exchange_data.get("rates", {})
        else:
            exchange_rates = {}

        for country in countries_data:

            try:

                validate_country_data(country)

                name = country.get("name", "").strip()
                capital = country.get("capital")
                region = country.get("region")
                population = country.get("population", 0)
                flag_url = country.get("flag")
                currencies = country.get("currencies", [])

                if currencies and isinstance(currencies, list) and len(currencies) > 0:
                    currency = currencies[0]
                    if isinstance(currency, dict):
                        currency_code = (currency.get("code", "").upper())
                    else:
                        currency_code = None
                else:
                    currency_code = None

                if currency_code is None:
                    exchange_rate = None
                    estimated_gdp = 0.0
                else:
                    rate = exchange_rates.get(currency_code)
                    if rate is None:
                        exchange_rate = None
                        estimated_gdp = None
                    else:         
                        exchange_rate = rate     
                        multiplier = random.uniform(1000, 2000)
                        if exchange_rate > 0.0 and population > 0:
                            estimated_gdp = (population * multiplier) / exchange_rate
                    
                existing_country = db.query(Country).filter(Country.name.ilike(name)).first()

                if existing_country:
                    #update te  existing country
                    existing_country.capital = capital
                    existing_country.region = region
                    existing_country.population = population
                    existing_country.currency_code = currency_code
                    existing_country.exchange_rate = exchange_rate
                    existing_country.estimated_gdp = estimated_gdp
                    existing_country.flag_url = flag_url
                    existing_country.last_refreshed_at = last_refreshed_at
                else:
                    #create new country
                    new_country = Country(
                        name=name,
                        capital=capital,
                        region=region,
                        population=population,
                        currency_code=currency_code,
                        exchange_rate=exchange_rate,
                        estimated_gdp=estimated_gdp,
                        flag_url=flag_url,
                        last_refreshed_at=last_refreshed_at
                    )
                    db.add(new_country)

            except Exception as e:
                continue

        db.commit()

        generate_summary_image(db)

        return RefreshResponse(
            message="Country data refreshed successfully",
            # countries_processed=len(countries_data),
            # countries_updated=db.query(Country).filter(Country.last_refreshed_at == last_refreshed_at).count(),
            # countries_created=db.query(Country).filter(Country.last_refreshed_at == last_refreshed_at).count(),
            last_refreshed_at=last_refreshed_at
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal Server Error"}
        )
    

@app.get("/countries/image")
def get_summary_image():
    image_path = "cache/summary.png"
    if os.path.exists(image_path):
        return FileResponse(image_path, media_type="image/png", filename="summary.png")
    else:
        raise HTTPException(
            status_code=404,
            detail={"error": "Summary image not found"}
        )
            

@app.get("/countries", response_model=List[CountryResponse])
def get_countries(region: Optional[str] = None, currency: Optional[str] = None, sort: Optional[str] = None, db: Session = Depends(get_db)):

    try:
        query = db.query(Country)

        if region:
            query = query.filter(Country.region.ilike(region))
        if currency:
            query = query.filter(Country.currency_code.ilike(currency))
        if sort == "population_asc":
            query = query.order_by(Country.population.asc())
        elif sort == "population_desc":
            query = query.order_by(Country.population.desc())
        elif sort == "gdp_asc":
            query = query.order_by(Country.estimated_gdp.asc())
        elif sort == "gdp_desc":
            query = query.order_by(Country.estimated_gdp.desc())
        elif sort == "name_desc":
            query = query.order_by(Country.name.desc())
        else:
            query = query.order_by(Country.name.asc())

        countries = query.all()
        return countries if countries else []
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal Server Error"}
        )



@app.get("/countries/{country_name}", response_model=CountryResponse)
def get_country(country_name: str, db: Session = Depends(get_db)):
    country = db.query(Country).filter(Country.name.ilike(country_name)).first()
    if not country:
        raise HTTPException(status_code=404, detail={"error": "Country not found"})
    return country

@app.get("/status", response_model=StatusResponse)
def get_status(db: Session = Depends(get_db)):
    total_countries = db.query(Country).count()
    last_refreshed_country = db.query(Country.last_refreshed_at).order_by(Country.last_refreshed_at.desc()).first()
    if last_refreshed_country:
        last_refreshed_at = last_refreshed_country.last_refreshed_at
    else:
        last_refreshed_at = None

    return StatusResponse(
        total_countries=total_countries,
        last_refreshed_at=last_refreshed_at
    )

@app.delete("/countries/{country_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(country_name: str, db: Session = Depends(get_db)):
    country = db.query(Country).filter(Country.name.ilike(country_name)).first()
    if not country:
        raise HTTPException(status_code=404, detail={"error": "Country not found"})
    
    db.delete(country)
    db.commit()

