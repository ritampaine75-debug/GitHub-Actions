import os
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
URL = "https://krishakbandhu.wb.gov.in/agricultural-labour/farmer_search"
SEARCH_IDS = ["8192 5751 6764", "819257516764"]
SENDER_EMAIL = os.environ.get('EMAIL_USER')
SENDER_PASS = os.environ.get('EMAIL_PASS')
RECEIVER_EMAIL = "manasipaine@gmail.com" # Example or your actual email

def get_farmer_data():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    results = []

    try:
        for search_id in SEARCH_IDS:
            driver.get(URL)
            # Find input and search button (IDs may vary based on site HTML)
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "voter_id")) 
            )
            search_box.send_keys(search_id)
            
            search_btn = driver.find_element(By.ID, "btnSearch")
            search_btn.click()
            
            # Capture result text
            try:
                result_text = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
                ).text
            except:
                result_text = "No record found for ID: " + search_id
            
            results.append(f"ID: {search_id}\nResult: {result_text}\n" + "-"*30)
            
    finally:
        driver.quit()
    
    return "\n\n".join(results)

def send_email(content):
    msg = EmailMessage()
    msg.set_content(f"Hello,\n\nHere is your daily Krishak Bandhu search report:\n\n{content}\n\nRegards,\nAutomation Bot")
    msg['Subject'] = "Daily Agricultural Labour Search Report"
    msg['From'] = SENDER_EMAIL
    msg['To'] = SENDER_EMAIL # Sending to yourself

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASS)
        smtp.send_message(msg)

if __name__ == "__main__":
    report = get_farmer_data()
    send_email(report)
  
