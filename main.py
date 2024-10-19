import os
import time
import json
import logging
import getpass

from src.login import login
from src.utils import get_todo_list
from src.helpers import get_subjects


def main() -> None:
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    try:
        if time.time() - os.path.getmtime(f"{username}_cookies.json") > 3600:
            login_cookies = login(username, password)

        with open(f"{username}_cookies.json", "r") as f:
            login_cookies = json.load(f)

    except FileNotFoundError:
        login_cookies = login(username, password)
        with open(f"{username}_cookies.json", "w") as f:
            json.dump(login_cookies, f)

    logging.info("Cookies saved to cookies.json")
    logging.info(login_cookies)

    if login_cookies is None:
        logging.error("Failed to login")
        exit(1)

    subjects = get_subjects(login_cookies)

    how_many_subjects = len(subjects.get("subjList"))
    subject_semester = subjects.get("value")

    for index in range(how_many_subjects):
        todo_list = get_todo_list(
            cookies=login_cookies,
            subject_id=subjects.get("subjList")[index].get("value"),
            year=subject_semester,
        )

        print(subjects.get("subjList")[index].get("name"))

        if todo_list["homeworks"]:
            print(len(todo_list["homeworks"]))

        if todo_list["lectures"]:
            print(len(todo_list["lectures"]))

        if todo_list["team_projects"]:
            print(len(todo_list["team_projects"]))

        if todo_list["quizzes"]:
            print(len(todo_list["quizzes"]))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        encoding="utf-8",
        filename="main.log",
    )

    main()
