from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv
from datetime import datetime
from queries import QUERIES
from utils import analyze_response, append_to_sheet

load_dotenv()

def query_google_sge(query):
    options = Options()
    options.add_argument("--headless=new")  # Run headless (no browser window)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")  # Mimic real browser
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get("https://www.google.com")
        wait = WebDriverWait(driver, 10)
        
        # Find and fill search box
        search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
        search_box.clear()
        search_box.send_keys(query + Keys.ENTER)
        
        # Wait for results
        time.sleep(5)  # Allow AI Overview to load
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract AI Overview (2025 selector: div with data-ai-overview="true")
        ai_overview = soup.find('div', {'data-ai-overview': 'true'})
        ai_text = ai_overview.get_text(strip=True) if ai_overview else ""
        
        # Fallback to organic snippet if no AI Overview
        if not ai_text:
            snippet = soup.find('span', class_='hgKElc')  # Common 2025 snippet selector
            ai_text = snippet.get_text(strip=True) if snippet else "No AI Overview or snippet found"
        
        return ai_text
    except Exception as e:
        print(f"Error for {query}: {e}")
        return "Error extracting content"
    finally:
        driver.quit()

results = []
for query in QUERIES:
    ai_text = query_google_sge(query)
    mention, score, excerpt = analyze_response(ai_text)
    results.append([
        datetime.now().isoformat(),
        query,
        mention,
        score,
        excerpt,
        ai_text[:500]  # Truncate for Sheet
    ])
    time.sleep(3)  # Delay to avoid rate limits/blocks

if results:
    append_to_sheet(results, 'SGE')
print("Google SGE tracking complete. Check 'SGE' tab and dashboard.")