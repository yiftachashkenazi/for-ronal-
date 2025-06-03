#!/bin/bash

echo "🌍 מתקין מערכת סיווג שטח - Google Earth Engine"
echo "================================================"

# בדיקת Python
echo "📋 בדיקת Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python לא מותקן. אנא התקן Python 3.8 ומעלה"
    exit 1
fi

echo "✅ Python נמצא: $(python3 --version)"

# יצירת סביבה וירטואלית
echo "📦 יוצר סביבה וירטואלית..."
python3 -m venv venv
source venv/bin/activate

# שדרוג pip
echo "⬆️  משדרג pip..."
pip install --upgrade pip

# התקנת חבילות חיוניות
echo "📚 מתקין חבילות חיוניות..."
pip install streamlit earthengine-api

echo "📚 מתקין חבילות נוספות..."
pip install pillow numpy matplotlib plotly folium streamlit-folium opencv-python-headless

# אימות Google Earth Engine  
echo "🔐 מגדיר Google Earth Engine..."
echo "אנא הפעל את הפקודה הבאה לאימות:"
echo "earthengine authenticate"

echo ""
echo "✅ ההתקנה הושלמה!"
echo "להפעלת המערכת:"
echo "1. source venv/bin/activate"
echo "2. earthengine authenticate"
echo "3. streamlit run app.py" 