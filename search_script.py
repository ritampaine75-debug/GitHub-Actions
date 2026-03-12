import os
import smtplib
import time
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
URL = "https://krishakbandhu.wb.gov.in/agricultural-labour/farmer_search"
SEARCH_IDS = ["8192 5751 6764", "819257516764"] # Put your actual IDs here
SENDER_EMAIL = os.environ.get('EMAIL_USER')
SENDER_PASS = os.environ.get('EMAIL_PASS')

def get_farmer_data():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    results = []

    try:
        for search_id in SEARCH_IDS:
            driver.get(URL)
            time.sleep(5)
            try:
                # Try to find the voter input field
                search_box = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "voter_id"))
                )
                search_box.clear()
                search_box.send_keys(search_id)
                
                # Try to click search button
                search_btn = driver.find_element(By.ID, "btnSearch")
                search_btn.click()
                time.sleep(5)
                
                page_text = driver.find_element(By.TAG_NAME, "body").text
                if "No Record Found" in page_text:
                    status = "No Record Found"
                else:
                    status = "Record Found! Check Website."
                    
            except Exception as e:
                # This prints the error in GitHub actions so you know if it's a Captcha or IP block
                print(f"Failed for {search_id}. Reason: {str(e)}")
                status = "Error: Element not found, IP blocked, or Captcha appeared."
            
            results.append(f"ID: {search_id} | Result: {status}")
            
    finally:
        driver.quit()
    return "\n".join(results)

def send_email(content):
    if not SENDER_EMAIL or not SENDER_PASS:
        print("Email credentials missing. Cannot send email.")
        return
        
    msg = EmailMessage()
    msg.set_content(f"Daily Report:\n\n{content}")
    msg['Subject'] = "Krishak Bandhu Report"
    msg['From'] = SENDER_EMAIL
    msg['To'] = SENDER_EMAIL # Sends the email to yourself
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASS)
            smtp.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

if __name__ == "__main__":
    print("Starting Krishak Bandhu Bot...")
    data = get_farmer_data()
    print("\nResults collected:\n", data)
    send_email(data)
    print("Process Complete.")
