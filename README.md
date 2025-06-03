# מערכת סיווג שטח באמצעות Google Earth Engine

## תיאור הפרויקט
מערכת לסיווג תצלומי אוויר לקטגוריות שונות של שימושי קרקע:
- שטח חקלאי
- שטח עירוני  
- יער

המערכת משתמשת בGoogle Earth Engine לעיבוד תמונות לוויין ובאלגוריתמי machine learning לסיווג.

## התקנה

### 1. התקנת Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. הגדרת Google Earth Engine
```bash
# התקנת Earth Engine CLI
pip install earthengine-api

# אימות (יפתח דפדפן לאימות)
earthengine authenticate

# אתחול
earthengine --version
```

### 3. הגדרת Google Cloud (אופציונלי לשמירת תוצאות)
- צור פרויקט ב-Google Cloud Console
- הפעל את Earth Engine API
- צור Service Account Key
- שמור את הקובץ JSON במיקום מאובטח

## הפעלה

```bash
streamlit run app.py
```

## שימוש במערכת

1. העלה תמונת לוויין או תצלום אוויר
2. בחר אזור עניין על המפה
3. הפעל ניתוח סיווג
4. צפה בתוצאות האינטראקטיביות

## תכונות

- ✅ העלאת תמונות מקומיות
- ✅ בחירת אזור על מפה אינטראקטיבית
- ✅ סיווג אוטומטי לשטח חקלאי/עירוני/יער
- ✅ ויזואליזציה אינטראקטיבית של התוצאות
- ✅ ייצוא תוצאות לקבצים
- ✅ סטטיסטיקות מפורטות

## טכנולוגיות
- Google Earth Engine
- Streamlit
- Python
- OpenCV
- Folium (מפות)
- Plotly (גרפים) # for-ronal-
