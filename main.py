import json
import logging
from os import getenv
import getpass
from dotenv import load_dotenv

from login import login
from helpers import get_subject_info, get_subjects, print_lecture_info
from todo import get_todo_list

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
    filename="main.log",
)

login_cookies = None


def main() -> None:
    # try:
    #     with open("cookies.json", "r") as f:
    #         login_cookies = json.load(f)
    # except FileNotFoundError:
    #     login_cookies = login(getenv("KW_USERNAME"), getenv("KW_PASSWORD"))
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    login_cookies = login(username, password)

    if login_cookies is None:
        logging.error("Failed to login")
        exit(1)

    data = get_subjects(login_cookies)

    for index in range(len(data.get("subjList"))):
        subject_name = data.get("subjList")[index].get("label")
        lecture_info = get_subject_info(
            login_cookies=login_cookies, data=data, subject_index=index
        )
        print(f"{subject_name:_^80}")
        print_lecture_info(lecture_info)
        print()

        year = data.get("value")
        print(f"{f"You need to complete!"}")
        print(f"{data.get("subjList")[index].get("name")}: ", end="")

        get_todo_list(
            cookies=login_cookies,
            subject_id=data.get("subjList")[index].get("value"),
            year=year,
        )
        print("\n\n")


if __name__ == "__main__":
    main()
