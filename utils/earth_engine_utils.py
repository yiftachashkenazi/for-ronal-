"""
מודול עזר לGoogle Earth Engine
מכיל פונקציות לעיבוד תמונות לוויין וסיווג שטח
"""

import ee
import numpy as np
from typing import Dict, List, Tuple, Optional
import config

def initialize_ee(service_account_file: Optional[str] = None):
    """
    אתחול Google Earth Engine
    """
    try:
        if service_account_file:
            credentials = ee.ServiceAccountCredentials(None, service_account_file)
            ee.Initialize(credentials)
        else:
            ee.Initialize()
        print("✅ Google Earth Engine initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Earth Engine: {e}")
        return False

def get_satellite_image(bounds: List[float], 
                       date_start: str, 
                       date_end: str, 
                       collection: str = 'sentinel2') -> ee.Image:
    """
    קבלת תמונת לוויין עבור אזור ותאריך נתונים
    
    Args:
        bounds: [west, south, east, north]
        date_start: תאריך התחלה 'YYYY-MM-DD'
        date_end: תאריך סיום 'YYYY-MM-DD'
        collection: סוג אוסף לוויין
    """
    try:
        # יצירת גיאומטריה מהגבולות
        roi = ee.Geometry.Rectangle(bounds)
        
        # בחירת אוסף לוויין
        collection_id = config.SATELLITE_COLLECTIONS.get(collection, config.SATELLITE_COLLECTIONS['sentinel2'])
        
        # טעינת תמונות
        image_collection = (ee.ImageCollection(collection_id)
                           .filterBounds(roi)
                           .filterDate(date_start, date_end)
                           .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))
        
        # חישוב חציון לתמונה נקייה
        image = image_collection.median().clip(roi)
        
        return image
        
    except Exception as e:
        print(f"❌ Error getting satellite image: {e}")
        return None

def calculate_indices(image: ee.Image) -> ee.Image:
    """
    חישוב אינדקסים ספקטרליים לסיווג שטח
    """
    try:
        # NDVI (Normalized Difference Vegetation Index)
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        
        # NDBI (Normalized Difference Built-up Index) 
        ndbi = image.normalizedDifference(['B11', 'B8']).rename('NDBI')
        
        # MNDWI (Modified Normalized Difference Water Index)
        mndwi = image.normalizedDifference(['B3', 'B11']).rename('MNDWI')
        
        # EVI (Enhanced Vegetation Index)
        evi = image.expression(
            '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
            {
                'NIR': image.select('B8'),
                'RED': image.select('B4'),
                'BLUE': image.select('B2')
            }
        ).rename('EVI')
        
        # הוספת האינדקסים לתמונה
        return image.addBands([ndvi, ndbi, mndwi, evi])
        
    except Exception as e:
        print(f"❌ Error calculating indices: {e}")
        return image

def classify_land_use(image: ee.Image) -> ee.Image:
    """
    סיווג שימושי קרקע בהתבסס על אינדקסים ספקטרליים
    """
    try:
        # חישוב אינדקסים
        image_with_indices = calculate_indices(image)
        
        # הגדרת תנאים לסיווג
        # יער - NDVI גבוה
        forest = (image_with_indices.select('NDVI').gt(0.6)
                 .And(image_with_indices.select('EVI').gt(0.3)))
        
        # חקלאות - NDVI בינוני עד גבוה
        agriculture = (image_with_indices.select('NDVI').gt(0.3)
                      .And(image_with_indices.select('NDVI').lt(0.6))
                      .And(image_with_indices.select('EVI').gt(0.2)))
        
        # עירוני - NDBI גבוה, NDVI נמוך
        urban = (image_with_indices.select('NDBI').gt(0.1)
                .And(image_with_indices.select('NDVI').lt(0.3)))
        
        # מים - MNDWI גבוה
        water = image_with_indices.select('MNDWI').gt(0.3)
        
        # יצירת מפת סיווג
        classification = (ee.Image(0)  # רקע
                         .where(agriculture, 1)  # חקלאות
                         .where(urban, 2)        # עירוני
                         .where(forest, 3)       # יער
                         .where(water, 4))       # מים
        
        return classification.rename('classification')
        
    except Exception as e:
        print(f"❌ Error in land use classification: {e}")
        return None

def get_classification_stats(classification: ee.Image, 
                           geometry: ee.Geometry) -> Dict:
    """
    חישוב סטטיסטיקות של הסיווג
    """
    try:
        # חישוב שטח כל קטגוריה
        pixel_count = classification.reduceRegion(
            reducer=ee.Reducer.frequencyHistogram(),
            geometry=geometry,
            scale=config.EE_SCALE,
            maxPixels=config.EE_MAX_PIXELS
        )
        
        return pixel_count.getInfo()
        
    except Exception as e:
        print(f"❌ Error calculating classification stats: {e}")
        return {}

def export_classification(classification: ee.Image, 
                         geometry: ee.Geometry,
                         filename: str) -> str:
    """
    ייצוא תוצאות הסיווג
    """
    try:
        # יצירת משימת ייצוא
        task = ee.batch.Export.image.toDrive(
            image=classification,
            description=filename,
            folder='earth_engine_exports',
            region=geometry,
            scale=config.EE_SCALE,
            crs='EPSG:4326',
            maxPixels=config.EE_MAX_PIXELS
        )
        
        task.start()
        return f"Export task started: {filename}"
        
    except Exception as e:
        print(f"❌ Error exporting classification: {e}")
        return f"Export failed: {e}" 