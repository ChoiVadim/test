import json
import time
import logging

import requests
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


ua = UserAgent()


def get_encoded_password(raw_password: str) -> str | None:
    url = "https://klas.kw.ac.kr/mst/cmn/login/SelectScrtyPwd.do"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": ua.random,
    }

    data = {"loginPwd": raw_password}
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        encoded_pwd = response.json().get("loginPwd")
        logging.info(f"Encoded password: {encoded_pwd}")
        return encoded_pwd
    else:
        logging.error("Failed to get encoded password")
        return None


def login(username, raw_password) -> dict | None:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # service = Service('path/to/chromedriver')

    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://klas.kw.ac.kr/mst/cmn/login/LoginForm.do")

    password = get_encoded_password(raw_password)
    js_code = f"appLogin.setInitial('on', '{username}', '{password}')"
    driver.execute_script(js_code)

    time.sleep(3)

    cookies = driver.get_cookies()
    driver.quit()

    if len(cookies) == 0:
        logging.error("Failed to get cookies")
        return None

    login_cookies = {}

    for cookie in cookies:
        login_cookies[cookie["name"]] = cookie["value"]

    with open("cookies.json", "w") as f:
        json.dump(login_cookies, f)

    logging.info("Cookies saved to cookies.json")
    logging.info(login_cookies)

    return login_cookies
