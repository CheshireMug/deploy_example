import psycopg2
from flask import Flask, flash, get_flashed_messages, \
    url_for, render_template, request, redirect, abort
from user_repository import UserRepository


app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"


# Подключение к базе
conn = psycopg2.connect(
    dbname="test_cars",
    user="cars_owner",
    password="password",
    host="localhost"
)
repo = UserRepository(conn)


def validate(user):
    errors = {}
    if not user.get("name"):
        errors["name"] = "Can't be blank"
    elif len(user["name"]) < 5:
        errors["name"] = "Nickname must be greater than 4 characters"
    if not user.get("email"):
        errors["email"] = "Can't send email"
    return errors


@app.route("/")
def index():
    return render_template("users/index.html")


@app.get("/users/")
def users_get():
    query = request.args.get("query", "")
    users = repo.get_content()
    filtered_users = [u for u in users if query.lower() in u["name"].lower()]
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        "users/index.html",
        users=filtered_users,
        search=query,
        messages=messages,
    )


@app.post("/users")
def users_post():
    user_data = request.form.to_dict()
    errors = validate(user_data)
    if errors:
        for _, message in errors.items():
            flash(message, "error")
        return render_template(
            "users/new.html", user=user_data, errors=errors
        ), 422

    user_id = repo.save(user_data)
    flash("Пользователь успешно добавлен", "success")
    return redirect(url_for("users_get"))


@app.route("/users/new")
def users_new():
    user = {"name": "", "email": ""}
    errors = {}
    return render_template("users/new.html", user=user, errors=errors)


@app.route("/users/<id>")
def show_user(id):
    user = repo.find(id)
    if user is None:
        abort(404)
    return render_template("users/show.html", user=user)


@app.route("/users/<id>/edit")
def users_edit(id):
    user = repo.find(id)
    if user is None:
        abort(404)
    errors = {}
    return render_template("users/edit.html", user=user, errors=errors)


@app.route("/users/<id>/patch", methods=["POST"])
def users_patch(id):
    user = repo.find(id)
    if user is None:
        abort(404)

    data = request.form.to_dict()
    data["id"] = id
    errors = validate(data)
    if errors:
        return render_template("users/edit.html", user=data, errors=errors), 422

    repo.save(data)
    flash("User has been updated", "success")
    return redirect(url_for("users_get"))


@app.route("/users/<id>/delete", methods=["POST"])
def users_delete(id):
    repo.destroy(id)
    flash("User has been deleted", "success")
    return redirect(url_for("users_get"))
