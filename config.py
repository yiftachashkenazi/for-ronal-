# הגדרות מערכת סיווג שטח
import os

# Google Earth Engine Configuration
EE_SERVICE_ACCOUNT = os.environ.get('EE_SERVICE_ACCOUNT', None)
EE_PRIVATE_KEY_FILE = os.environ.get('EE_PRIVATE_KEY_FILE', None)

# הגדרות סיווג
LAND_USE_CLASSES = {
    'agricultural': {'name': 'חקלאי', 'color': '#90EE90', 'id': 1},
    'urban': {'name': 'עירוני', 'color': '#FF6B6B', 'id': 2}, 
    'forest': {'name': 'יער', 'color': '#228B22', 'id': 3},
    'water': {'name': 'מים', 'color': '#4169E1', 'id': 4},
    'other': {'name': 'אחר', 'color': '#D3D3D3', 'id': 0}
}

# הגדרות מפה
DEFAULT_MAP_CENTER = [31.5, 34.8]  # ישראל
DEFAULT_ZOOM = 8

# הגדרות עיבוד תמונה
MAX_IMAGE_SIZE = 5000  # פיקסלים
SUPPORTED_FORMATS = ['jpg', 'jpeg', 'png', 'tif', 'tiff']

# הגדרות Earth Engine
EE_MAX_PIXELS = 1e8
EE_SCALE = 30  # מטרים לפיקסל

# הגדרות לוויין
SATELLITE_COLLECTIONS = {
    'sentinel2': 'COPERNICUS/S2_SR',
    'landsat8': 'LANDSAT/LC08/C02/T1_L2',
    'landsat9': 'LANDSAT/LC09/C02/T1_L2'
}

# הגדרות מודל
MODEL_BANDS = ['B2', 'B3', 'B4', 'B8', 'B11', 'B12']  # Sentinel-2
NDVI_THRESHOLD = 0.3
NDBI_THRESHOLD = 0.1 