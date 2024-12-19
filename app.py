# Имопртирование библиотек
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    redirect,
    jsonify,
    session,
    send_file,
)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import base64
import io

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
class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    volume = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(30), nullable=False)
    age_limit = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(100), nullable=True)


# Создаем объект базы данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    number = db.Column(db.String(12), nullable=False, unique=True)
    telegramm_connect = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)


@app.route("/book_detail/<int:book_id>")
def book_details(book_id):
    user_name = session.get("user_name")
    book = Books.query.get_or_404(book_id)
    return render_template("book_detail.html", book=book, user_name=user_name)


@app.route("/img_book/<int:book_id>")
def get_image_book(book_id):
    book = Books.query.get_or_404(book_id)
    if book.image:
        return send_file(
            io.BytesIO(book.image),  # Создаем поток из бинарных данных изображения
            mimetype="image/jpeg",  # Указываем MIME-тип
            as_attachment=False,  # Показываем изображение в браузере
        )
    else:
        return "", 404


@app.get("/addbook")
def addbook():
    user_name = session.get("user_name")
    return render_template("addbook.html", user_name=user_name)


@app.post("/addbook")
def addbook_response():
    try:
        data = request.get_json()

        title = data.get("title")
        author = data.get("author")
        description = data.get("description")
        volume = data.get("volume")
        genre = data.get("genre")
        age_limit = data.get("age_limit")
        imageBase64 = data.get("image")

        image = None
        # print(title, author, description, volume, genre, age_limit)

        if imageBase64:
            image_filename = f"{title.replace(' ', '_')}.jpg"
            # Убираем префикс data:image/*
            image = base64.b64decode(imageBase64.split(",")[1])
            print("test image")

        new_book = Books(
            title=title,
            author=author,
            description=description,
            volume=volume,
            genre=genre,
            age_limit=age_limit,
            image=image,
        )
        # book = Books.query.get_or_404(5)
        # db.session.delete(book)
        # book = Books.query.get_or_404(6)
        # db.session.delete(book)
        # book = Books.query.get_or_404(7)
        # db.session.delete(book)
        # book = Books.query.get_or_404(8)
        # db.session.delete(book)
        # db.session.commit()
        db.session.add(new_book)
        db.session.commit()

        return jsonify({"message": "Книга успешно добавлена!"}), 200
    except Exception as e:
        return jsonify({"message": f"Ошибка: {str(e)}"}), 500


@app.route("/logout")
def logout():
    session.clear()  # Очистка данных сессии
    return redirect("/login")  # Перенаправление на страницу входа


# Создание главной странички
@app.route("/")
@app.route("/home")
def home():
    # Проверяем, авторизован ли пользователь
    user_name = session.get("user_name")

    if user_name:
        # Получение всех книг из базы данных
        books = Books.query.all()
        return render_template("home.html", user_name=user_name, books=books)
    else:
        # Перенаправляем на страницу входа, если пользователь не авторизован
        return redirect("/login")


@app.get("/profile")
def profile():
    user_name = session.get("user_name")
    user_email = session.get("user_email")
    user_number = session.get("user_number")
    user_telegramm = session.get("user_telegramm")
    user_pass = session.get("user_pass")

    return render_template(
        "profile.html",
        user_name=user_name,
        user_email=user_email,
        user_number=user_number,
        user_telegramm=user_telegramm,
        user_pass=user_pass,
    )


@app.delete("/profile")
def profile_response():
    try:
        user_email = session.get("user_email")
        existing_user = User.query.filter_by(email=user_email).first()
        print(-1)
        if existing_user:
            print(0)
            db.session.delete(existing_user)
            print(1)
            db.session.commit()
            print(2)
            session.clear()
            print(3)
            return jsonify({"message": f"Аккаунт {user_email}, успешно удален!"}), 200
        else:
            print(4)
            return (
                jsonify(
                    {
                        "message": f"Полльзователя {user_email} не существует или вы не вошли в аккаунт"
                    }
                ),
                409,
            )
    except Exception as e:
        return jsonify({"message": f"Ошибка: {str(e)}"}), 500


# Создание страничку регистрации
@app.get("/register")
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
                    "message": f"Пользователь добавлен в БД email: (EMAIL: {email} PASSWORD: {password})"
                }
            ),
            200,
        )
    # В противном случае возвращаем любую другую ошибку
    except Exception as e:
        return jsonify({"message": f"Ошибка: {str(e)}"}), 500


# Создаем страничку входа
@app.get("/login")
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
                session["user_number"] = existing_user.number
                session["user_telegramm"] = existing_user.telegramm_connect
                session["user_pass"] = existing_user.password

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
