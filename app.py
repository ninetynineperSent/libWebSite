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
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import base64
import io
import random

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


def generate_code(length=6):
    return ''.join(random.choices('0123456789', k=length))


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
    is_admin = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.LargeBinary, nullable=True)


class BookOrder(db.Model):
    id_order = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, nullable=False)
    id_book = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='reserved')
    date_created = db.Column(db.DateTime, default=datetime.utcnow)  # когда создана бронь
    date_booked_until = db.Column(db.DateTime, nullable=False)  # до какого дня держат бронь
    date_borrowed = db.Column(db.DateTime, nullable=True)  # когда выдали
    date_due = db.Column(db.DateTime, nullable=True)  # до какого числа вернуть
    date_returned = db.Column(db.DateTime, nullable=True)  # когда вернул
    confirm_code = db.Column(db.String(16), nullable=True)  # поле для одноразового кода


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


@app.get("/admin/addbook")
def addbook():
    if not session.get("is_admin"):
        return redirect("/home")  # Только для админов!
    user_name = session.get("user_name")
    return render_template("addbook.html", user_name=user_name)


@app.post("/admin/addbook")
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

    return render_template(
        "profile.html",
        user_name=user_name,
        user_email=user_email,
        user_number=user_number,
        user_telegramm=user_telegramm,
    )


@app.post("/profile")
def profile_response():
    try:
        data = request.get_json()
        name = data.get("name")
        new_number = data.get("number")
        telegramm_connect = data.get("telegramm_connect")

        avatar_base64 = data.get("avatar")

        avatar = base64.b64decode(avatar_base64.split(",")[1]) if avatar_base64 else None

        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"message": "Неавторизован"}), 401

        user = User.query.get(user_id)
        if user:
            user.name = name
            user.number = new_number
            user.telegramm_connect = telegramm_connect
            if avatar:
                user.avatar = avatar
            db.session.commit()

            session["user_name"] = name
            session["user_number"] = new_number
            session["user_telegramm"] = telegramm_connect

            return jsonify({"message": "Профиль обновлён"}), 200
        else:
            return jsonify({"message": "Пользователь не найден"}), 404
    except Exception as e:
        return jsonify({"message": f"Ошибка: {str(e)}"}), 500


@app.route("/avatar/<int:user_id>")
def get_avatar(user_id):
    user = User.query.get_or_404(user_id)
    if user.avatar:
        return send_file(io.BytesIO(user.avatar), mimetype="image/jpeg", as_attachment=False)
    else:
        return "", 404


