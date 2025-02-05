import requests
import json
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_all_blog_titles():
    # API endpoint
    url = "https://www.anaplan.com/content/anaplan/us/en/blog/jcr:content/root/container/container/aemsearch.search.json"

    # Base parameters for the API request
    base_params = {
        "contentType": "blog",
        "resourcePath": "/content/anaplan/us/en/blog",
        "locale": "en",
        "query": None,
        "filterCategoryList": [
            {"value": "anaplan:blog/function", "label": "Function"},
            {"value": "anaplan:blog/industry", "label": "Industry"},
            {"value": "anaplan:blog/platform", "label": "Product"}
        ],
        "filterCategorySelected": [
            {"label": "Supply Chain", "value": "anaplan:blog/function/supply-chain"}
        ],
        "order": {
            "name": "@jcr:content/createdDate",
            "sortDirection": "desc"
        },
        "pageSize": "10",
        "pageNumber": 0
    }

    all_titles = []
    page_number = 0

    while True:
        # Update the page number in the request parameters
        base_params["pageNumber"] = page_number
        params = {"searchRequest": json.dumps(base_params)}

        try:
            # Send the GET request
            response = requests.get(url, params=params)
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()

            # Collect blog titles and URLs
            hits = data.get("hits", [])
            for hit in hits:
                title = hit.get("title")
                blog_url = hit.get("url")
                all_titles.append({"title": title, "url": blog_url})

            # Check if more results are available
            if not data.get("hasMore"):
                print("No more results available. Fetching complete.")
                break

            page_number += 1

        except Exception as e:
            print(f"Error fetching page {page_number}: {e}")
            break

    return all_titles

def sanitize_text(text):
    """Clean up text by replacing problematic characters."""
    return text.encode("utf-8", errors="ignore").decode("utf-8")

def fetch_blog_content_with_selenium(blog_url):
    """Use Selenium in headless mode to fetch the content of a blog."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service("/Users/liam.mccaffrey/Downloads/COMP_ANAL/chromedriver-mac-arm64/chromedriver")  # Update with your ChromeDriver path

    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        driver.get(blog_url)

        # Wait for the blog content to load (adjust selector as needed)
        content = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main.container"))
        )
        return content.text
    except Exception as e:
        print(f"Error fetching content for {blog_url}: {e}")
        return "Error fetching content."
    finally:
        driver.quit()

def save_to_database(blogs, db_path="anaplan_sitemap_urls.db"):
    """Save the fetched blog titles, URLs, and content to a SQLite database."""
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create the table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blog_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE,
                url TEXT UNIQUE,
                content TEXT
            )
        ''')

        # Insert the blog data
        for blog in blogs:
            sanitized_title = sanitize_text(blog["title"])
            cursor.execute('''
                INSERT OR IGNORE INTO blog_posts (title, url, content) VALUES (?, ?, ?)
            ''', (sanitized_title, blog["url"], blog["content"]))

        # Commit changes and close the connection
        conn.commit()
        conn.close()
        print(f"All enriched blog data saved to {db_path}")
    except Exception as e:
        print(f"Error saving to database: {e}")

# Main function
if __name__ == "__main__":
    # Fetch blog titles and URLs
    blogs = fetch_all_blog_titles()

    # Sanitize and fetch content for each blog
    enriched_blogs = []
    for blog in blogs:
        title = sanitize_text(blog["title"])
        url = blog["url"]
        print(f"Fetching content for: {title}")
        content = fetch_blog_content_with_selenium(url)
        enriched_blogs.append({"title": title, "url": url, "content": sanitize_text(content)})

    # Save the enriched blog data to the SQLite database
    save_to_database(enriched_blogs)