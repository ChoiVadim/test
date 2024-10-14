import json
import logging
from os import getenv

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
    try:
        with open("cookies.json", "r") as f:
            login_cookies = json.load(f)
    except FileNotFoundError:
        login_cookies = login(getenv("USERNAME"), getenv("PASSWORD"))

    if login_cookies is None:
        logging.error("Failed to login")
        exit(1)

    data = get_subjects(login_cookies)

    index = 0
    # subject_name = data.get("subjList")[index].get("name")
    # lecture_info = get_subject_info(
    #     login_cookies=login_cookies, data=data, subject_index=index
    # )
    # print(f"Subject: {subject_name}")
    # print_lecture_info(lecture_info)

    year = data.get("value")
    print(data.get("subjList")[index].get("value"))
    print(data.get("subjList")[index].get("label"))

    get_todo_list(
        cookies=login_cookies,
        subject_id=data.get("subjList")[index].get("value"),
        year=year,
    )


if __name__ == "__main__":
    main()
