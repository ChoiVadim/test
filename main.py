import os
import time
import json
import logging
import getpass
from pprint import pprint

from dotenv import load_dotenv

from login import login
from utils import get_todo_list
from helpers import get_subjects, get_subject_info


load_dotenv()


def main() -> None:
    login_cookies = None
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    try:
        if time.time() - os.path.getmtime(f"{username}_cookies.json") > 3600:
            login_cookies = login(username, password)

        with open(f"{username}_cookies.json", "r") as f:
            login_cookies = json.load(f)

    except FileNotFoundError:
        login_cookies = login(username, password)

    if login_cookies is None:
        logging.error("Failed to login")
        exit(1)

    subjects = get_subjects(login_cookies)
    get_subject_info(login_cookies, subjects, 0)

    # for index in range(len(data.get("subjList"))):
    #     subject_name = data.get("subjList")[index].get("label")
    #     lecture_info = get_subject_info(
    #         login_cookies=login_cookies, data=data, subject_index=index
    #     )
    #     print(f"{subject_name:_^80}")
    #     print_lecture_info(lecture_info)
    #     print()

    #     year = data.get("value")
    #     print(f"{f"You need to complete!"}")
    #     print(f"{data.get("subjList")[index].get("name")}: ", end="")

    #     get_todo_list(
    #         cookies=login_cookies,
    #         subject_id=data.get("subjList")[index].get("value"),
    #         year=year,
    #     )
    #     print("\n\n")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        encoding="utf-8",
        filename="main.log",
    )

    main()
