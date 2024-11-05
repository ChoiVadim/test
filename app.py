from flask import Flask, render_template, request
from test import get_test
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
    filename="main.log",
)
app = Flask(__name__)

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
