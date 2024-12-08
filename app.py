# Имопртирование библиотек
from flask import Flask, render_template, url_for, request, redirect, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

# Случайный 32-символьный ключ
SECRET_KEY = secrets.token_hex(16)
print(SECRET_KEY)
# Создание веб-приложения
app = Flask(__name__)
app.secret_key = SECRET_KEY
# Настройки для работы сервера и сайта
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///base.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Создание базы дынных
db = SQLAlchemy(app)


# Создание класса в базе данных
# class Book(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     intro = db.Column(db.String(300), nullable=False)
#     text = db.Column(db.Text, nullable=False)
#     date = db.Column(db.String, default=datetime.today().strftime("%d/%m/%y %H:%M"))


# Создаем объект базы данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    number = db.Column(db.String(12), nullable=False, unique=True)
    telegramm_connect = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)


# Создание главной странички
@app.route("/")
@app.route("/home")
def home():
    # Проверяем, авторизован ли пользователь
    user_name = session.get("user_name")

    if user_name:
        return render_template("home.html", user_name=user_name)
    else:
        # Перенаправляем на страницу входа, если пользователь не авторизован
        return redirect("/login")


# Создание страничку регистрации
@app.route("/register")
def register():
    return render_template("register.html")


# Пост обработка странички регистрации
@app.post("/register")
def register_response():
    try:
        # пробуем считать форму(данные) с сайта
        data = request.get_json()  # Получаем JSON данные
        name = data.get("name")
        email = data.get("email")
        number = data.get("number")
        telegramm_connect = data.get("telegramm_connect")
        password = data.get("password")

        # Если данных нет, выводим ошибку в консоль в браузере
        if not data:
            return jsonify({"message": "Нет данных"}), 400

        # Проверяем есть ли такой пользователь уже в БД
        existing_user = User.query.filter(
            (User.email == email) | (User.number == number)
        ).first()

        # Если такой пользователь уже есть, то выводим ошибку
        if existing_user:
            return jsonify({"message": "Такой пользователь уже есть в БД"}), 409

        # Объект базы данных
        user = User(
            name=name,
            email=email,
            number=number,
            telegramm_connect=telegramm_connect,
            password=password,
        )

        # Пытаемся добавить статью в БД
        db.session.add(user)
        db.session.commit()
        # Возвращаем хороший протокол
        return (
            jsonify(
                {
                    "message": f"Пользователь добавлен в БД email: ({email} pass: {password})"
                }
            ),
            200,
        )
    # В противном случае возвращаем любую другую ошибку
    except Exception as e:
        return jsonify({"message": f"Ошибка: {str(e)}"}), 500


# Создаем страничку входа
@app.route("/login")
def login():
    # Подгружаем html страничку
    return render_template("login.html")


@app.post("/login")
def login_response():
    try:
        data = request.get_json()  # Получаем JSON данные
        email = data.get("email")
        password = data.get("password")

        # Если данных нет, выводим ошибку в консоль в браузере
        if not data:
            return jsonify({"message": "Нет данных"}), 400

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            if existing_user.password == password:
                session["user_id"] = existing_user.id
                session["user_name"] = existing_user.name
                session["user_email"] = existing_user.email

                return (
                    jsonify(
                        {
                            "message": f"Вы успешно вошли в аккаунт {email}. Добро пожаловать, {existing_user.name}!"
                        }
                    ),
                    200,
                )
            else:
                return jsonify({"message": "Пароли не совпадают!"}), 401
        else:
            return (
                jsonify({"message": f"Пользователя с почтой {email} не существует"}),
                404,
            )

    except Exception as e:
        return jsonify({"message": f"Ошибка: {str(e)}"}), 500


# Загрузка
if __name__ == "__main__":
    app.run(debug=True)