@app.delete("/profile")
def profile_delete():
    try:
        user_email = session.get("user_email")
        existing_user = User.query.filter_by(email=user_email).first()
        print(-1)
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
            session.clear()
            return jsonify({"message": f"Аккаунт {user_email}, успешно удален!"}), 200

        else:
            session.clear()
            return (
                jsonify({"message": f"Полльзователя {user_email} не существует или вы не вошли в аккаунт"}),
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
        password = generate_password_hash(data.get("password"))

        # Если данных нет, выводим ошибку в консоль в браузере
        if not data:
            return jsonify({"message": "Нет данных"}), 400

        # Проверяем есть ли такой пользователь уже в БД
        existing_user = User.query.filter((User.email == email) | (User.number == number)).first()

        # Если такой пользователь уже есть, то выводим ошибку
        if existing_user:
            return jsonify({"message": "Такой пользователь уже есть в БД"}), 409
        

        default_avatar = User.query.get_or_404(4).avatar
        
        # Объект базы данных
        user = User(
            name=name,
            email=email,
            number=number,
            telegramm_connect=telegramm_connect,
            password=password,
            avatar=default_avatar,
        )

        # Пытаемся добавить статью в БД
        db.session.add(user)
        db.session.commit()
        # Возвращаем хороший протокол
        return (
            jsonify({"message": f"Пользователь добавлен в БД email: (EMAIL: {email} PASSWORD: {password})"}),
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
            if check_password_hash(existing_user.password, password):
                session["user_id"] = existing_user.id
                session["user_name"] = existing_user.name
                session["user_email"] = existing_user.email
                session["user_number"] = existing_user.number
                session["user_telegramm"] = existing_user.telegramm_connect
                session['is_admin'] = existing_user.is_admin

                return (
                    jsonify({"message": f"Вы успешно вошли в аккаунт {email}. Добро пожаловать, {existing_user.name}!"}),
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


@app.get("/about")
def about():
    user_name = session.get("user_name")

    if user_name:
        # Получение всех книг из базы данных
        return render_template("about.html", user_name=user_name)
    else:
        # Перенаправляем на страницу входа, если пользователь не авторизован
        return redirect("/login")


@app.get("/mybooks")
def mybooks():
    user_name = session.get("user_name")
    user_id = session.get("user_id")
    if not user_name:
        return redirect("/login")
    # Получаем все заказы этого пользователя, JOIN-ом подтягиваем книги
    orders = BookOrder.query.filter_by(id_user=user_id).order_by(BookOrder.date_created.desc()).all()

    # Чтобы подтянуть объект книги:
    for order in orders:
        book = Books.query.get(order.id_book)
        order.book_title = book.title
        order.book_image_url = f"/img_book/{book.id}"
        order.book = Books.query.get(order.id_book)
        # print(order.book)
    return render_template("mybooks.html", user_name=user_name, orders=orders)


# 1. Забронировать книгу (reserve)
@app.route('/reserve_book', methods=['POST'])
def reserve_book():
    if not session.get('user_id'):
        return jsonify({'message': 'Авторизуйтесь!'}), 401
    data = request.get_json()
    book_id = data.get('book_id')
    date_until = data.get('date_booked_until')  # строка: '2024-06-12'
    try:
        user_id = session['user_id']
        existing = BookOrder.query.filter_by(id_user=user_id, id_book=book_id, status='reserved').first()
        if existing:
            return jsonify({'message': 'Эта книга уже забронирована вами!'}), 409
        new_order = BookOrder(id_user=user_id, id_book=book_id, status='reserved', date_booked_until=datetime.strptime(date_until, '%Y-%m-%d'))
        db.session.add(new_order)
        db.session.commit()
        return jsonify({'message': 'Книга забронирована до ' + date_until}), 200
    except Exception as e:
        return jsonify({'message': 'Ошибка: ' + str(e)}), 500


# 2. Взять книгу (borrow)
@app.route('/borrow_book', methods=['POST'])
def borrow_book():
    if not session.get('user_id'):
        return jsonify({'message': 'Авторизуйтесь!'}), 401
    data = request.get_json()
    order_id = data.get('order_id')
    days = int(data.get('days', 14))
    user_code = data.get('code')

    try:
        order = BookOrder.query.filter_by(id_order=order_id, id_user=session['user_id'], status='reserved').first()
        if not order:
            return jsonify({'message': 'Бронь не найдена или уже выдана!'}), 404

        # Проверяем введённый пользователем код
        if user_code != order.confirm_code:
            return jsonify({'message': 'Неверный код подтверждения!'}), 403

        now = datetime.utcnow()
        order.status = 'borrowed'
        order.date_borrowed = now
        order.date_due = now + timedelta(days=days)
        db.session.commit()
        return jsonify({'message': f'Книга выдана до {order.date_due.strftime("%Y-%m-%d")}'}), 200
    except Exception as e:
        return jsonify({'message': 'Ошибка: ' + str(e)}), 500


# 3. Вернуть книгу (return)
@app.route('/return_book', methods=['POST'])
def return_book():
    if not session.get('user_id'):
        return jsonify({'message': 'Авторизуйтесь!'}), 401
    data = request.get_json()
    order_id = data.get('order_id')  # ID заказа
    try:
        order = BookOrder.query.filter_by(id_order=order_id, id_user=session['user_id'], status='borrowed').first()
        if not order:
            return jsonify({'message': 'Книга не была выдана или уже возвращена!'}), 404
        order.status = 'confirm_returned'  # <--- Меняем статус на confirm_returned!
        db.session.commit()
        return jsonify({'message': 'Запрос на возврат отправлен админу!'}), 200
    except Exception as e:
        return jsonify({'message': 'Ошибка: ' + str(e)}), 500


# 4. (Опционально) Отменить бронь (cancel)
@app.route('/cancel_reservation', methods=['POST'])
def cancel_reservation():
    if not session.get('user_id'):
        return jsonify({'message': 'Авторизуйтесь!'}), 401
    data = request.get_json()
    order_id = data.get('order_id')
    try:
        order = BookOrder.query.filter_by(id_order=order_id, id_user=session['user_id'], status='reserved').first()
        if not order:
            return jsonify({'message': 'Бронь не найдена!'}), 404
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'Бронь отменена!'}), 200
    except Exception as e:
        return jsonify({'message': 'Ошибка: ' + str(e)}), 500


@app.route('/admin/notifications')
def admin_notifications():
    if not session.get("is_admin"):
        return redirect("/home")  # Только для админов!
    # Показываем заказы, где нужно действие админа (пример: confirm_returned или ожидают кода)
    orders = BookOrder.query.filter(BookOrder.status.in_(['confirm_returned', 'reserved'])).order_by(BookOrder.date_due.desc()).all()
    for order in orders:
        user = User.query.get(order.id_user)
        book = Books.query.get(order.id_book)
        order.user_name = user.name if user else "Неизвестно"
        order.book_title = book.title if book else "Без названия"
    return render_template("admin_notifications.html", orders=orders)


@app.route('/admin/approve_return', methods=['POST'])
def admin_approve_return():
    if not session.get("is_admin"):
        return jsonify({'message': 'Доступ только для админа!'}), 403
    data = request.get_json()
    order_id = data.get('order_id')
    order = BookOrder.query.get(order_id)
    if not order or order.status != 'confirm_returned':
        return jsonify({'message': 'Неверный статус заказа!'}), 400
    order.status = 'returned'
    order.date_returned = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Возврат подтвержден!'}), 200


@app.route('/admin/reject_return', methods=['POST'])
def admin_reject_return():
    if not session.get("is_admin"):
        return jsonify({'message': 'Доступ только для админа!'}), 403
    data = request.get_json()
    order_id = data.get('order_id')
    order = BookOrder.query.get(order_id)
    if not order or order.status != 'confirm_returned':
        return jsonify({'message': 'Неверный статус заказа!'}), 400
    order.status = 'borrowed'
    db.session.commit()
    return jsonify({'message': 'Запрос на возврат отклонён!'}), 200


@app.route('/api/generate_code', methods=['POST'])
def api_generate_code():
    if not session.get('user_id'):
        return jsonify({'message': 'Авторизуйтесь!'}), 401
    data = request.get_json()
    order_id = data.get('order_id')
    order = BookOrder.query.filter_by(id_order=order_id, id_user=session['user_id'], status='reserved').first()
    if not order:
        return jsonify({'message': 'Бронь не найдена!'}), 404
    code = generate_code()
    order.confirm_code = code
    db.session.commit()
    # Код увидит только админ!
    return jsonify({'success': True})


@app.route('/api/reset_code', methods=['POST'])
def api_reset_code():
    if not session.get('user_id'):
        return jsonify({'message': 'Авторизуйтесь!'}), 401
    data = request.get_json()
    order_id = data.get('order_id')
    order = BookOrder.query.filter_by(id_order=order_id, id_user=session['user_id'], status='reserved').first()
    if not order:
        return jsonify({'message': 'Бронь не найдена!'}), 404
    order.confirm_code = None
    db.session.commit()
    return jsonify({'success': True})


# Загрузка
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
