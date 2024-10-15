import requests
from fake_useragent import UserAgent
import datetime

ua = UserAgent()


def get_todo_list(cookies, subject_id, year):
    lectures_url = "https://klas.kw.ac.kr/std/lis/evltn/SelectOnlineCntntsStdList.do"
    homeworks_url = "https://klas.kw.ac.kr/std/lis/evltn/TaskStdList.do"
    team_projects_url = "https://klas.kw.ac.kr/std/lis/evltn/PrjctStdList.do"

    requests_body = {
        "selectSubj": subject_id,
        "selectYearhakgi": year,
        "selectChangeYn": "Y",
    }

    session = requests.Session()

    headers = {
        "Content-Type": "application/json",
        "User-Agent": ua.random,
    }

    response = session.post(
        url=lectures_url, json=requests_body, headers=headers, cookies=cookies
    )

    lecture_count = 0
    homework_count = 0
    team_project_count = 0

    if response.status_code == 200:
        data = response.json()
        for task in data:
            if task.get("prog") is not None:
                if task.get("prog") < 100:
                    lecture_count += 1

    response = session.post(
        url=homeworks_url, json=requests_body, headers=headers, cookies=cookies
    )

    if response.status_code == 200:
        data = response.json()
        for task in data:
            if task.get("indate") == "Y":
                homework_count += 1
                expire_date = task.get("expiredate")

                if expire_date:
                    expire_date_time = datetime.datetime.strptime(
                        expire_date, "%Y-%m-%d %H:%M:%S"
                    )
                    now_time = datetime.datetime.now()
                    left_time = expire_date_time - now_time
                    print(f"{left_time.days} days left: {task.get('title')}", end=" ")

    response = session.post(
        url=team_projects_url, json=requests_body, headers=headers, cookies=cookies
    )

    if response.status_code == 200:
        data = response.json()
        for task in data:
            if task.get("submityn") == "N":
                team_project_count += 1

    if lecture_count != 0:
        print("Lectures: ", lecture_count)
    if homework_count != 0:
        print("Homeworks: ", homework_count)
    if team_project_count != 0:
        print("Team Projects: ", team_project_count)
