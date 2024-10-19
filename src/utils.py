import requests
import datetime
from fake_useragent import UserAgent

ua = UserAgent()
session = requests.Session()


def make_request(url: str, cookies: dict, subject_id: str, year: str) -> dict | None:
    requests_body = {
        "selectSubj": subject_id,
        "selectYearhakgi": year,
        "selectChangeYn": "Y",
    }

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


def get_lectures(cookies: dict, subject_id: str, year: str) -> dict | None:
    lectures_url = "https://klas.kw.ac.kr/std/lis/evltn/SelectOnlineCntntsStdList.do"
    return make_request(lectures_url, cookies, subject_id, year)


def get_homeworks(cookies: dict, subject_id: str, year: str) -> dict | None:
    homeworks_url = "https://klas.kw.ac.kr/std/lis/evltn/TaskStdList.do"
    return make_request(homeworks_url, cookies, subject_id, year)


def get_team_projects(cookies: dict, subject_id: str, year: str) -> dict | None:
    team_projects_url = "https://klas.kw.ac.kr/std/lis/evltn/PrjctStdList.do"
    return make_request(team_projects_url, cookies, subject_id, year)


def get_quiz(cookies: dict, subject_id: str, year: str) -> dict | None:
    quiz_url = "https://klas.kw.ac.kr/std/lis/evltn/AnytmQuizStdList.do"
    return make_request(quiz_url, cookies, subject_id, year)


def get_todo_list(cookies, subject_id, year):
    lectures = get_lectures(cookies, subject_id, year)
    homeworks = get_homeworks(cookies, subject_id, year)
    team_projects = get_team_projects(cookies, subject_id, year)
    quizzes = get_quiz(cookies, subject_id, year)

    return {
        "lectures": get_not_done_lectures_info(lectures),
        "homeworks": get_not_done_homeworks_info(homeworks),
        "team_projects": get_not_done_team_projects_info(team_projects),
        "quizzes": get_not_done_quizzes_info(quizzes),
    }


def get_todo_list_left_time(cookies, subject_id, year):
    lectures = get_lectures(cookies, subject_id, year)
    homeworks = get_homeworks(cookies, subject_id, year)
    team_projects = get_team_projects(cookies, subject_id, year)
    quizzes = get_quiz(cookies, subject_id, year)

    return {
        "lectures": get_not_done_lectures_left_time(lectures),
        "homeworks": get_not_done_homeworks_left_time(homeworks),
        "team_projects": get_not_done_team_projects_left_time(team_projects),
        "quizzes": get_not_done_quizzes_left_time(quizzes),
    }


def get_not_done_lectures_info(lectures):
    not_done_lectures = []
    for lecture in lectures:
        if lecture.get("prog") is not None and lecture.get("prog") < 100:
            not_done_lectures.append(
                {
                    "title": lecture.get("sbjt"),
                    "progress": lecture.get("prog"),
                    "expire_date": lecture.get("endDate"),
                    "left_time": get_left_time(
                        lecture.get("endDate"), "%Y-%m-%d %H:%M"
                    ),
                }
            )
    return not_done_lectures


def get_not_done_lectures_left_time(lectures):
    return [
        get_left_time(lecture.get("endDate"), "%Y-%m-%d %H:%M")
        for lecture in lectures
        if lecture.get("prog") is not None
        and lecture.get("prog") < 100
        and lecture.get("endDate")
    ]


def get_not_done_homeworks_info(homeworks):
    not_done_homeworks = []
    for homework in homeworks:
        if homework.get("submityn") == "N":
            not_done_homeworks.append(
                {
                    "title": homework.get("title"),
                    "expire_date": homework.get("expiredate"),
                    "left_time": get_left_time(
                        homework.get("expiredate"), "%Y-%m-%d %H:%M:%S"
                    ),
                }
            )
    return not_done_homeworks


def get_not_done_homeworks_left_time(homeworks):
    return [
        get_left_time(homework.get("expiredate"), "%Y-%m-%d %H:%M:%S")
        for homework in homeworks
        if homework.get("submityn") == "N" and homework.get("expiredate")
    ]


def get_not_done_team_projects_info(team_projects):
    not_done_team_projects = []
    for team_project in team_projects:
        if team_project.get("submityn") != "Y":
            not_done_team_projects.append(
                {
                    "title": team_project.get("title"),
                    "expire_date": team_project.get("expiredate"),
                    "left_time": get_left_time(
                        team_project.get("expiredate"), "%Y-%m-%dT%H:%M:%S.%f%z", True
                    ),
                }
            )
    return not_done_team_projects


def get_not_done_team_projects_left_time(team_projects):
    return [
        get_left_time(team_project.get("expiredate"), "%Y-%m-%dT%H:%M:%S.%f%z", True)
        for team_project in team_projects
        if team_project.get("submityn") != "Y" and team_project.get("expiredate")
    ]


def get_not_done_quizzes_info(quizzes):
    not_done_quizzes = []
    for quiz in quizzes:
        if quiz.get("issubmit") == "N":
            not_done_quizzes.append(
                {
                    "title": quiz.get("papernm"),
                    "expire_date": quiz.get("edt"),
                    "left_time": get_left_time(quiz.get("edt"), "%Y-%m-%d %H:%M"),
                }
            )
    return not_done_quizzes


def get_not_done_quizzes_left_time(quizzes):
    return [
        get_left_time(quiz.get("edt"), "%Y-%m-%d %H:%M")
        for quiz in quizzes
        if quiz.get("issubmit") == "N" and quiz.get("edt")
    ]


def get_left_time(expire_date, date_format, remove_timezone=False):
    expire_date_time = datetime.datetime.strptime(expire_date, date_format)
    if remove_timezone:
        expire_date_time = expire_date_time.replace(tzinfo=None)
    now_time = datetime.datetime.now()
    return expire_date_time - now_time
