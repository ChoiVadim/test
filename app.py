import logging
from flask import Flask, render_template, request, session, redirect, url_for
from src.kwuni import KwangwoonUniversityApi


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)

app = Flask(__name__)
app.secret_key = "your_secret_key_here"


@app.route("/", methods=["GET"])
def index():
    if session["cookies"].get("SESSION", None):
        kw = KwangwoonUniversityApi()
        kw.set_cookies(session["cookies"])
        student_info = kw.get_student_info()
        photo_url = kw.get_student_photo_url()
        if student_info:
            return render_template(
                "index.html", student_info=student_info, photo_url=photo_url
            )

    return redirect(url_for("login", error=""))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        kw = KwangwoonUniversityApi()
        kw.login(username, password)
        student_info = kw.get_student_info()
        photo_url = kw.get_student_photo_url()
        print(photo_url)

        session["cookies"] = kw.cookies

        if not student_info:
            return render_template("login.html", error="Login failed")

        return render_template(
            "index.html", student_info=student_info, photo_url=photo_url
        )
    return render_template("login.html")


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
