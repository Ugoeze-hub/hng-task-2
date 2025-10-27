import sys
import os

# Add your app directory to path
sys.path.append('.')

from database import get_db, engine, SessionLocal
from models import Country, Base
from PIL import Image, ImageDraw
import random

def test_image_generation():
    try:
        # Create test data
        db = SessionLocal()
        
        # Clear existing data
        db.query(Country).delete()
        
        # Add some test countries
        test_countries = [
            Country(
                name="Test Country 1",
                population=1000000,
                currency_code="USD",
                exchange_rate=1.0,
                estimated_gdp=1500000000.0
            ),
            Country(
                name="Test Country 2", 
                population=5000000,
                currency_code="EUR",
                exchange_rate=0.85,
                estimated_gdp=3000000000.0
            )
        ]
        
        for country in test_countries:
            db.add(country)
        
        db.commit()
        
        # Test your image function
        from main import generate_summary_image
        result = generate_summary_image(db)
        
        if result and os.path.exists("cache/summary.png"):
            print("✅ SUCCESS: Image generated successfully!")
            print(f"📁 Image saved at: {os.path.abspath('cache/summary.png')}")
        else:
            print("❌ FAILED: Image generation failed")
            
        # Cleanup
        db.close()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image_generation()