from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
import requests
import json
import logging
from fake_useragent import UserAgent


ua = UserAgent()


def encrypt_rsa(public_key_str, plaintext):
    # Wrap the public key in PEM format
    pem_public_key = (
        f"-----BEGIN PUBLIC KEY-----\n{public_key_str}\n-----END PUBLIC KEY-----"
    )

    # Import the public key
    public_key = RSA.import_key(pem_public_key)
    cipher_rsa = PKCS1_v1_5.new(public_key)

    # Encrypt the plaintext
    ciphertext = cipher_rsa.encrypt(plaintext.encode())

    # Return Base64-encoded ciphertext
    return base64.b64encode(ciphertext).decode("utf-8")


# Example function to perform login
def perform_login(login_id, login_pwd, store_id_yn):
    # Obtain public key from the server
    public_key_url = "https://klas.kw.ac.kr/usr/cmn/login/LoginSecurity.do"
    public_key_response = requests.get(public_key_url)
    public_key_json = public_key_response.json()
    public_key_str = public_key_json["publicKey"]

    session = requests.Session()

    # Encrypt login data
    login_data = {"loginId": login_id, "loginPwd": login_pwd, "storeIdYn": store_id_yn}
    login_json = json.dumps(login_data)
    encrypted_login = encrypt_rsa(public_key_str, login_json)
    print(encrypted_login)

    # Send encrypted data to login endpoint
    login_url = "https://klas.kw.ac.kr/usr/cmn/login/LoginConfirm.do"

    login_payload = {
        "loginToken": encrypted_login,
        "redirectUrl": "",
        "redirectTabUrl": "",
    }

    default_cookies = {
        "WMONID": "",
        "SESSION": "",
        "JSESSIONID": "",
    }

    login_headers = {"Content-Type": "application/json", "User-Agent": ua.random}

    login_response = session.post(
        login_url, json=login_payload, headers=login_headers, cookies=default_cookies
    )

    if login_response.status_code == 200:
        response_data = login_response.json()
        if response_data.get("errorCount", 0) == 0:
            print("Login successful. Redirecting...")
            print(login_response.cookies)
        else:
            print("Login failed.")
    else:
        print("Failed to communicate with server.")
        print("Status code:", login_response.status_code)


# Example usage
if __name__ == "__main__":
    from os import getenv
    from dotenv import load_dotenv

    load_dotenv()
    perform_login(getenv("KW_USERNAME"), getenv("KW_PASSWORD"), "Y")
