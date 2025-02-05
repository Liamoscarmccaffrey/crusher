from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import sqlite3

# Initialize database (create the table if not already present)
def initialize_database(db_path='sitemap_urls.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            content TEXT,
            added_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Ensure the content column exists
def add_content_column(db_path='sitemap_urls.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute('ALTER TABLE urls ADD COLUMN content TEXT')
        print("Content column added successfully.")
    except sqlite3.OperationalError:
        print("Content column already exists.")
    conn.commit()
    conn.close()

# Retrieve URLs without content
def get_unscraped_urls(db_path='sitemap_urls.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id, url FROM urls WHERE content IS NULL')
    unscraped_urls = cursor.fetchall()  # List of tuples (id, url)
    conn.close()
    return unscraped_urls

# Store content in the database
def store_content(url_id, content, db_path='sitemap_urls.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('UPDATE urls SET content = ? WHERE id = ?', (content, url_id))
    conn.commit()
    conn.close()

# Scrape blog content using Selenium
def scrape_blog_content(url, css_selector):
    # Configure Selenium ChromeDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    service = Service(executable_path="/Users/liam.mccaffrey/Downloads/COMP_ANAL/chromedriver-mac-arm64/chromedriver")  # Update with your ChromeDriver path
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Load the URL
        driver.get(url)
        time.sleep(3)  # Wait for JS content to load (adjust if necessary)
        
        # Extract blog content using the CSS selector
        blog_elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
        blog_content = "\n".join([element.text for element in blog_elements])
        
        return blog_content
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None
    finally:
        driver.quit()

# Main function
def main():
    db_path = 'sitemap_urls.db'
    
    # Initialize the database and ensure the content column exists
    initialize_database(db_path)
    add_content_column(db_path)
    
    # Get URLs without content
    unscraped_urls = get_unscraped_urls(db_path)
    
    if not unscraped_urls:
        print("No new pages to scrape.")
        return
    
    print(f"Found {len(unscraped_urls)} pages to scrape.")
    
    # Define the CSS selector for blog content
    blog_css_selector = ".css-wnv8f0"  # Update this to match the target website's blog content class or ID
    
    for url_id, url in unscraped_urls:
        print(f"Scraping blog content from: {url}")
        content = scrape_blog_content(url, blog_css_selector)
        if content:
            store_content(url_id, content, db_path)
            print(f"Content successfully stored for {url}")
        else:
            print(f"Failed to scrape content for {url}")

if __name__ == '__main__':
    main()