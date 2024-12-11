import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
import time
from google.cloud import storage
import re

def get_next_image_number(bucket):
    blobs = bucket.list_blobs()
    highest_number = 0
    for blob in blobs:
        match = re.search(r'image_(\d+)\.jpg$', blob.name)
        if match:
            number = int(match.group(1))
            if number > highest_number:
                highest_number = number
    return highest_number + 1

def download_images(url, bucket_name, max_images=10000, record_file='processed_images_paginated.txt'):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    next_image_number = get_next_image_number(bucket)

    if os.path.exists(record_file):
        with open(record_file, 'r') as f:
            processed_urls = set(line.strip() for line in f)
    else:
        processed_urls = set()

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)

    img_urls = set()
    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(img_urls) < max_images:
        try:
            # Scroll down to the bottom of the page to load all images
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Collect image URLs
            images = driver.find_elements(By.TAG_NAME, 'img')
            for image in images:
                img_url = image.get_attribute('src')
                if img_url and 'http' in img_url and img_url not in processed_urls:
                    img_urls.add(img_url)
                    if len(img_urls) >= max_images:
                        break

            # Process and upload images
            with open(record_file, 'a') as f:
                for img_url in img_urls:
                    try:
                        img_data = requests.get(img_url).content
                        blob_name = f"image_{next_image_number}.jpg"
                        blob = bucket.blob(blob_name)
                        blob.upload_from_string(img_data, content_type='image/jpeg')
                        print(f'Uploaded {blob_name} to bucket {bucket_name}')
                        f.write(img_url + '\n')
                        next_image_number += 1
                    except requests.exceptions.RequestException as e:
                        print(f"Error downloading {img_url}: {e}")
                    except Exception as e:
                        print(f"Error uploading {img_url} to GCS: {e}")

            img_urls.clear()

            # Check for the "Next" button and click it
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//a[@title='Next page']"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(2)  # Give the button time to become interactive
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)  # Wait for the page to load
            except NoSuchElementException:
                print("No next button found. Reached the end of pagination.")
                break
            except TimeoutException:
                print("Next button was not clickable in time.")
                break
            except ElementClickInterceptedException:
                print("Next button click intercepted, trying to scroll to it again.")
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(2)
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

        except StaleElementReferenceException:
            time.sleep(2)
            continue

        except TimeoutException:
            print("Timeout occurred while loading the page.")
            break

        except Exception as e:
            print(f"Unexpected error: {e}")
            break

    driver.quit()

# Example usage
download_images('https://www.istockphoto.com/search/2/image-film?phrase=indian%20woman%20young', 'image_scraping_test2', max_images=10000)
