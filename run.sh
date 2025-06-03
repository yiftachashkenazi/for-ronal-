#!/bin/bash

echo "🌍 מפעיל מערכת סיווג שטח"
echo "============================="

# בדיקה שהסביבה הוירטואלית קיימת
if [ ! -d "venv" ]; then
    echo "❌ סביבה וירטואלית לא נמצאה"
    echo "💡 הפעל תחילה: ./install.sh"
    exit 1
fi

# הפעלת הסביבה הוירטואלית
echo "📦 מפעיל סביבה וירטואלית..."
source venv/bin/activate

# בדיקת Google Earth Engine
echo "🔍 בודק Google Earth Engine..."
if ! earthengine --version > /dev/null 2>&1; then
    echo "⚠️  Google Earth Engine לא מאותחל"
    echo "💡 הפעל: earthengine authenticate"
fi

# הפעלת האפליקציה
echo "🚀 מפעיל את המערכת..."
echo "📱 האפליקציה תיפתח בדפדפן בכתובת: http://localhost:8501"
echo ""

streamlit run app.py 