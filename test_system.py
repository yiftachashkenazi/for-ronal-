#!/usr/bin/env python3
"""
קובץ בדיקה למערכת סיווג שטח
בודק שכל המודולים פועלים כהלכה
"""

import sys
import traceback

def test_imports():
    """בדיקת ייבוא מודולים"""
    print("🧪 בודק ייבוא מודולים...")
    
    try:
        import streamlit as st
        print("✅ Streamlit")
    except Exception as e:
        print(f"❌ Streamlit: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy")
    except Exception as e:
        print(f"❌ NumPy: {e}")
        return False
    
    try:
        import cv2
        print("✅ OpenCV")
    except Exception as e:
        print(f"❌ OpenCV: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ Plotly")
    except Exception as e:
        print(f"❌ Plotly: {e}")
        return False
    
    try:
        import folium
        print("✅ Folium")
    except Exception as e:
        print(f"❌ Folium: {e}")
        return False
    
    try:
        import ee
        print("✅ Google Earth Engine API")
    except Exception as e:
        print(f"❌ Google Earth Engine API: {e}")
        return False
    
    return True

def test_config():
    """בדיקת קובץ הגדרות"""
    print("\n⚙️  בודק קובץ הגדרות...")
    
    try:
        import config
        print("✅ Config loaded")
        
        # בדיקת הגדרות חיוניות
        assert hasattr(config, 'LAND_USE_CLASSES'), "LAND_USE_CLASSES missing"
        assert hasattr(config, 'DEFAULT_MAP_CENTER'), "DEFAULT_MAP_CENTER missing"
        assert hasattr(config, 'SATELLITE_COLLECTIONS'), "SATELLITE_COLLECTIONS missing"
        
        print("✅ כל ההגדרות נמצאות")
        return True
        
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_utils():
    """בדיקת מודולי עזר"""
    print("\n🛠️  בודק מודולי עזר...")
    
    try:
        sys.path.append('./utils')
        from utils.image_processing import load_image, resize_image
        print("✅ Image processing module")
    except Exception as e:
        print(f"❌ Image processing: {e}")
        return False
    
    try:
        from utils.earth_engine_utils import initialize_ee
        print("✅ Earth Engine utils module")
    except Exception as e:
        print(f"❌ Earth Engine utils: {e}")
        return False
    
    return True

def test_earth_engine():
    """בדיקת אתחול Google Earth Engine"""
    print("\n🛰️  בודק Google Earth Engine...")
    
    try:
        sys.path.append('./utils')
        from utils.earth_engine_utils import initialize_ee
        
        # ניסיון אתחול (ללא אימות)
        success = initialize_ee()
        
        if success:
            print("✅ Earth Engine initialized successfully")
        else:
            print("⚠️  Earth Engine not authenticated (run 'earthengine authenticate')")
        
        return True
        
    except Exception as e:
        print(f"❌ Earth Engine error: {e}")
        return False

def main():
    """הפעלת כל הבדיקות"""
    print("🌍 בדיקת מערכת סיווג שטח")
    print("=" * 40)
    
    tests = [
        ("Import Tests", test_imports),
        ("Config Tests", test_config), 
        ("Utils Tests", test_utils),
        ("Earth Engine Tests", test_earth_engine)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("📊 תוצאות בדיקה:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ עבר" if passed else "❌ נכשל"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 כל הבדיקות עברו בהצלחה!")
        print("להפעלת המערכת: streamlit run app.py")
    else:
        print("⚠️  יש בעיות שדורשות תיקון")
        print("בדוק את התלויות והגדרות")

if __name__ == "__main__":
    main() 