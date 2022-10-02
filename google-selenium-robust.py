import sys
import urllib3
import backoff
from selenium import webdriver

import logging

#
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s'
)
#
logging.getLogger('urllib3').setLevel(logging.ERROR)

SELENIUM_URL = "127.0.0.1:4444"


@backoff.on_exception(
    backoff.expo,
    urllib3.exceptions.MaxRetryError,
    max_tries=5,
    jitter=None
)
def selenium_connect(url):
    return webdriver.Remote(url, {'browserName': 'chrome'})


try:
    browser = selenium_connect(f"http://{SELENIUM_URL}/wd/hub")
except urllib3.exceptions.MaxRetryError:
    logging.error("Unable to connect to Selenium.")
    sys.exit(1)

browser.get("https://www.google.com")

logging.info(f"Retrieved URL: {browser.current_url}.")

browser.close()
