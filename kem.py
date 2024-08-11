import json
import os
from selenium import webdriver
from selenium_stealth import stealth
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService


import requests
import uuid
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--skip", type=int, default=560, help="number of items skipped")
parser.add_argument("--url", type=str, help="url")

args = parser.parse_args()
skip_num = 0
if args.skip > 0:
    skip_num = args.skip

if not args.url:
    print("url needed cuz")
    exit()

url = args.url

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")

options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--window-size=1920,1080")
service = ChromeService(executable_path=ChromeDriverManager().install())

driver = webdriver.Chrome(options=options, service=service)

stealth(
    driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)

driver.get(url)

time.sleep(10)


def get_everything(driver, url, folder_name):
    infos = {}
    sub_folder_name = url.split("/")[-1]
    if not os.path.exists(f"{folder_name}/{sub_folder_name}"):
        os.makedirs(f"{folder_name}/{sub_folder_name}")

    # contents
    try:
        contents = driver.find_element(By.CLASS_NAME, "post__content")
        infos["contents"] = contents.text
    except:
        print("contents not found")

    # attachments
    try:
        attachments = driver.find_element(By.CLASS_NAME, "post__attachments")
        url_els = attachments.find_elements(By.CLASS_NAME, "post__attachment-link")
        attachment_names = []
        for url_el in url_els:
            dl_url = url_el.get_attribute("href")
            attachment_name = url_el.get_attribute("download")

            response = requests.get(dl_url)

            with open(
                f"{folder_name}/{sub_folder_name}/{attachment_name}", "wb"
            ) as attachment:
                attachment.write(response.content)
            attachment_names.append(attachment_name)
        infos["AttachmentNames"] = attachment_names
    except:
        print("no attachements found")

    # files
    try:
        files_container = driver.find_element(By.CLASS_NAME, "post__files")
        files = files_container.find_elements(By.CLASS_NAME, "image-link")
        file_names = []
        files_len = len(files)
        for file_count, file in enumerate(files):
            dl_url = file.get_attribute("href")
            file_name = file.get_attribute("download")
            img_name = f"{folder_name}/{sub_folder_name}/{file_name}"
            if os.path.isfile(img_name):
                file_names.append(file_name)
                continue
            print(f"requesting image {file_count} / {files_len}")
            response = requests.get(dl_url)

            with open(img_name, "wb") as file:
                file.write(response.content)
            file_names.append(file_name)
        infos["FileNames"] = file_names
    except Exception as e:
        print("bruh AINTNOWAY that there is no single file")

    infos["URL"] = url
    print(f"saving {url}...")

    return infos


def read_json_file(file_path):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
        for item in data:
            yield item


count = -1
url_split = url.split("/")
folder_name = f"{url_split[-3]}-{url_split[-1]}"

if not os.path.exists(folder_name):
    os.mkdir(folder_name)


while True:
    try:
        original_window = driver.current_window_handle
        container_el = driver.find_element(By.CLASS_NAME, "card-list__items")
        href_el = container_el.find_elements(By.CLASS_NAME, "image-link")
        html_content = driver.page_source
        with open("kem.html", "w", encoding="utf-8") as file:
            file.write(html_content)

        file_path = "kem.json"
        urls = []
        if os.path.isfile(file_path):
            urls = [info["URL"] for info in read_json_file(file_path)]

        for element in href_el:
            count += 1
            print(f"Scraping: {count}")
            tab_url = element.get_attribute("href")
            if tab_url in urls:
                print(f"url saved: {tab_url}")
                continue
            driver.execute_script("window.open(arguments[0]);", tab_url)
            driver.switch_to.window(driver.window_handles[-1])

            new_info = get_everything(driver, tab_url, folder_name)

            if not new_info:
                driver.close()

                driver.switch_to.window(original_window)
                continue

            urls.append(new_info["URL"])

            file_name = "kem.json"
            infos = []
            if os.path.exists(file_name):
                with open(file_name, "r") as json_file:
                    infos = json.load(json_file)

            infos.append(new_info)

            with open(file_name, "w") as json_file:
                json.dump(infos, json_file, indent=4)

            driver.close()

            driver.switch_to.window(original_window)

        next_button = driver.find_element(By.CLASS_NAME, "next")
        next_button.click()
        print("going nexxt page....")
        time.sleep(10)
    except Exception as e:
        print("while error:", e)
        break

driver.quit()
