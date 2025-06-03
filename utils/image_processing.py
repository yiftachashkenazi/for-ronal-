"""
מודול עיבוד תמונות מקומיות
עיבוד תמונות שהועלו על ידי המשתמש
"""

import cv2
import numpy as np
from PIL import Image
import rasterio
from typing import Tuple, Optional, Dict
import config

def load_image(file_path: str) -> Optional[np.ndarray]:
    """
    טעינת תמונה מקובץ
    """
    try:
        # בדיקת סוג הקובץ
        file_ext = file_path.lower().split('.')[-1]
        
        if file_ext in ['tif', 'tiff']:
            # קובץ GeoTIFF
            with rasterio.open(file_path) as src:
                image = src.read()
                # המרה לפורמט numpy standard
                if len(image.shape) == 3:
                    image = np.transpose(image, (1, 2, 0))
                return image
        else:
            # קובץ תמונה רגיל
            image = cv2.imread(file_path)
            if image is not None:
                # המרה מ-BGR ל-RGB
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                return image
        
        return None
        
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        return None

def resize_image(image: np.ndarray, max_size: int = None) -> np.ndarray:
    """
    שינוי גודל תמונה
    """
    if max_size is None:
        max_size = config.MAX_IMAGE_SIZE
        
    height, width = image.shape[:2]
    
    # בדיקה אם נדרש שינוי גודל
    if max(height, width) <= max_size:
        return image
    
    # חישוב גודל חדש תוך שמירה על יחס גובה-רוחב
    if height > width:
        new_height = max_size
        new_width = int(width * (max_size / height))
    else:
        new_width = max_size
        new_height = int(height * (max_size / width))
    
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return resized

def calculate_image_indices(image: np.ndarray) -> Dict[str, np.ndarray]:
    """
    חישוב אינדקסים ספקטרליים מתמונה רגילה (RGB)
    """
    try:
        # הפרדת ערוצי צבע
        if len(image.shape) == 3:
            r = image[:, :, 0].astype(np.float32)
            g = image[:, :, 1].astype(np.float32)
            b = image[:, :, 2].astype(np.float32)
        else:
            # תמונה אפורה
            r = g = b = image.astype(np.float32)
        
        # מניעת חלוקה באפס
        epsilon = 1e-8
        
        # חישוב אינדקסים מבוססי RGB
        # Green-Red Vegetation Index (GRVI)
        grvi = np.where((g + r) > epsilon, (g - r) / (g + r + epsilon), 0)
        
        # Visible Atmospherically Resistant Index (VARI)
        vari = np.where((g + r - b) > epsilon, (g - r) / (g + r - b + epsilon), 0)
        
        # Excess Green Index (ExG)
        exg = 2 * g - r - b
        
        # Triangular Greenness Index (TGI)
        tgi = g - 0.39 * r - 0.61 * b
        
        return {
            'grvi': grvi,
            'vari': vari,
            'exg': exg,
            'tgi': tgi,
            'r': r, 'g': g, 'b': b
        }
        
    except Exception as e:
        print(f"❌ Error calculating image indices: {e}")
        return {}

def classify_rgb_image(image: np.ndarray) -> np.ndarray:
    """
    סיווג תמונה RGB לקטגוריות שימוש בקרקע
    """
    try:
        indices = calculate_image_indices(image)
        
        if not indices:
            return np.zeros(image.shape[:2], dtype=np.uint8)
        
        height, width = image.shape[:2]
        classification = np.zeros((height, width), dtype=np.uint8)
        
        # חישוב HSV לזיהוי צבעים טוב יותר
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
        
        # יער - צבע ירוק כהה, GRVI גבוה
        forest_mask = (
            (indices['grvi'] > 0.1) & 
            (indices['tgi'] > 10) &
            (h >= 40) & (h <= 80) &  # גוון ירוק
            (s > 50) & (v > 30)
        )
        
        # חקלאות - צבע ירוק בהיר, GRVI בינוני
        agriculture_mask = (
            (indices['grvi'] > 0.05) & (indices['grvi'] <= 0.1) &
            (indices['exg'] > 0) &
            (h >= 30) & (h <= 90) &  # גוון ירוק-צהוב
            (s > 30) & (v > 40)
        )
        
        # עירוני - צבעים אפורים/בהירים, GRVI נמוך
        urban_mask = (
            (indices['grvi'] < 0.05) &
            (s < 50) &  # רוויה נמוכה
            (v > 60)   # בהירות גבוהה
        )
        
        # מים - צבע כחול
        water_mask = (
            (h >= 100) & (h <= 130) &  # גוון כחול
            (s > 40) & (v > 30)
        )
        
        # החלת הסיווג
        classification[agriculture_mask] = 1  # חקלאות
        classification[urban_mask] = 2        # עירוני
        classification[forest_mask] = 3       # יער
        classification[water_mask] = 4        # מים
        
        return classification
        
    except Exception as e:
        print(f"❌ Error in RGB image classification: {e}")
        return np.zeros(image.shape[:2], dtype=np.uint8)

def get_rgb_classification_stats(classification: np.ndarray) -> Dict:
    """
    חישוב סטטיסטיקות סיווג לתמונה RGB
    """
    try:
        unique, counts = np.unique(classification, return_counts=True)
        total_pixels = classification.size
        
        stats = {}
        for class_id, count in zip(unique, counts):
            percentage = (count / total_pixels) * 100
            
            class_name = 'other'
            for key, value in config.LAND_USE_CLASSES.items():
                if value['id'] == class_id:
                    class_name = key
                    break
            
            stats[class_name] = {
                'pixels': int(count),
                'percentage': round(percentage, 2),
                'area_km2': round((count * 0.0009), 4)  # הערכה גסה
            }
        
        return stats
        
    except Exception as e:
        print(f"❌ Error calculating RGB classification stats: {e}")
        return {}

def create_classification_overlay(image: np.ndarray, 
                                classification: np.ndarray, 
                                alpha: float = 0.5) -> np.ndarray:
    """
    יצירת שכבת סיווג שקופה על התמונה המקורית
    """
    try:
        # יצירת מפת צבעים לסיווג
        height, width = classification.shape
        colored_classification = np.zeros((height, width, 3), dtype=np.uint8)
        
        for class_key, class_info in config.LAND_USE_CLASSES.items():
            mask = classification == class_info['id']
            color = class_info['color']
            
            # המרת צבע מהקס ל-RGB
            color_rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
            colored_classification[mask] = color_rgb
        
        # שילוב התמונה המקורית עם הסיווג
        overlay = cv2.addWeighted(image, 1-alpha, colored_classification, alpha, 0)
        
        return overlay
        
    except Exception as e:
        print(f"❌ Error creating classification overlay: {e}")
        return image 