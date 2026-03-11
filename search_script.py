import os
import smtplib
import time
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# কনফিগারেশন
URL = "https://krishakbandhu.wb.gov.in/agricultural-labour/farmer_search"
SEARCH_IDS = ["8192 5751 6764", "819257516764"]
SENDER_EMAIL = os.environ.get('EMAIL_USER')
SENDER_PASS = os.environ.get('EMAIL_PASS')

def get_farmer_data():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") # নতুন হেডলেস মোড
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # আসল মানুষের মতো দেখানোর জন্য User-Agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    results = []

    try:
        for search_id in SEARCH_IDS:
            driver.get(URL)
            time.sleep(3) # পেজ লোড হওয়ার জন্য সময়
            
            try:
                # ভোটার আইডি ইনপুট বক্স খোঁজা
                search_box = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "voter_id")) 
                )
                search_box.clear()
                search_box.send_keys(search_id)
                
                # সার্চ বাটন ক্লিক
                search_btn = driver.find_element(By.ID, "btnSearch")
                search_btn.click()
                
                time.sleep(5) # রেজাল্ট আসার জন্য অপেক্ষা
                
                # ফলাফল কপি করা
                result_element = driver.find_element(By.TAG_BODY)
                result_text = result_element.text
                
                if "No Record Found" in result_text:
                    status = "কোন রেকর্ড পাওয়া যায়নি"
                else:
                    status = "তথ্য পাওয়া গেছে! দয়া করে ওয়েবসাইট চেক করুন।"
                
            except Exception as e:
                status = f"এরর: {str(e)}"
            
            results.append(f"ID: {search_id}\nফলাফল: {status}\n" + "-"*30)
            
    finally:
        driver.quit()
    
    return "\n\n".join(results)

def send_email(content):
    if not SENDER_EMAIL or not SENDER_PASS:
        print("Email credentials not found in Secrets!")
        return

    msg = EmailMessage()
    msg.set_content(f"নমস্কার,\n\nআপনার আজকের কৃষক বন্ধু সার্চ রিপোর্ট নিচে দেওয়া হলো:\n\n{content}\n\nধন্যবাদ,\nআপনার অটোমেশন বট")
    msg['Subject'] = "Daily Krishak Bandhu Report"
    msg['From'] = SENDER_EMAIL
    msg['To'] = SENDER_EMAIL

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASS)
            smtp.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    report_data = get_farmer_data()
    send_email(report_data)
    
