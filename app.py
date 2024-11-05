import logging
from flask import Flask, render_template, request
from src.kwuni import KwangwoonUniversityApi


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
    filename="main.log",
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        kw = KwangwoonUniversityApi()
        kw.login(username, password)
        student_info = kw.get_student_info(username, password)

        return render_template("index.html", student_info=student_info)
    return render_template("login.html")


if __name__ == "__main__":
    app.run()
