from flask import Flask, render_template, request
from test import get_test
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
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
        student_info = get_test(username, password)
        logging.info(student_info)

        return render_template("index.html", student_info=student_info)
    return render_template("login.html")


if __name__ == "__main__":
    app.run()
