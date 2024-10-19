import os
import json
import logging
import subprocess

import requests
from fake_useragent import UserAgent

ua = UserAgent()


def encryptor(publicKey, phrase):
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to jsencryptor.js
    js_path = os.path.join(current_dir, "js", "jsencryptor.js")

    # Check if the JS file exists
    if not os.path.exists(js_path):
        raise FileNotFoundError(f"JavaScript file not found: {js_path}")

    try:
        result = subprocess.run(
            ["node", js_path, publicKey, phrase],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output = result.stdout.decode("utf-8").strip()
        return output
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running Node.js script: {e}")
        logging.error(f"STDERR: {e.stderr}")
        return None
    except FileNotFoundError:
        logging.error("Node.js is not installed or not in the system PATH")
        return None


def login(login_id, login_pwd):
    login_cookies = {}

    login_url = "https://klas.kw.ac.kr/usr/cmn/login/LoginForm.do"

    login_response = requests.get(login_url)

    logging.info(login_response.cookies)

    for cookie in login_response.cookies:
        login_cookies[cookie.name] = cookie.value

    # Obtain public key from the server
    public_key_url = "https://klas.kw.ac.kr/usr/cmn/login/LoginSecurity.do"
    public_key_response = requests.get(public_key_url)

    for cookie in public_key_response.cookies:
        login_cookies[cookie.name] = cookie.value

    public_key_json = public_key_response.json()
    public_key_str = public_key_json["publicKey"]

    session = requests.Session()

    # Encrypt login data
    login_data = {"loginId": login_id, "loginPwd": login_pwd, "storeIdYn": "Y"}
    login_json = json.dumps(login_data)

    try:
        encrypted_login = encryptor(public_key_str, login_json)
        if encrypted_login:
            logging.info(f"Encrypted output: {encrypted_login}")
        else:
            logging.error("Encryption failed")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

    # Send encrypted data to login endpoint
    login_url = "https://klas.kw.ac.kr/usr/cmn/login/LoginConfirm.do"

    login_payload = {
        "loginToken": encrypted_login,
        "redirectUrl": "/std/cmn/frame/Frame.do",
        "redirectTabUrl": "",
    }

    login_headers = {"Content-Type": "application/json", "User-Agent": ua.random}

    login_response = session.post(
        login_url, json=login_payload, headers=login_headers, cookies=login_cookies
    )

    if login_response.status_code == 200:
        response_data = login_response.json()
        if response_data.get("errorCount", 0) == 0:
            logging.info("Login successful.")
            for cookie in session.cookies:
                login_cookies[cookie.name] = cookie.value
            return login_cookies
        else:
            logging.error("Login failed.")
            return None
    else:
        logging.error("Failed to communicate with server.")
        logging.error(f"Status code: {login_response.status_code}")
        return None
