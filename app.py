# Имопртирование библиотек
from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


# Создание веб-приложения
app = Flask(__name__)
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

# def __repr__(self):
#     return "<Article %r>" % self.id


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
def hello():
    # Подгружаем html страничку
    return render_template("index.html")


@app.post("/register")
def register_response():
    try:
        data = request.get_json()  # Получаем JSON данные
        name = data.get("name")
        email = data.get("email")
        number = data.get("number")
        telegramm_connect = data.get("telegramm_connect")
        password = data.get("password")

        if not data:
            return jsonify({"message": "Нет данных"}), 400

        user = User(
            name=name,
            email=email,
            number=number,
            telegramm_connect=telegramm_connect,
            password=password,
        )
        try:
            # Пытаемся добавить статью в БД
            db.session.add(user)
            db.session.commit()
            # Перенаправляем пользователя на главную страничку
            return (
                jsonify(
                    {
                        "message": f"Пользователь добавлен в БД email: {email} pass: {password}"
                    }
                ),
                200,
            )
        except:
            # Выдаем ошибку если что-то не так
            return jsonify({"message": "Такой пользователь уже есть в БД"}), 402

        # Возвращаем JSON ответ

    except Exception as e:
        return jsonify({"message": f"Ошибка: {str(e)}"}), 500


# Регистрация
@app.route("/register")
def register():
    # # Проверяем запрос
    # if request.method == "POST":
    #     name = request.form["name"]
    #     email = request.form["email"]
    #     number = request.form["number"]
    #     telegramm_connect = request.form["telegramm_connect"]
    #     password = request.form["password"]
    #     confirm_password = request.form["confirm_password"]

    #     user = User(
    #         name=name,
    #         email=email,
    #         number=number,
    #         telegramm_connect=telegramm_connect,
    #         password=password,
    #     )

    #     try:
    #         # Пытаемся добавить статью в БД
    #         db.session.add(user)
    #         db.session.commit()
    #         # Перенаправляем пользователя на главную страничку
    #         return redirect("/home")
    #     except:
    #         # Выдаем ошибку если что-то не так
    #         return "Ошибка при добавлении пользователя :("

    # else:
    #     # Подгружаем html страничку
    #     return render_template("register.html")
    return render_template("register.html")


# Вход
@app.route("/login")
def login():
    # Подгружаем html страничку
    return render_template("login.html")


# # Вывод всех статей
# @app.route("/feed")
# def feed():
#     # Берем из базы данных статьи и сортируем по дате
#     articles = Book.query.order_by(Book.id.desc()).all()
#     return render_template("feed.html", articles=articles)


# # Офромление полной статьи
# @app.route("/feed/<int:id>")
# def feed_detail(id):
#     article = Article.query.get_or_404(id)
#     return render_template("feed_detail.html", article=article)


# # Удаление статьи
# @app.route("/feed/<int:id>/delete")
# def feed_del(id):
#     article = Article.query.get_or_404(id)

#     try:
#         db.session.delete(article)
#         db.session.commit()
#         return redirect("/feed")

#     except:
#         return "Error with delete article :("
#         # return "Error with delete article :(", {"Refresh": "2; url=/feed/<int:id>/"}


# # Изменение статьи для добавления статей в БД
# @app.route("/feed/<int:id>/update", methods=["POST", "GET"])
# def feed_update(id):
#     article = Article.query.get_or_404(id)
#     # Проверяем запрос
#     if request.method == "POST":
#         article.title = request.form["title"]
#         article.intro = request.form["intro"]
#         article.text = request.form["text"]

#         try:
#             # Пытаемся добавить статью в БД
#             db.session.commit()
#             # Перенаправляем пользователя на главную страничку
#             return redirect("/feed")
#         except:
#             # Выдаем ошибку если что-то не так
#             return "error with add article :("
#     else:
#         return render_template("feed_update.html", article=article)


# # Создание статьи для добавления статей в БД
# @app.route("/create", methods=["POST", "GET"])
# def create():
#     # Проверяем запрос
#     if request.method == "POST":
#         title = request.form["title"]
#         intro = request.form["intro"]
#         text = request.form["text"]

#         article = Book(title=title, intro=intro, text=text)

#         try:
#             # Пытаемся добавить статью в БД
#             db.session.add(article)
#             db.session.commit()
#             # Перенаправляем пользователя на главную страничку
#             return redirect("/feed")
#         except:
#             # Выдаем ошибку если что-то не так
#             return "error with add article :("
#     else:
#         # Подгружаем html страничку
#         return render_template("create.html")


# @app.route("/user/<string:name>/")
# def user(name):
#     return f"User page name - {name} "

# Загрузка
if __name__ == "__main__":
    app.run(debug=True)
