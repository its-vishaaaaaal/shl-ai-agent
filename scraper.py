from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

all_data = []
seen = set()

# Each page contains 12 records. Looping through approximately 32 pages.
# Page 1 = start=0, Page 2 = start=12, Page 3 = start=24, etc.
# 32 pages * 12 = 384 as the maximum loop boundary.
for start_val in range(0, 385, 12):
    page_num = (start_val // 12) + 1
    print(f"\n🚀 Fetching Page {page_num} (start={start_val})...")
    
    # Constructing the target URL using the pagination parameters
    target_url = f"https://www.shl.com/solutions/products/product-catalog/?start={start_val}&type=1&type=1"
    driver.get(target_url)
    
    # Static wait to ensure the dynamic content is fully rendered
    time.sleep(4)
    
    try:
        # Locate all table rows for the current page
        rows = driver.find_elements(By.XPATH, "//tr[@data-entity-id]")
        print(f"📈 Rows found on this page: {len(rows)}")
        
        if not rows:
            print("No data rows found on this page. End of catalog reached. Stopping loop.")
            break
            
        page_saved_count = 0
        for row in rows:
            try:
                name_element = row.find_element(By.XPATH, ".//td[contains(@class,'title')]//a")
                name = name_element.text.strip()
                url = name_element.get_attribute("href")
                
                if url and url.startswith("/"):
                    url = "https://www.shl.com" + url

                test_type = "K"
                try:
                    type_tag = row.find_element(By.XPATH, ".//td[contains(@class,'product-catalogue__keys')]//span")
                    test_type = type_tag.text.strip()
                except:
                    pass

                if name and url and url not in seen:
                    all_data.append({
                        "name": name,
                        "url": url,
                        "test_type": test_type
                    })
                    seen.add(url)
                    page_saved_count += 1
            except:
                continue
                
        print(f"✅ Saved {page_saved_count} new records from this page.")
        
        # Safe exit if no new records are found on a subsequent page (all duplicates)
        if page_saved_count == 0 and page_num > 1:
            print("No new records found. Loop complete.")
            
    except Exception as page_err:
        print(f"❌ Error while scraping this page: {page_err}")
        continue

driver.quit()

# Save the extracted data to a JSON file
with open("individual_test_solutions.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=4, ensure_ascii=False)

print("\n" + "="*40)
print("🏆 SCRAPING MISSION SUCCESSFULLY COMPLETED!")
print(f"📊 TOTAL UNIQUE RECORDS SAVED IN JSON: {len(all_data)}")
print("="*40)