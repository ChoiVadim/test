import logging
from flask import Flask, render_template, request, session, redirect, url_for
from src.kwuni import KwangwoonUniversityApi
from flask_sqlalchemy import SQLAlchemy
import datetime


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)

app = Flask(__name__)
db = SQLAlchemy()
app.secret_key = "your_secret_key_here"
db_uri = "sqlite:///chat.db"
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
db.init_app(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET"])
def index():
    kw = KwangwoonUniversityApi()
    if kw.login_with_cookies(session.get("cookies")):
        student_info = kw.get_student_info()
        photo_url = kw.get_student_photo_url()
        return render_template(
            "index.html", student_info=student_info, photo_url=photo_url
        )

    return render_template("login.html", error="")


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
            return render_template("login.html", error="Wrong username or password")

        return render_template(
            "index.html", student_info=student_info, photo_url=photo_url
        )
    return render_template("login.html", error="")


@app.route("/logout")
def logout():
    session.pop("cookies", None)
    return redirect(url_for("index"))


@app.route("/todo")
def todo():
    kw = KwangwoonUniversityApi()
    if kw.login_with_cookies(session.get("cookies")):
        todos = kw.get_todo_list()
        return render_template("todo.html", todos=todos)

    return render_template("login.html", error="")


@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        message = request.form.get("message")
        new_message = Message(content=message)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for("chat"))

    if request.method == "GET":
        messages = Message.query.order_by(Message.timestamp).all()
        return render_template("chat.html", messages=messages)


@app.route("/faq")
def faq():
    return render_template("faq.html")


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
