import os
import smtplib
import time
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

# কনফিগারেশন
URL = "https://krishakbandhu.wb.gov.in/agricultural-labour/farmer_search"
SEARCH_IDS = ["8192 5751 6764", "819257516764"]
SENDER_EMAIL = os.environ.get('EMAIL_USER')
SENDER_PASS = os.environ.get('EMAIL_PASS')

def get_farmer_data():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # এটি আসল ব্রাউজারের মতো কাজ করতে সাহায্য করবে
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    results = []

    try:
        for search_id in SEARCH_IDS:
            driver.get(URL)
            time.sleep(5) # পেজ লোড হতে সময় দিন
            
            try:
                # ১. আইডি টাইপ ড্রপডাউন থেকে 'Voter ID' সিলেক্ট করা
                # লক্ষ্য করুন: সাইটে আইডি ড্রপডাউন থাকলে এটি কাজ করবে
                dropdown = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, "id_type")) # আইডিটি চেক করুন
                )
                select = Select(dropdown)
                select.select_by_index(1) # প্রথম অপশন সিলেক্ট করবে
                
                # ২. ইনপুট বক্সে নাম্বার লেখা
                input_field = driver.find_element(By.NAME, "voter_id")
                input_field.clear()
                input_field.send_keys(search_id)
                
                # ৩. সার্চ বাটনে ক্লিক
                search_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                search_btn.click()
                
                time.sleep(5) # রেজাল্ট লোড হতে সময় দিন
                
                # ৪. টেবিল থেকে ডাটা নেওয়া
                result_area = driver.find_element(By.TAG_NAME, "body").text
                
                if "No Record Found" in result_area:
                    status = "কোন তথ্য পাওয়া যায়নি (No Record Found)"
                else:
                    # এখানে আপনি চাইলে টেবিলের নির্দিষ্ট অংশ কাটতে পারেন
                    status = "সফল! তথ্য পাওয়া গেছে।"
                
            except Exception as e:
                status = f"এরর: এলিমেন্ট খুঁজে পাওয়া যায়নি। ওয়েবসাইট লোড হতে সমস্যা হচ্ছে।"
            
            results.append(f"ID: {search_id}\nফলাফল: {status}\n" + "-"*30)
            
    finally:
        driver.quit()
    
    return "\n\n".join(results)

def send_email(content):
    if not SENDER_EMAIL or not SENDER_PASS: return
    msg = EmailMessage()
    msg.set_content(f"নমস্কার,\n\nরিপোর্ট:\n\n{content}\n\nধন্যবাদ।")
    msg['Subject'] = "Daily Farmer Search Report"
    msg['From'] = SENDER_EMAIL
    msg['To'] = SENDER_EMAIL
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASS)
        smtp.send_message(msg)

if __name__ == "__main__":
    report = get_farmer_data()
    send_email(report)
    
