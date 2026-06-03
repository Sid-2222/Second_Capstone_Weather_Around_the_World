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

                weather_title = image.get_attribute("title")


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

    print(df.tail())
    
    print("\nChecking for empty cells:\n")
    print(df.isnull().sum())
    print("check duplicate values")
    print(df.duplicated().sum())
    df.dropna(inplace=True)
    df.sort_values(by="city", inplace=True)
    df.reset_index(drop=True, inplace=True)
    print(df.tail())
    
    df.to_csv("weather_data.csv", index=False)
    
    with sqlite3.connect("weather.db") as conn:
        print("Database connected successfully.")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather (
                city TEXT,
                country TEXT,
                time TEXT,
                temperature TEXT,
                weather TEXT,
                image TEXT
            )""")
        df.to_sql("weather", conn, if_exists="replace", index=False)
        
    
         
    
    

    input("Press Enter to close browser...")

except Exception as e:
    print("couldn't get the web page")
    print(f"Exception: {type(e).__name__} {e}")

finally:
    driver.quit()