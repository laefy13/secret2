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


def get_everything(driver, urls, url):

    if not os.path.exists("./samples"):
        os.makedirs("./samples")
    if not os.path.exists("./images"):
        os.makedirs("./images")
    infos = {}

    # infos
    try:
        info_table = driver.find_element(By.ID, "work_right_inner")

        title_element = driver.find_element(
            By.XPATH, "//h1[contains(@id, 'work_name')]"
        )
        infos["Title"] = title_element.text

        maker_name = info_table.find_element(By.CLASS_NAME, "maker_name")
        infos["Circle"] = maker_name.text

        outline_el = info_table.find_element(By.ID, "work_outline")
        tr_elements = outline_el.find_elements(By.TAG_NAME, "tr")
        for tr in tr_elements:
            th_element = tr.find_element(By.TAG_NAME, "th")
            td_element = tr.find_element(By.TAG_NAME, "td")
            infos[th_element.text] = td_element.text
    except Exception as e:
        print(f"info error: {e}")
        driver.quit()
        exit()

    # downloading samples
    file_ext = "zip"
    dl_url = None
    try:
        dl_button = driver.find_element(By.CLASS_NAME, "btn_trial")
        dl_url = dl_button.get_attribute("href")
    except:
        pass
    if dl_url is None:
        file_ext = "mp4"
        for height in ["1080", "720", "480"]:
            try:
                vid_el = driver.find_element(
                    By.XPATH, f"//source[@data-height='{height}']"
                )
                print("found the vid")

                dl_url = vid_el.get_attribute("src")

                break
            except:
                continue

    final_name = url.split("/")[-1].replace(".html", "")

    if not dl_url is None:
        response = requests.get(dl_url)
        file_name = f"./samples/{final_name}.{file_ext}"
        with open(file_name, "wb") as file:
            file.write(response.content)
        infos["FileName"] = file_name
    else:
        try:
            iframe_el = driver.find_element(By.CLASS_NAME, "work_parts_container")
            iframe = iframe_el.find_element(By.TAG_NAME, "iframe")
            driver.switch_to.frame(iframe)
            track_list = driver.find_element(By.TAG_NAME, "ol")
            tracks = track_list.find_elements(By.TAG_NAME, "li")

            if tracks == []:
                raise Exception
            folder_name = f"./samples/{final_name}"
            os.makedirs(folder_name)
            for track in tracks:
                track_url = track.get_attribute("data-src")
                response = requests.get(track_url)
                file_name = f"{folder_name}/{uuid.uuid4()}.{track_url[-5:]}"
                with open(file_name, "wb") as file:
                    file.write(response.content)
            infos["FileName"] = folder_name

        except Exception as e:
            try:
                vid_el = driver.find_element(By.XPATH, f"//source[@data-height='1080']")

                dl_url = vid_el.get_attribute("src")
                response = requests.get(dl_url)
                file_name = f"./samples/{file_name}.{dl_url[-6:]}"
                with open(file_name, "wb") as file:
                    file.write(response.content)
                infos["FileName"] = file_name

            except:
                html_content = driver.page_source
                with open("error.html", "w", encoding="utf-8") as file:
                    file.write(html_content)
                print(f"bruh: {e}")
                infos["FileName"] = "noSample"

    print("doing images...")
    # images
    try:
        image_slider = driver.find_element(By.CLASS_NAME, "product-slider-data")
        images = image_slider.find_elements(By.TAG_NAME, "div")
        image_name = f"./images/{final_name}"
        os.makedirs(image_name)
        for image in images:
            image_url = image.get_attribute("data-src")
            final_image_name = image_name + f"/{uuid.uuid4()}.{image_url[-5:]}"
            response = requests.get(f"https:{image_url}")
            with open(final_image_name, "wb") as file:
                file.write(response.content)
    except:
        pass

    infos["URL"] = url
    print(f'saving {infos["Title"]}...')
    urls.append(url)
    return infos


def read_json_file(file_path):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
        for item in data:
            yield item


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip", type=int, default=230, help="number of items skipped")
    parser.add_argument("--url", type=str, help="the url")

    args = parser.parse_args()
    assert args.url
    url = args.url
    skip_num = 0
    if args.skip > 0:
        skip_num = args.skip

    options = webdriver.ChromeOptions()

    options.add_argument("start-maximized")
    options.add_argument("--headless")

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
    try:
        what_button = driver.find_element(By.CLASS_NAME, "btn-approval")
        what_button.click()
    except Exception as e:
        print(f"guess youre g: {e}")
        pass

    count = -1
    while True:
        try:
            original_window = driver.current_window_handle
            elements_with_class = driver.find_elements(
                By.CLASS_NAME, "search_result_img_box_inner"
            )

            file_path = "infos.json"
            if os.path.isfile(file_path):
                urls = [info["URL"] for info in read_json_file(file_path)]

            for element in elements_with_class:
                count += 1
                if count < skip_num:
                    continue
                print(f"Scraping: {count}")
                tab = element.find_element(By.CLASS_NAME, "work_thumb_inner")
                tab_url = tab.get_attribute("href")

                if tab_url in urls:
                    continue

                driver.execute_script("window.open(arguments[0]);", tab_url)
                driver.switch_to.window(driver.window_handles[-1])

                new_info = get_everything(driver, urls, tab_url)
                if not new_info:
                    driver.close()

                    driver.switch_to.window(original_window)
                    continue
                file_name = "infos.json"
                infos = []
                if os.path.exists(file_name):
                    with open(file_name, "r") as json_file:
                        infos = json.load(json_file)

                infos.append(new_info)

                with open(file_name, "w") as json_file:
                    json.dump(infos, json_file, indent=4)

                driver.close()

                driver.switch_to.window(original_window)

            next_button = driver.find_element(By.XPATH, '//a[contains(text(), "Next")]')
            next_button.click()
            print("going nexxt page....")
            time.sleep(10)
        except Exception as e:
            print("while error:", e)
            break

    driver.quit()
