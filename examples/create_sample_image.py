#!/usr/bin/env python3
"""
יוצר תמונת דוגמה לבדיקת המערכת
תמונה סינתטית עם אזורים שונים לבדיקת הסיווג
"""

import numpy as np
import cv2
from PIL import Image, ImageDraw
import os

def create_sample_image(width=800, height=600, filename="sample_aerial.jpg"):
    """
    יוצר תמונת דוגמה עם אזורים שונים
    """
    # יצירת תמונה ריקה
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # רקע כחול שמיים
    image[:, :] = [135, 206, 235]  # sky blue
    
    # יער (ירוק כהה) - חלק עליון שמאל
    forest_color = [34, 139, 34]  # forest green
    image[0:height//3, 0:width//2] = forest_color
    
    # הוספת מרקם ליער
    for i in range(50):
        x = np.random.randint(0, width//2)
        y = np.random.randint(0, height//3)
        radius = np.random.randint(5, 15)
        dark_green = [20, 100, 20]
        cv2.circle(image, (x, y), radius, dark_green, -1)
    
    # שטח חקלאי (ירוק בהיר) - חלק תחתון שמאל
    agriculture_color = [144, 238, 144]  # light green
    image[height//3:height, 0:width//2] = agriculture_color
    
    # הוספת קווי שדות
    for i in range(height//3, height, 30):
        cv2.line(image, (0, i), (width//2, i), [120, 200, 120], 2)
    for i in range(0, width//2, 40):
        cv2.line(image, (i, height//3), (i, height), [120, 200, 120], 2)
    
    # אזור עירוני (אפור) - חלק עליון ימין
    urban_color = [169, 169, 169]  # gray
    image[0:height//2, width//2:width] = urban_color
    
    # הוספת בניינים (ריבועים כהים)
    for i in range(10):
        x = np.random.randint(width//2 + 10, width - 30)
        y = np.random.randint(10, height//2 - 30)
        w = np.random.randint(15, 30)
        h = np.random.randint(20, 40)
        building_color = [105, 105, 105]  # dim gray
        cv2.rectangle(image, (x, y), (x + w, y + h), building_color, -1)
    
    # הוספת כבישים
    cv2.line(image, (width//2, 0), (width//2, height//2), [64, 64, 64], 8)
    cv2.line(image, (width//2, height//4), (width, height//4), [64, 64, 64], 6)
    
    # אזור מים (כחול) - חלק תחתון ימין
    water_color = [65, 105, 225]  # royal blue
    image[height//2:height, width//2:width] = water_color
    
    # הוספת אפקט גלים
    for i in range(height//2, height, 5):
        for j in range(width//2, width, 10):
            if (i + j) % 20 < 10:
                image[i:i+2, j:j+5] = [70, 130, 180]  # steel blue
    
    # שמירת התמונה
    output_path = os.path.join("examples", filename)
    cv2.imwrite(output_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    
    print(f"✅ תמונת דוגמה נוצרה: {output_path}")
    print(f"📏 גודל: {width}x{height} פיקסלים")
    print(f"🎨 מכילה: יער, חקלאות, עירוני, מים")
    
    return output_path

def create_real_sample():
    """
    יוצר תמונה דמוית תצלום אוויר אמיתי
    """
    width, height = 1024, 768
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # רקע טבעי
    image[:, :] = [245, 245, 220]  # beige
    
    # יצירת נוף הררי עם יערות
    for y in range(height):
        for x in range(width):
            # הוספת רעש טבעי
            noise = np.random.randint(-20, 20)
            
            # יער בהרים
            if y < height * 0.4:
                base_color = [34, 139, 34]  # forest green
                variation = np.random.randint(-30, 30)
                for i in range(3):
                    image[y, x, i] = np.clip(base_color[i] + variation + noise, 0, 255)
            
            # עמק חקלאי
            elif y < height * 0.7:
                base_color = [154, 205, 50]  # yellow green
                variation = np.random.randint(-40, 40)
                for i in range(3):
                    image[y, x, i] = np.clip(base_color[i] + variation + noise, 0, 255)
            
            # אזור מעורב
            else:
                if x < width * 0.6:
                    # המשך חקלאות
                    base_color = [173, 255, 47]  # green yellow
                else:
                    # התחלת עיור
                    base_color = [192, 192, 192]  # silver
                
                variation = np.random.randint(-30, 30)
                for i in range(3):
                    image[y, x, i] = np.clip(base_color[i] + variation + noise, 0, 255)
    
    # הוספת כבישים
    cv2.line(image, (0, height//2), (width, height//2), [64, 64, 64], 8)
    cv2.line(image, (width//3, 0), (width//3, height), [64, 64, 64], 6)
    
    # הוספת נהר
    points = []
    for i in range(0, width, 20):
        y_river = int(height * 0.8 + 30 * np.sin(i * 0.02))
        points.append([i, y_river])
    
    points = np.array(points, np.int32)
    cv2.polylines(image, [points], False, [65, 105, 225], 15)
    
    # שמירה
    output_path = os.path.join("examples", "realistic_aerial.jpg")
    cv2.imwrite(output_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    
    print(f"✅ תמונה ריאליסטית נוצרה: {output_path}")
    
    return output_path

def main():
    """יוצר כמה תמונות דוגמה"""
    os.makedirs("examples", exist_ok=True)
    
    print("🎨 יוצר תמונות דוגמה...")
    
    # תמונה פשוטה לבדיקה בסיסית
    create_sample_image(800, 600, "simple_test.jpg")
    
    # תמונה מורכבת יותר
    create_sample_image(1200, 900, "complex_test.jpg")
    
    # תמונה ריאליסטית
    create_real_sample()
    
    print("\n🎉 כל התמונות נוצרו בהצלחה!")
    print("📁 ניתן למצוא אותן בתיקיית examples/")
    print("💡 השתמש בהן לבדיקת המערכת")

if __name__ == "__main__":
    main() 