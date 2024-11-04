import os
import time
import json
import logging

import requests
from fake_useragent import UserAgent

from src.login import login

session = requests.Session()
ua = UserAgent()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
    filename="main.log",
)


def make_request(url: str, cookies: dict) -> dict | None:
    requests_body = {}

    headers = {
        "Content-Type": "application/json",
        "User-Agent": ua.random,
    }

    response = session.post(
        url=url, json=requests_body, headers=headers, cookies=cookies
    )

    if response.status_code == 200:
        return response.json()

    return None


def get_test(username, password) -> None:
    try:
        if time.time() - os.path.getmtime(f"{username}_cookies.json") > 3600:
            login_cookies = login(username, password)
            with open(f"{username}_cookies.json", "w") as f:
                json.dump(login_cookies, f)

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

    student_info = make_request(
        "https://klas.kw.ac.kr/std/cps/inqire/AtnlcScreHakjukInfo.do",
        login_cookies,
    )
    grades = make_request(
        "https://klas.kw.ac.kr/std/cps/inqire/AtnlcScreSungjukTot.do",
        login_cookies,
    )

    grades_for_each_semester = make_request(
        "https://klas.kw.ac.kr/std/cps/inqire/AtnlcScreSungjukInfo.do",
        login_cookies,
    )
    semester = 0
    for semester_info in grades_for_each_semester:
        if semester_info.get("hakgiOrder") == "계절학기(동계)":
            continue
        semester += 1

    grade = student_info.get("grade")
    student_id = student_info.get("hakbun")
    major = student_info.get("hakgwa")
    student_name = student_info.get("kname")

    student_credits = grades.get("chidukHakjum")
    total_credits = 133
    total_major_credits = 60
    total_elective_credits = 30

    elective_credits = grades.get("cultureChidukHakjum")
    major_credits = grades.get("majorChidukHakjum")

    average_score = grades.get("jaechulScoresum")

    credits_ratio = round((student_credits / total_credits) * 100, 2)
    major_credits_ratio = round((major_credits / total_major_credits) * 100, 2)
    elective_credits_ratio = round((elective_credits / total_elective_credits) * 100, 2)

    credits_for_left_semesters = round(
        (total_credits - student_credits) / (4 * 2 - semester + 1), 2
    )
    major_credits_for_left_semesters = round(
        (total_major_credits - major_credits) / (4 * 2 - semester + 1), 2
    )

    return {
        "uid": student_id,
        "name": student_name,
        "major": major,
        "grade": grade,
        "semester": semester,
        "credits": {
            "total": student_credits,
            "required": total_credits,
            "ratio": credits_ratio,
        },
        "major_credits": {
            "total": major_credits,
            "required": total_major_credits,
            "ratio": major_credits_ratio,
        },
        "elective_credits": {
            "total": elective_credits,
            "required": total_elective_credits,
        },
        "average_score": average_score,
        "credits_for_left_semesters": credits_for_left_semesters,
        "major_credits_for_left_semesters": major_credits_for_left_semesters,
    }

    # response = requests.get(
    #     "https://klas.kw.ac.kr/spv/cmn/reprt/GraduateKecStd.do",
    #     cookies=login_cookies,
    # )
    # if response.status_code == 200:
    #     # Open a new file in write-binary mode
    #     with open("response.html", "wb") as file:
    #         file.write(response.content)
    #     print("The file was saved successfully!")
    # else:
    #     print(f"Failed to retrieve the page. Status code: {response.status_code}")


if __name__ == "__main__":

    get_test()
