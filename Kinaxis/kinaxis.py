import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import sqlite3
import time


# Scrape blog URLs using requests and BeautifulSoup
def scrape_blogs_with_pagination(base_url, query_params, max_pages=10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    blogs = []
    page = 0

    while page < max_pages:
        print(f"Scraping page {page + 1}...")
        query_params["page"] = page
        try:
            response = requests.get(base_url, params=query_params, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Request failed on page {page}: {e}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        # Locate blog titles and URLs in HTML
        blog_elements = soup.select('.blog.views-row')
        if not blog_elements:
            print(f"No more blogs found on page {page}. Stopping pagination.")
            break

        for blog in blog_elements:
            title_element = blog.select_one('.views-field-title a')
            url_element = blog.select_one('.views-field-title a')
            
            if title_element and url_element:
                title = title_element.text.strip()
                url = url_element['href']
                blogs.append({
                    "title": title,
                    "url": f"https://www.kinaxis.com{url}"  # Make URL absolute
                })

        page += 1
        time.sleep(2)  # Throttle requests to avoid overwhelming the server

    return blogs


# Set up headless Selenium browser
def setup_headless_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome resource limits
    chrome_options.add_argument("--window-size=1920x1080")  # Set a standard window size
    
    # Initialize WebDriver with your correct driver path
    service = Service("/Users/liam.mccaffrey/Downloads/Blog_extractor/chromedriver-mac-arm64/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


# Scrape blog content using Selenium
def scrape_blog_content(blogs):
    driver = setup_headless_browser()
    enriched_blogs = []

    try:
        for idx, blog in enumerate(blogs, start=1):
            try:
                print(f"Scraping content for blog {idx}/{len(blogs)}: {blog['url']}")
                driver.get(blog["url"])
                time.sleep(2)  # Adjust sleep time based on page load speed

                # Extract blog title and content
                title = driver.find_element(By.TAG_NAME, "h1").text
                content = driver.find_element(By.CLASS_NAME, "page-content-wrapper").text
                
                enriched_blogs.append({
                    "title": title,
                    "content": content,
                    "url": blog["url"]
                })
                print(f"Successfully scraped: {title}")
            except Exception as e:
                print(f"Error scraping {blog['url']}: {e}")
    except Exception as e:
        print(f"Error during content scraping: {e}")
    finally:
        driver.quit()

    return enriched_blogs


# Save blogs to SQLite database
def save_to_database(blogs, db_path="kinaxis.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE,
                url TEXT UNIQUE,
                content TEXT
            )
        ''')

        # Insert data
        for blog in blogs:
            cursor.execute('''
                INSERT OR IGNORE INTO blogs (title, url, content) VALUES (?, ?, ?)
            ''', (blog["title"], blog["url"], blog["content"]))

        conn.commit()
        conn.close()
        print(f"All blog data saved to {db_path}")
    except Exception as e:
        print(f"Error saving to database: {e}")


# Main function
if __name__ == "__main__":
    BASE_URL = "https://www.kinaxis.com/en/search"
    QUERY_PARAMS = {
        "type[blog]": "blog",
        "search_api_fulltext": "supply chain"
    }

    # Step 1: Scrape blog URLs
    print("Step 1: Fetching blog URLs...")
    scraped_blogs = scrape_blogs_with_pagination(BASE_URL, QUERY_PARAMS, max_pages=10)

    # Step 2: Enrich blog data with content
    print("Step 2: Fetching blog content...")
    enriched_blogs = scrape_blog_content(scraped_blogs)

    # Step 3: Save to database
    print("Step 3: Saving blogs to database...")
    save_to_database(enriched_blogs)