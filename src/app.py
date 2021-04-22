import os

from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import login_user, current_user, LoginManager
from flask_login import UserMixin
from uuid import uuid4

root_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"].encode()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(root_dir, 'test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'user_avatars')
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    avatar = db.Column(db.String(80))
    _password = db.Column(db.String(128))

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext):
        self._password = generate_password_hash(plaintext)

    def has_correct_password(self, plaintext):
        return check_password_hash(self._password, plaintext)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == user_id).first()


@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template("index.html")
    return redirect(url_for("login"))


# TODO flash errors
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("login", "")
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user is not None and user.has_correct_password(password):
            login_user(user)
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Wrong username or password. Try again")
    return render_template("login.html")


#  TODO add email verification (https://exploreflask.com/en/latest/users.html)
# noinspection PyArgumentList
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if request.files.get('img'):
            file = request.files['img']
            file_ext = "." + file.filename.rsplit('.', 1)[1].lower()
            filename = uuid4().hex + file_ext
            link_to_img = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(link_to_img)
        else:
            link_to_img = os.path.join("static", "assets", "img", "avatar_base.png")

        reg = User(username=username, email=email, password=password, avatar=link_to_img)
        db.session.add(reg)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("registration.html")


if __name__ == '__main__':
    db.create_all()
    app.run()
