import json
import logging
import requests
from fake_useragent import UserAgent


ua = UserAgent()


def get_subjects(login_cookies: dict) -> dict:
    url = "https://klas.kw.ac.kr/std/cmn/frame/YearhakgiAtnlcSbjectList.do"

    session = requests.Session()

    headers = {
        "Content-Type": "application/json",
        "User-Agent": ua.random,
    }

    response = session.post(url, headers=headers, cookies=login_cookies, json={})

    if response.status_code == 200:
        logging.debug(
            f"Data retrieved successfully. Status code: {response.status_code}"
        )
        data = response.json()
        logging.info(json.dumps(data, indent=4, ensure_ascii=False))
        return data[0]  # Return the last semester data, remove 0 if you want all

    else:
        logging.error(f"Failed to retrieve data. Status code: {response.status_code}")


def get_subject_info(login_cookies: dict, data: dict, subject_index: int) -> dict:
    url = "https://klas.kw.ac.kr/std/lis/evltn/LctrumHomeStdInfo.do"

    session = requests.Session()

    headers = {
        "Content-Type": "application/json",
        "User-Agent": ua.random,
    }

    subject_id = data.get("subjList")[subject_index].get("value")
    subject_label = data.get("subjList")[subject_index].get("label")
    subject_name = data.get("subjList")[subject_index].get("name")
    year = data.get("value")
    label = data.get("label")

    request_body = {
        "selectChangeYn": "Y",
        "selectSubj": subject_id,
        "selectYearhakgi": year,
        "subj": {
            "value": subject_id,
            "label": subject_label,
            "name": subject_name,
        },
        "subjNm": subject_label,
        "yearhakgi": {
            "value": year,
            "label": label,
            "subjList": data.get("subjList"),
        },
    }

    response = session.post(
        url, headers=headers, cookies=login_cookies, json=request_body
    )

    if response.status_code == 200:
        logging.debug("Data retrieved successfully!")
        data = response.json()
        logging.info(json.dumps(data, indent=4, ensure_ascii=False))
        return data

    else:
        logging.error(f"Failed to retrieve data. Status code: {response.status_code}")


def print_lecture_info(lecture_info):
    # Lecture
    viewed_lectures_count = lecture_info.get("cntntCmpltCnt")
    lectures_count = len(lecture_info.get("cntntList"))

    # Quiz
    done_quiz_count = lecture_info.get("quizPrsntCnt")
    undone_quiz_count = lecture_info.get("quizNewCnt")
    quiz_count = lecture_info.get("quizCnt")

    # Homework
    task_count = lecture_info.get("taskCnt")
    new_task_count = lecture_info.get("taskNewCnt")
    done_task_count = lecture_info.get("taskPrsntCnt")

    # Team Project
    project_count = lecture_info.get("prjctCnt")
    new_project_count = lecture_info.get("prjctNewCnt")
    done_project_count = lecture_info.get("prjctPrsntCnt")

    print(f"{f'Lecture: {viewed_lectures_count}/{lectures_count}':^80}")
    print(f"{f'Quiz: {done_quiz_count}/{quiz_count}':^80}")
    print(f"{f'Homework: {done_task_count}/{task_count}':^80}")
    print(f"{f'Team Project: {done_project_count}/{project_count}':^80}")


def update_lecture_progress(lecture_info: dict) -> None:
    url = "https://klas.kw.ac.kr/spv/lis/lctre/viewer/UpdateProgress.do"
    pass
