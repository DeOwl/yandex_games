from data import db_session
from data.users import User
from data.games import Game
from flask import Flask, request, render_template, redirect, url_for
from flask import session as server_session
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed

from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, FileField, RadioField
from wtforms.validators import DataRequired

from flask_ngrok import run_with_ngrok
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from werkzeug.utils import secure_filename
import os
import datetime


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'img', 'users')
app = Flask(__name__)
run_with_ngrok(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
db_session.global_init('db/db.sqlite')
login_manager = LoginManager()
login_manager.init_app(app)



class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField('Repeat password', validators=[DataRequired()])
    username = StringField('username', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CheckoutForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    phone = StringField("номер телефона(+7(123)123-12-12)", validators=[DataRequired()])
    adress = StringField("адрес", validators=[DataRequired()])
    payment = RadioField(label="способо оплаты", validators=[DataRequired()], choices=[("карта", "карта"), ("наличные", "наличные")])
    submit = SubmitField("оформить заказ")


class UploadForm(FlaskForm):
    file = FileField("фото профиля")
    phone = StringField("номер телефона(+7(123)123-12-12)")
    adress = StringField("адрес")

@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/')
def main_page():
    if "message" in server_session:
        server_session["message"] = ""
    session = db_session.create_session()
    games = session.query(Game)
    return render_template("main_page.html", current_user=current_user, games=games)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form, current_user=current_user)
    return render_template('login.html', title='Авторизация', form=form, current_user=current_user)


@app.route('/register', methods=["GET", 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают", current_user=current_user)
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть", current_user=current_user)
        user = User(
            email=form.email.data,
            username=form.username.data,
            hashed_password=form.password.data,
            phone="",
            adress=""
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        login_user(user)
        return redirect("/")
    return render_template('register.html', title='Регистрация', form=form, current_user=current_user)

@app.route('/games/<gameid>')
def game(gameid):
    session = db_session.create_session()
    game = session.query(Game).filter(Game.id == gameid).first()
    message = ""
    if "message" in server_session:
        message = server_session["message"]
        server_session["message"] = ""
    return render_template('game_page.html', current_user=current_user, game=game, message=message)


@app.route("/delete_all_users")
def delete_all():
    session = db_session.create_session()
    session.query(User).delete()
    session.commit()
    return redirect("/")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/user', methods=["GET", 'POST'])
@login_required
def user_page():

    return render_template("user.html", user=current_user)


@app.route("/user/change_photo", methods=["GET", 'POST'])
def change_profile():
    form = UploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        form.file.data.save(
            os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id) + "." + filename.split(".")[-1]))
        session = db_session.create_session()
        user = session.query(User).filter(User.id == current_user.id).first()
        user.image = "/static/img/users/" + str(user.id) + "." + filename.split(".")[-1]
        if form.adress.data:
            user.adress = form.adress.data
        if form.phone.data:
            user.phone = form.phone.data
        session.commit()
        return redirect("/user")
    return render_template("user_change.html", user=current_user, form=form)


@app.route("/games/add_game/<id>/<source>")
def add_game_to_session(id, source):
    server_session["message"] = "вы добавили игру в корзину"
    if "games" in server_session:
        server_session["games"] += [id]
    else:
        server_session["games"] = [id]
    if source == "game":
        return redirect("/games/" + str(id))
    elif source == "cart":
        return redirect("/cart")

@app.route("/games/remove_game/<id>/<source>")
def remove_game_to_session(id, source):
    server_session["message"] = "вы добавили игру в корзину"
    if "games" in server_session:
        server_session["games"].remove(id)
    else:
        server_session["games"] = [id]
    if source == "game":
        return redirect("/games/" + str(id))
    elif source == "cart":
        return redirect("/cart")


@app.route("/cart")
def cart():
    if "games" not in server_session:
        server_session["games"] = []
    games = []
    session = db_session.create_session()
    amount = dict()
    price = dict()
    total = 0

    for game in server_session["games"]:

        game_got = session.query(Game).filter(Game.id==game).first()
        if game_got not in games:
            games.append(game_got)
            amount[game] = 1
            price[game] = game_got.cost
            total += game_got.cost
        else:
            amount[game] += 1
            price[game] += game_got.cost
            total += game_got.cost
    print(price)
    return render_template("cart.html", games=games, amount=amount, price=price, total=total)


@app.route("/checkout", methods=["GET", 'POST'])
def checkout():
    form = CheckoutForm()

    if current_user.is_authenticated:
        session = db_session.create_session()
        person = session.query(User).filter(current_user.id == current_user.id).first()
        form.email.data = person.email
        form.adress.data = person.adress
        form.phone.data = person.phone
    if form.validate_on_submit():
        if "games" in server_session:
            server_session["games"] = []
        return redirect("/")
    return render_template("checkout.html", user=current_user, form=form)


if __name__ == '__main__':
    app.run()