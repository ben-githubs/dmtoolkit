import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


_DRIVER = None

def browser_fetch(url: str) -> str:
    get_driver().get("view-source:" + url)
    import time
    time.sleep(0)
    data = get_driver().find_element(By.TAG_NAME, "pre").text
    return data

def get_driver():
    """Lazily load the browser driver"""
    global _DRIVER
    if not _DRIVER:
        opts = Options()
        opts.headless = True
        os.environ["MOZ_HEADLESS"] = "1"
        _DRIVER = webdriver.Firefox(options=opts)
    return _DRIVER

class ConverterError(BaseException):
    pass