import os
import json
import logging
import datetime
import subprocess

import requests
from fake_useragent import UserAgent


class KwangwoonUniversityApi:
    def __init__(self) -> None:
        self.ua = UserAgent()
        self.session = requests.Session()
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": self.ua.random,
        }

        self.cookies = {}

    def _cookies_is_valid(self) -> bool:
        if not self.cookies:
            logging.error("No cookies found. Please log in first.")
            return False

        return True

    def set_cookies(self, cookies: dict):
        self.cookies = cookies

    def _encryptor(self, publicKey: str, phrase: str) -> str | None:
        js_path = os.path.join(self.current_dir, "js", "jsencryptor.js")

        try:
            result = subprocess.run(
                ["node", js_path, publicKey, phrase],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            output = result.stdout.decode("utf-8").strip()

            if not output:
                return None

            logging.debug(f"Encrypted output: {output}")
            return output

        except subprocess.CalledProcessError as e:
            logging.error(f"Error running Node.js script: {e}")
            logging.error(f"STDERR: {e.stderr}")
            return None

        except FileNotFoundError:
            logging.error("Node.js is not installed or not in the system PATH")
            return None

    def login(self, login_id: str, login_pwd: str) -> dict | None:
        login_form_url = "https://klas.kw.ac.kr/usr/cmn/login/LoginForm.do"
        public_key_url = "https://klas.kw.ac.kr/usr/cmn/login/LoginSecurity.do"
        login_url = "https://klas.kw.ac.kr/usr/cmn/login/LoginConfirm.do"

        self.session.get(login_form_url)
        public_key_response = self.session.get(public_key_url)

        public_key_json = public_key_response.json()
        public_key_str = public_key_json["publicKey"]

        login_data = {"loginId": login_id, "loginPwd": login_pwd, "storeIdYn": "Y"}
        login_json = json.dumps(login_data)

        try:
            encrypted_login = self._encryptor(public_key_str, login_json)
            if not encrypted_login:
                logging.error("Encryption failed")
                return None

            logging.info(f"Encrypted output: {encrypted_login}")

        except Exception as e:
            logging.error(f"An error occurred: {e}")

        login_body = {
            "loginToken": encrypted_login,
            "redirectUrl": "/std/cmn/frame/Frame.do",
            "redirectTabUrl": "",
        }

        login_response = self.session.post(
            login_url,
            json=login_body,
            headers=self.headers,
            cookies=self.session.cookies,
        )

        if login_response.status_code == 200:
            response_data = login_response.json()
            if response_data.get("errorCount", 0) == 0:
                logging.info("Login successful.")
                self.cookies = {
                    cookie.name: cookie.value for cookie in self.session.cookies
                }

            else:
                logging.error("Failed to parse response. Login failed.")
                return "Wrong password or ID"

        else:
            logging.error("Failed to communicate with server.")
            logging.error(f"Status code: {login_response.status_code}")
            return None

    def get_subjects(self) -> dict:
        if not self._cookies_is_valid():
            return None

        url = "https://klas.kw.ac.kr/std/cmn/frame/YearhakgiAtnlcSbjectList.do"

        response = self.session.post(
            url=url, headers=self.headers, cookies=self.cookies, json={}
        )

        if response.status_code == 200:
            response_data = response.json()
            logging.info(f"Data about subjects retrieved successfully.")
            # Return the last semester data, remove 0 if you want to get all
            return response_data[0]

        else:
            logging.error(
                f"Failed to retrieve data. Status code: {response.status_code}"
            )

    def _make_lecture_request(
        self, url: str, subject_id: str, year: str
    ) -> dict | None:
        if not self._cookies_is_valid():
            return None

        requests_body = {
            "selectSubj": subject_id,
            "selectYearhakgi": year,
            "selectChangeYn": "Y",
        }

        response = self.session.post(
            url=url, json=requests_body, headers=self.headers, cookies=self.cookies
        )

        if response.status_code == 200:
            return response.json()

        return None

    def _get_lectures(self, subject_id: str, year: str) -> dict | None:
        lectures_url = (
            "https://klas.kw.ac.kr/std/lis/evltn/SelectOnlineCntntsStdList.do"
        )
        return self._make_lecture_request(lectures_url, subject_id, year)

    def _get_homeworks(self, subject_id: str, year: str) -> dict | None:
        homeworks_url = "https://klas.kw.ac.kr/std/lis/evltn/TaskStdList.do"
        return self._make_lecture_request(homeworks_url, subject_id, year)

    def _get_team_projects(self, subject_id: str, year: str) -> dict | None:
        team_projects_url = "https://klas.kw.ac.kr/std/lis/evltn/PrjctStdList.do"
        return self._make_lecture_request(team_projects_url, subject_id, year)

    def _get_quizzes(self, subject_id: str, year: str) -> dict | None:
        quizzes_url = "https://klas.kw.ac.kr/std/lis/evltn/AnytmQuizStdList.do"
        return self._make_lecture_request(quizzes_url, subject_id, year)

    def _get_not_done_lectures_info(self, lectures: list[dict]) -> list[dict]:
        not_done_lectures = []
        for lecture in lectures:
            if (
                lecture.get("prog") is not None
                and lecture.get("prog") < 100
                and lecture.get("startDate")
                < datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            ):
                not_done_lectures.append(
                    {
                        "title": lecture.get("sbjt"),
                        "progress": lecture.get("prog"),
                        "expire_date": lecture.get("endDate"),
                        "left_time": self._get_left_time(
                            lecture.get("endDate"), "%Y-%m-%d %H:%M"
                        ),
                    }
                )
        return not_done_lectures

    def _get_not_done_homeworks_info(self, homeworks: list[dict]) -> list[dict]:
        not_done_homeworks = []
        for homework in homeworks:
            if homework.get("submityn") == "N":
                not_done_homeworks.append(
                    {
                        "title": homework.get("title"),
                        "expire_date": homework.get("expiredate"),
                        "left_time": self._get_left_time(
                            homework.get("expiredate"), "%Y-%m-%d %H:%M:%S"
                        ),
                    }
                )
        return not_done_homeworks

    def _get_not_done_team_projects_info(self, team_projects: list[dict]) -> list[dict]:
        not_done_team_projects = []
        for team_project in team_projects:
            if team_project.get("submityn") != "Y":
                not_done_team_projects.append(
                    {
                        "title": team_project.get("title"),
                        "expire_date": team_project.get("expiredate"),
                        "left_time": self._get_left_time(
                            team_project.get("expiredate"),
                            "%Y-%m-%dT%H:%M:%S.%f%z",
                            True,
                        ),
                    }
                )
        return not_done_team_projects

    def _get_not_done_quizzes_info(self, quizzes: list[dict]) -> list[dict]:
        not_done_quizzes = []
        for quiz in quizzes:
            if quiz.get("issubmit") == "N":
                not_done_quizzes.append(
                    {
                        "title": quiz.get("papernm"),
                        "expire_date": quiz.get("edt"),
                        "left_time": self._get_left_time(
                            quiz.get("edt"), "%Y-%m-%d %H:%M"
                        ),
                    }
                )
        return not_done_quizzes

    def _get_left_time(self, expire_date, date_format, remove_timezone=False):
        expire_date_time = datetime.datetime.strptime(expire_date, date_format)
        if remove_timezone:
            expire_date_time = expire_date_time.replace(tzinfo=None)
        now_time = datetime.datetime.now()
        return expire_date_time - now_time

    def get_todo_list(self) -> list[dict] | None:
        if not self._cookies_is_valid():
            return None

        subjects = self.get_subjects()
        if not subjects:
            return None

        todo_list = [
            {"id": subject.get("value"), "name": subject.get("name"), "todo": {}}
            for subject in subjects.get("subjList")
        ]

        try:
            subject_semester = subjects.get("value")

            for todo in todo_list:
                year = subject_semester
                subject_id = todo.get("id")

                lectures = self._get_lectures(subject_id, year)
                homeworks = self._get_homeworks(subject_id, year)
                team_projects = self._get_team_projects(subject_id, year)
                quizzes = self._get_quizzes(subject_id, year)

                todo["todo"] = {
                    "lectures": self._get_not_done_lectures_info(lectures),
                    "homeworks": self._get_not_done_homeworks_info(homeworks),
                    "team_projects": self._get_not_done_team_projects_info(
                        team_projects
                    ),
                    "quizzes": self._get_not_done_quizzes_info(quizzes),
                }

            return todo_list

        except Exception as e:
            logging.error(f"An error occurred while getting todo list: {e}")

    def _make_student_info_request(self, url: str) -> dict | None:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": self.ua.random,
        }

        response = self.session.post(
            url=url, json={}, headers=headers, cookies=self.cookies
        )

        if response.status_code == 200:
            return response.json()

        return None

    def get_student_info(self) -> dict | None:
        if not self._cookies_is_valid():
            return None

        student_info = self._make_student_info_request(
            "https://klas.kw.ac.kr/std/cps/inqire/AtnlcScreHakjukInfo.do",
        )
        grades = self._make_student_info_request(
            "https://klas.kw.ac.kr/std/cps/inqire/AtnlcScreSungjukTot.do",
        )

        grades_for_each_semester = self._make_student_info_request(
            "https://klas.kw.ac.kr/std/cps/inqire/AtnlcScreSungjukInfo.do",
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

        credits_for_each_semester = round(
            (total_credits - student_credits) / (4 * 2 - semester + 1), 2
        )
        major_credits_for_each_semester = round(
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
            "credits_for_each_semester": credits_for_each_semester,
            "major_credits_for_each_semester": major_credits_for_each_semester,
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from pprint import pprint

    student = KwangwoonUniversityApi()
    student.login("", "")
    pprint(student.get_todo_list())
