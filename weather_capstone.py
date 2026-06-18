from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import sqlite3

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000) 
pd.set_option("display.expand_frame_repr", False)

options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920x1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://www.timeanddate.com/weather/"

try:
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.zebra"))
    )

    weather_data = []

    rows = driver.find_elements(By.CSS_SELECTOR, "table.zebra tbody tr")

    for row in rows:
        table_cells  = row.find_elements(By.TAG_NAME, "td")

        for i in range(0, len(table_cells ), 4):
            source = ""  
            weather_title = ""
            try:
                city_element  = table_cells [i].find_element(By.TAG_NAME, "a")
                city = city_element.text.strip()
                href = city_element.get_attribute("href")
                parts = href.split("/")
                country = parts[4] if len(parts) > 4 else ""
            except:
                city = ""
                country = ""

            try:
                time = table_cells [i + 1].text.strip()
            except:
                time = ""

            try:
                temp = table_cells [i + 3].text.strip()
            except:
                temp = ""

            try:
                image = table_cells [i + 2].find_element(By.TAG_NAME, "img")
                source = image.get_attribute("src")
                weather_title = image.get_attribute("title")
                if source.startswith("//"):
                    source = "https:" + source


            except:
                image = ""
                weather_title = ""

    
            if city:
                weather_data.append({
                    "city": city,
                    "country": country,
                    "time": time,
                    "temperature": temp,
                    "weather": weather_title,
                    "image": source
                })

    df = pd.DataFrame(weather_data)
    
    print("BEFORE CLEANING:")
    print(df.head())
    print(df.shape)  
    
    print("\nBEFORE CLEANING DUPLICATES:")
    print(df.duplicated().sum())
    
    df_clean = df.dropna() 
    df_clean = df_clean.drop_duplicates() 
    
    df_clean["temperature_num"] = df_clean["temperature"].str.extract(r"(\d+)").astype(float)
    
    print("\nTRANSFORMATION CHECK:")
    print(df_clean[["temperature", "temperature_num"]].head())
    
    df_clean = df_clean.sort_values(by="city")
    df_clean.reset_index(drop=True, inplace=True)
    
    print("\nAFTER CLEANING:")
    print(df_clean.head())
    print(df_clean.shape)
    
    print("\nChecking for missing values:")
    print(df_clean.isnull().sum())
    
    print("check duplicate values")
    print(df_clean.duplicated().sum())
    
    warm_cities = df_clean[df_clean["temperature_num"] > 70]
    print("\nCities above 70 degrees:")
    print(warm_cities[["city", "temperature_num"]].head())
    
    df_clean.to_csv("weather_data.csv", index=False)
    
    df_locations = df_clean[["city", "country"]]
    df_locations.to_csv("locations.csv", index=False)
    
    df_weather_conditions = df_clean[["city", "weather", "image"]]
    df_weather_conditions.to_csv("weather_conditions.csv", index=False)
    
    df_time_temp = df_clean[["city", "time", "temperature", "temperature_num"]]
    df_time_temp.to_csv("time_temperature.csv", index=False)
    
    with sqlite3.connect("weather.db") as conn:
        print("Database connected successfully.")
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                city TEXT,
                country TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_conditions (
                city TEXT,
                weather TEXT,
                image TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_temperature (
                city TEXT,
                time TEXT,
                temperature TEXT,
                temperature_num REAL
            )
        """)
        conn.commit()
        df_locations.to_sql("locations", conn, if_exists="replace", index=False)
        df_weather_conditions.to_sql("weather_conditions", conn, if_exists="replace", index=False)
        df_time_temp.to_sql("time_temperature", conn, if_exists="replace", index=False)
        print("Data successfully saved to SQLite database.")       
    
    
    

    input("Press Enter to close browser...")

except Exception as e:
    print("couldn't get the web page")
    print(f"Exception: {type(e).__name__} {e}")

finally:
    driver.quit()