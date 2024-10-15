import datetime
import requests
from fake_useragent import UserAgent

ua = UserAgent()
session = requests.Session()


def get_lectures(cookies: dict, subject_id: str, year: str) -> dict | None:
    lectures_url = "https://klas.kw.ac.kr/std/lis/evltn/SelectOnlineCntntsStdList.do"

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
        url=lectures_url, json=requests_body, headers=headers, cookies=cookies
    )

    if response.status_code == 200:
        return response.json()

    return None


def get_homeworks(cookies: dict, subject_id: str, year: str) -> dict | None:
    homeworks_url = "https://klas.kw.ac.kr/std/lis/evltn/TaskStdList.do"

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
        url=homeworks_url, json=requests_body, headers=headers, cookies=cookies
    )

    if response.status_code == 200:
        return response.json()

    return None


def get_team_projects(cookies: dict, subject_id: str, year: str) -> dict | None:
    team_projects_url = "https://klas.kw.ac.kr/std/lis/evltn/PrjctStdList.do"

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
        url=team_projects_url, json=requests_body, headers=headers, cookies=cookies
    )

    if response.status_code == 200:
        return response.json()

    return None


def get_quiz(cookies: dict, subject_id: str, year: str) -> dict | None:
    quiz_url = "https://klas.kw.ac.kr/std/lis/evltn/AnytmQuizStdList.do"

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
        url=quiz_url, json=requests_body, headers=headers, cookies=cookies
    )

    if response.status_code == 200:
        return response.json()

    return None


def get_todo_list(cookies, subject_id, year):
    lectures = get_lectures(cookies, subject_id, year)
    homeworks = get_homeworks(cookies, subject_id, year)
    team_projects = get_team_projects(cookies, subject_id, year)
    quiz = get_quiz(cookies, subject_id, year)

    not_done_lectures = []
    for lecture in lectures:
        if lecture.get("prog") is not None:
            if lecture.get("prog") < 100:
                not_done_lectures.append(lecture)

    not_done_homeworks = []
    for homework in homeworks:
        if homework.get("indate") == "Y":
            not_done_homeworks.append(homework)
            # expire_date = homework.get("expiredate")

            # if expire_date:
            #     expire_date_time = datetime.datetime.strptime(
            #         expire_date, "%Y-%m-%d %H:%M:%S"
            #     )
            #     now_time = datetime.datetime.now()
            #     left_time = expire_date_time - now_time

    not_done_team_projects = []
    for team_project in team_projects:
        if team_project.get("submityn") != "Y":
            not_done_team_projects.append(team_project)

    not_done_quizzes = []
    for quiz in quiz:
        if quiz.get("issubmit") != "Y":
            not_done_quizzes.append(quiz)

    return {
        "lectures": not_done_lectures,
        "homeworks": not_done_homeworks,
        "team_projects": not_done_team_projects,
        "quizzes": not_done_quizzes,
    }
