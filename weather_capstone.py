from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

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

    # ✅ FIX: iterate row by row
    rows = driver.find_elements(By.CSS_SELECTOR, "table.zebra tbody tr")

    for row in rows:
        tds = row.find_elements(By.TAG_NAME, "td")

        # each city = 4 columns (city, time, icon, temp)
        for i in range(0, len(tds), 4):

            try:
                city = tds[i].find_element(By.TAG_NAME, "a").text.strip()
            except:
                city = ""

            try:
                time = tds[i + 1].text.strip()
            except:
                time = ""

            try:
                temp = tds[i + 3].text.strip()
            except:
                temp = ""

            try:
                image = tds[i + 2].find_element(By.TAG_NAME, "img").get_attribute("src")
            except:
                image = ""

            # stop empty blocks (important for last incomplete row like Nairobi)
            if city:
                weather_data.append({
                    "city": city,
                    "time": time,
                    "temperature": temp,
                    "image": image
                })

    df = pd.DataFrame(weather_data)

    print(df)

    df.to_csv("weather_data.csv", index=False)

    input("Press Enter to close browser...")

except Exception as e:
    print("couldn't get the web page")
    print(f"Exception: {type(e).__name__} {e}")

finally:
    driver.quit()