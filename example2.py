import uuid
import requests
from flask import Flask, flash, get_flashed_messages, \
    url_for, render_template, request, redirect, session


app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"

BOOKS_API_URL = 'http://localhost:8000'

courses = [
    {'id': 42, 'name': 'Курс по Flask'},
]


# ------------------------------
# Валидация
# ------------------------------
def validate(user):
    errors = {}
    if not user["name"]:
        errors["name"] = "Can't be blank"
    elif len(user["name"]) < 5:
        errors["name"] = "Nickname must be greater than 4 characters"
    if not user["email"]:
        errors["email"] = "Can't send email"
    return errors


# ------------------------------
# Хелперы для работы с session
# ------------------------------
def get_users():
    return session.setdefault("users", [])


def save_users(users):
    session["users"] = users


# ------------------------------
# Роуты
# ------------------------------
@app.route("/")
def index():
    return render_template(
        "courses/index.html",
        courses=courses,
    )


@app.get("/users/")
def users_get():
    users = get_users()
    messages = get_flashed_messages(with_categories=True)
    query = request.args.get('query', '')
    filtered_users = [user for user in users if query in user['name']]
    return render_template(
        'users/index.html',
        users=filtered_users,
        search=query,
        messages=messages
    )


@app.post("/users")
def users_post():
    user_data = request.form.to_dict()
    errors = validate(user_data)
    if errors:
        for field, message in errors.items():
            flash(message, "error")
        return render_template(
            "users/new.html",
            user=user_data,
            errors=errors,
        ), 422

    user = {
        'id': str(uuid.uuid4()),
        'name': user_data['name'],
        'email': user_data['email']
    }
    users = get_users()
    users.append(user)
    save_users(users)

    flash('Пользователь успешно добавлен', 'success')
    return redirect(url_for('users_get'), code=302)


@app.route('/users/new')
def users_new():
    user = {'name': '', 'email': ''}
    errors = {}
    return render_template(
        'users/new.html',
        user=user,
        errors=errors,
    )


@app.route("/users/<id>")
def show_user(id):
    users = get_users()
    user = next((u for u in users if u["id"] == id), None)
    if user is None:
        return "Пользователь не найден", 404
    return render_template(
        'users/show.html',
        user=user,
    )


@app.route("/users/<id>/edit")
def users_edit(id):
    users = get_users()
    user = next((u for u in users if u["id"] == id), None)
    if user is None:
        return "Пользователь не найден", 404
    errors = {}
    return render_template(
        'users/edit.html',
        user=user,
        errors=errors,
    )


@app.route("/users/<id>/patch", methods=["POST"])
def users_patch(id):
    users = get_users()
    user = next((u for u in users if u["id"] == id), None)
    if not user:
        return "Пользователь не найден", 404

    data = request.form.to_dict()
    errors = validate(data)
    if errors:
        return render_template(
            "users/edit.html",
            user=user,
            errors=errors,
        ), 422

    user['name'] = data['name']
    user['email'] = data['email']
    save_users(users)

    flash("User has been updated", "success")
    return redirect(url_for("users_get"))


@app.route("/users/<id>/delete", methods=["POST"])
def users_delete(id):
    users = [u for u in get_users() if u["id"] != id]
    save_users(users)
    flash("User has been deleted", "success")
    return redirect(url_for("users_get"))


@app.route("/courses/<id>")
def courses_show(id):
    return f"Course id: {id}"


@app.route("/log-info")
def get_log_indo():
    app.logger.info("Получен запрос к главной странице")
    return "Добро пожаловать в библиотеку!"


@app.route("/books")
def get_books():
    app.logger.debug("Начинаем запрос к внешнему API")

    try:
        app.logger.info(f"Отправляем GET запрос к {BOOKS_API_URL}")
        response = requests.get(BOOKS_API_URL)
        response.raise_for_status()

        try:
            books = response.json()
        except ValueError:
            app.logger.error("API вернул не-JSON")
            return "Внешний API вернул неожиданный формат", 502

    except requests.exceptions.Timeout:
        app.logger.error(f"Таймаут при запросе к {BOOKS_API_URL}")
        return "Сервер не отвечает", 504

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Ошибка при запросе к API: {str(e)}")
        return "Произошла ошибка при получении списка книг", 500

    app.logger.debug(f"Получено {len(books)} книг")
    return f"Книги: {books}"


@app.route("/status")
def status():
    app.logger.debug("Проверка статуса приложения")
    try:
        requests.get(BOOKS_API_URL)
        app.logger.info("Внешний API доступен")
        status = "OK"
    except Exception as e:
        app.logger.warning(f"Внешний API недоступен: {str(e)}")
        status = "API недоступен"

    return f"Статус системы: {status}"
