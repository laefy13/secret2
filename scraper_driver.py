from selenium import webdriver
from selenium_stealth import stealth

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService


class ScraperDriver:
    def __init__(self, headless=False, download_dir=""):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")

        if headless:
            options.add_argument("--headless")

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--window-size=1920,1080")
        if download_dir != "":
            options.add_experimental_option(
                "prefs",
                {
                    "download.default_directory": download_dir,
                },
            )

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
        self.driver = driver

    def getDriver(self):
        return self.driver
