import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from PIL import Image
import tempfile
import os
from datetime import datetime, timedelta
import sys

# הוספת הנתיב למודולים מקומיים
sys.path.append('.')
sys.path.append('./utils')

try:
    import config
    from utils.earth_engine_utils import *
    from utils.image_processing import *
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# הגדרת עמוד
st.set_page_config(
    page_title="מערכת סיווג שטח - Google Earth Engine",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# כותרת ראשית
st.title("🌍 מערכת סיווג שטח באמצעות Google Earth Engine")
st.markdown("---")

# בר צד עם הגדרות
with st.sidebar:
    st.header("⚙️ הגדרות")
    
    # בחירת מצב עבודה
    analysis_mode = st.radio(
        "בחר מצב ניתוח:",
        ["תמונה מקומית", "Google Earth Engine", "מפה אינטראקטיבית"],
        help="בחר איך תרצה לנתח את השטח"
    )
    
    st.markdown("---")
    
    # הגדרות נוספות
    if analysis_mode == "Google Earth Engine":
        st.subheader("🛰️ הגדרות לוויין")
        satellite = st.selectbox(
            "בחר לוויין:",
            ["sentinel2", "landsat8", "landsat9"],
            help="סוג הלוויין לניתוח"
        )
        
        date_range = st.date_input(
            "טווח תאריכים:",
            value=[datetime.now() - timedelta(days=30), datetime.now()],
            help="טווח התאריכים לחיפוש תמונות"
        )
        
        cloud_cover = st.slider(
            "כיסוי עננים מקסימלי (%):",
            0, 100, 20,
            help="אחוז כיסוי עננים מקסימלי מותר"
        )

# אזור תוכן ראשי
if analysis_mode == "תמונה מקומית":
    st.header("📁 ניתוח תמונה מקומית")
    
    # העלאת קובץ
    uploaded_file = st.file_uploader(
        "העלה תמונה לניתוח:",
        type=['jpg', 'jpeg', 'png', 'tif', 'tiff'],
        help="תמונה צריכה להיות תצלום אוויר או תמונת לוויין"
    )
    
    if uploaded_file is not None:
        # שמירת הקובץ זמנית
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name
        
        try:
            # טעינת התמונה
            with st.spinner("טוען תמונה..."):
                image = load_image(tmp_file_path)
            
            if image is not None:
                # הצגת התמונה המקורית
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🖼️ תמונה מקורית")
                    st.image(image, caption="תמונה מקורית", use_column_width=True)
                
                # כפתור לניתוח
                if st.button("🔍 התחל ניתוח", type="primary"):
                    with st.spinner("מבצע ניתוח סיווג..."):
                        # שינוי גודל אם נדרש
                        processed_image = resize_image(image)
                        
                        # סיווג התמונה
                        classification = classify_rgb_image(processed_image)
                        
                        # יצירת שכבת צבעים
                        overlay = create_classification_overlay(processed_image, classification, alpha=0.6)
                        
                        with col2:
                            st.subheader("🎨 תוצאות סיווג")
                            st.image(overlay, caption="סיווג שטח", use_column_width=True)
                        
                        # סטטיסטיקות
                        st.subheader("📊 סטטיסטיקות")
                        stats = get_rgb_classification_stats(classification)
                        
                        # יצירת DataFrame לתצוגה
                        stats_df = pd.DataFrame.from_dict(stats, orient='index')
                        if not stats_df.empty:
                            st.dataframe(stats_df, use_container_width=True)
                            
                            # גרף עוגה
                            fig_pie = px.pie(
                                values=stats_df['percentage'],
                                names=[config.LAND_USE_CLASSES.get(idx, {}).get('name', idx) for idx in stats_df.index],
                                title="התפלגות שימושי קרקע (%)",
                                color_discrete_map={
                                    config.LAND_USE_CLASSES.get(idx, {}).get('name', idx): 
                                    config.LAND_USE_CLASSES.get(idx, {}).get('color', '#888888')
                                    for idx in stats_df.index
                                }
                            )
                            st.plotly_chart(fig_pie, use_container_width=True)
                            
                            # גרף עמודות
                            fig_bar = px.bar(
                                x=[config.LAND_USE_CLASSES.get(idx, {}).get('name', idx) for idx in stats_df.index],
                                y=stats_df['percentage'],
                                title="שיעור שימושי קרקע",
                                labels={'x': 'סוג שטח', 'y': 'אחוז (%)'},
                                color=[config.LAND_USE_CLASSES.get(idx, {}).get('name', idx) for idx in stats_df.index],
                                color_discrete_map={
                                    config.LAND_USE_CLASSES.get(idx, {}).get('name', idx): 
                                    config.LAND_USE_CLASSES.get(idx, {}).get('color', '#888888')
                                    for idx in stats_df.index
                                }
                            )
                            st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.error("❌ לא ניתן לטעון את התמונה. בדוק שהקובץ תקין.")
                
        except Exception as e:
            st.error(f"❌ שגיאה בעיבוד התמונה: {e}")
        
        finally:
            # מחיקת קובץ זמני
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

elif analysis_mode == "Google Earth Engine":
    st.header("🛰️ ניתוח Google Earth Engine")
    
    # בדיקת אתחול Earth Engine
    if 'ee_initialized' not in st.session_state:
        with st.spinner("מאתחל Google Earth Engine..."):
            success = initialize_ee()
            st.session_state.ee_initialized = success
    
    if st.session_state.ee_initialized:
        st.success("✅ Google Earth Engine מאותחל בהצלחה")
        
        # כלים לבחירת אזור
        st.subheader("📍 בחירת אזור")
        
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("קו רוחב:", value=31.5, format="%.6f")
            lng = st.number_input("קו אורך:", value=34.8, format="%.6f")
        
        with col2:
            buffer_km = st.slider("רדיוס באזור (ק\"מ):", 1, 50, 10)
        
        if st.button("🔍 נתח אזור", type="primary"):
            # חישוב גבולות האזור
            buffer_deg = buffer_km / 111.0  # המרה גסה לדרגות
            bounds = [lng - buffer_deg, lat - buffer_deg, lng + buffer_deg, lat + buffer_deg]
            
            try:
                with st.spinner("מוריד תמונות לוויין..."):
                    date_start = date_range[0].strftime('%Y-%m-%d')
                    date_end = date_range[1].strftime('%Y-%m-%d')
                    
                    # קבלת תמונת לוויין
                    satellite_image = get_satellite_image(bounds, date_start, date_end, satellite)
                
                if satellite_image:
                    with st.spinner("מבצע סיווג..."):
                        # סיווג השטח
                        classification = classify_land_use(satellite_image)
                        
                        if classification:
                            # חישוב סטטיסטיקות
                            geometry = ee.Geometry.Rectangle(bounds)
                            stats = get_classification_stats(classification, geometry)
                            
                            st.success("✅ הניתוח הושלם בהצלחה!")
                            
                            # הצגת תוצאות
                            if stats:
                                st.subheader("📊 תוצאות ניתוח")
                                st.json(stats)
                        else:
                            st.error("❌ שגיאה בסיווג השטח")
                else:
                    st.error("❌ לא נמצאו תמונות לוויין עבור האזור והתאריכים שנבחרו")
                    
            except Exception as e:
                st.error(f"❌ שגיאה בניתוח: {e}")
    else:
        st.error("❌ לא ניתן לאתחל את Google Earth Engine. בדוק את האימות.")
        st.info("💡 הפעל את הפקודה: `earthengine authenticate` בטרמינל")

elif analysis_mode == "מפה אינטראקטיבית":
    st.header("🗺️ מפה אינטראקטיבית")
    
    # יצירת מפה
    m = folium.Map(
        location=config.DEFAULT_MAP_CENTER,
        zoom_start=config.DEFAULT_ZOOM,
        tiles='Esri.WorldImagery'
    )
    
    # הוספת שכבת OpenStreetMap
    folium.TileLayer('OpenStreetMap').add_to(m)
    
    # יצירת קבוצת שכבות
    feature_group = folium.FeatureGroup(name='Areas of Interest')
    m.add_child(feature_group)
    
    # הוספת בקרת שכבות
    folium.LayerControl().add_to(m)
    
    # הצגת המפה
    map_data = st_folium(m, width=700, height=500)
    
    # מידע על הקליקים
    if map_data['last_clicked']:
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lng = map_data['last_clicked']['lng']
        
        st.info(f"📍 נקודה נבחרה: {clicked_lat:.6f}, {clicked_lng:.6f}")
        
        if st.button("🔍 נתח את האזור הנבחר", type="primary"):
            st.info("🚧 ניתוח מפות אינטראקטיביות יוטמע בגרסה הבאה")

# כותרת תחתונה
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        🌍 מערכת סיווג שטח באמצעות Google Earth Engine<br>
        נבנה עם ❤️ בעזרת Streamlit ו-Python
    </div>
    """, 
    unsafe_allow_html=True
) 