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
import argparse

from scraper_driver import ScraperDriver


def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, help="url")
    parser.add_argument(
        "--nowav", action="store_true", help="some dl urls have no wav and yeah"
    )
    parser.add_argument("--skip", type=int, default=0, help="items skiped")
    parser.add_argument(
        "--id",
        type=str,
        help="basically you have to try downloading 1, then get the url of the file and get\
    the thing between the /download/ and /filename, would prolly update this if I felt like it but most likely wont",
    )
    parser.add_argument(
        "--second",
        action="store_true",
        help="for cases where the dl url needs the 2nd url",
    )
    parser.add_argument(
        "--small", action="store_true", help="the wav in the url is not capitalized"
    )

    args = parser.parse_args()
    assert args.url, "URL is required. Please provide --url argument."
    assert args.id, "no id!"
    return args


def tryDownload(dl_url, file_path):
    try:
        print("starting...")
        response = requests.get(dl_url)
        response.raise_for_status()
        with open(file_path, "wb") as file:
            file.write(response.content)
        print("download finished! yippee")
    except Exception as e:
        if "large" not in dl_url:
            tryDownload(dl_url.replace("raw", "large"), file_path)
        print(e)
        print("its joever, no file downloaded")


if __name__ == "__main__":
    args = parseArgs()

    url_id = args.id
    url = args.url
    skip_num = args.skip - 1

    """
    the magic main url goes here
    """
    main_url = ""
    file_name = url.split("/")[-1].split("?")[0]
    dl_url_beginning = f"{main_url}/{url_id}/{file_name}/WAV"
    try:
        url_split = url.split("%22")[1]
        url_name = url_split[1]
        url_2nd_name = url_split[3]

        if url_id.startswith("daily") and url_name != "WAV" and args.second:
            dl_url_beginning = (
                f"{main_url}/{url_id}/{file_name}/{url_name}/{url_2nd_name}/WAV"
            )
        elif url_id.startswith("daily") and url_name != "WAV":
            dl_url_beginning = f"{main_url}/{url_id}/{file_name}/{url_name}/WAV"

    except:
        pass
    if args.nowav:
        dl_url_beginning = dl_url_beginning.replace("/WAV", "")
    elif args.small:
        dl_url_beginning = dl_url_beginning.replace("/WAV", "/wav")

    folder_path = f"./full/{file_name}"

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if not os.path.isfile(f"{folder_path}/names.json"):
        cl = ScraperDriver(download_dir=folder_path, headless=True)
        driver = cl.getDriver()

        driver.get(url)
        time.sleep(10)

        try:
            elements_with_class = driver.find_elements(
                By.CSS_SELECTOR, ".non-selectable.q-item"
            )
            names = []
            for el_count, el in enumerate(elements_with_class):
                if skip_num > el_count:
                    continue
                item = el.find_elements(By.CLASS_NAME, "q-item__label")[0]
                names.append(item.text)
            with open(f"{folder_path}/names.json", "w", encoding="utf-8") as file:
                json.dump(names, file, ensure_ascii=False)
        except Exception as e:

            html_content = driver.page_source
            with open("download_error.html", "w", encoding="utf-8") as file:
                file.write(html_content)
            print(e)
            print("problem in driver or something")

        driver.quit()

    with open(f"{folder_path}/names.json", "r", encoding="utf-8") as file:
        names = json.load(file)
    if not names:
        raise Exception("empty array")

    names_len = len(names)
    for name_count, name in enumerate(names):
        file_path = f"{folder_path}/{name}"
        if not os.path.isfile(file_path):
            print(f"trying to download {name} | {name_count}/{names_len}")
            dl_url = f"{dl_url_beginning}/{name}"
            tryDownload(dl_url, file_path)

        else:
            print("file already downloaded!")
