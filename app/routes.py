from functools import wraps
from datetime import datetime

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash

from .database import get_connection
from .validators import validate_registration, validate_booking

bp = Blueprint("main", __name__)

STATUS_LABELS = {
    "new": "Новая",
    "confirmed": "Подтверждена",
    "completed": "Выполнена",
    "cancelled": "Отменена",
}
PAYMENT_LABELS = {
    "cash": "Наличными",
    "card": "Картой в студии",
    "online": "Онлайн-оплата",
}

PER_PAGE = 5


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Пожалуйста, войдите в систему.", "error")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Доступ только для администратора.", "error")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapped


@bp.context_processor
def inject_globals():
    return {
        "STATUS_LABELS": STATUS_LABELS,
        "PAYMENT_LABELS": PAYMENT_LABELS,
        "current_user": {
            "id": session.get("user_id"),
            "full_name": session.get("full_name"),
            "role": session.get("role"),
        },
    }


@bp.route("/")
def index():
    conn = get_connection()
    types = conn.execute("SELECT * FROM photoshoot_types ORDER BY id").fetchall()
    conn.close()
    return render_template("index.html", types=types)


# ---------------------------------------------------------------- РЕГИСТРАЦИЯ
@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "")
        login = request.form.get("login", "")
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")
        phone = request.form.get("phone", "")
        email = request.form.get("email", "")

        errors = validate_registration(full_name, login, password, phone, email)

        if password and password2 and password != password2:
            errors["password2"] = "Пароли не совпадают."

        conn = get_connection()
        if not errors:
            exists = conn.execute(
                "SELECT id FROM users WHERE login = ?", (login,)
            ).fetchone()
            if exists:
                errors["login"] = "Такой логин уже занят, выберите другой."

            email_exists = conn.execute(
                "SELECT id FROM users WHERE email = ?", (email,)
            ).fetchone()
            if email_exists:
                errors["email"] = "Пользователь с таким email уже зарегистрирован."

        if errors:
            conn.close()
            return render_template(
                "register.html", errors=errors,
                form={"full_name": full_name, "login": login,
                      "phone": phone, "email": email},
            )

        conn.execute(
            "INSERT INTO users (full_name, login, password_hash, phone, email, role) "
            "VALUES (?,?,?,?,?, 'client')",
            (full_name.strip(), login.strip(), generate_password_hash(password),
             phone.strip(), email.strip()),
        )
        conn.commit()
        conn.close()

        flash("Регистрация прошла успешно! Теперь войдите в систему.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html", errors={}, form={})


# ----------------------------------------------------------------- АВТОРИЗАЦИЯ
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_value = request.form.get("login", "").strip()
        password = request.form.get("password", "")

        error = None
        conn = get_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE login = ?", (login_value,)
        ).fetchone()
        conn.close()

        if not login_value or not password:
            error = "Заполните логин и пароль."
        elif not user:
            error = "Пользователь с таким логином не найден."
        elif not check_password_hash(user["password_hash"], password):
            error = "Неверный пароль."

        if error:
            return render_template("login.html", error=error, login_value=login_value)

        session["user_id"] = user["id"]
        session["full_name"] = user["full_name"]
        session["role"] = user["role"]

        flash(f"Добро пожаловать, {user['full_name']}!", "success")
        if user["role"] == "admin":
            return redirect(url_for("main.admin_panel"))
        return redirect(url_for("main.cabinet"))

    return render_template("login.html", error=None, login_value="")


@bp.route("/logout")
def logout():
    session.clear()
    flash("Вы вышли из системы.", "success")
    return redirect(url_for("main.index"))


# ------------------------------------------------------------- ЛИЧНЫЙ КАБИНЕТ
@bp.route("/cabinet", methods=["GET", "POST"])
@login_required
def cabinet():
    conn = get_connection()
    errors = {}
    form = {}

    if request.method == "POST":
        booking_date = request.form.get("booking_date", "")
        booking_time = request.form.get("booking_time", "")
        photoshoot_type_id = request.form.get("photoshoot_type_id", "")
        payment_method = request.form.get("payment_method", "")
        comment = request.form.get("comment", "")
        form = {
            "booking_date": booking_date, "booking_time": booking_time,
            "photoshoot_type_id": photoshoot_type_id,
            "payment_method": payment_method, "comment": comment,
        }

        errors = validate_booking(booking_date, booking_time, photoshoot_type_id, payment_method)

        if not errors:
            try:
                d = datetime.strptime(booking_date, "%Y-%m-%d").date()
                if d < datetime.now().date():
                    errors["booking_date"] = "Дата съёмки не может быть в прошлом."
            except ValueError:
                errors["booking_date"] = "Некорректная дата."

        if not errors:
            conn.execute(
                "INSERT INTO bookings (user_id, photoshoot_type_id, booking_date, "
                "booking_time, payment_method, comment, status) VALUES (?,?,?,?,?,?, 'new')",
                (session["user_id"], photoshoot_type_id, booking_date,
                 booking_time, payment_method, comment.strip()),
            )
            conn.commit()
            conn.close()
            flash("Заявка на фотосессию успешно создана!", "success")
            return redirect(url_for("main.cabinet"))

    types = conn.execute("SELECT * FROM photoshoot_types ORDER BY id").fetchall()
    bookings = conn.execute(
        "SELECT b.*, t.name AS type_name, t.price AS type_price "
        "FROM bookings b JOIN photoshoot_types t ON b.photoshoot_type_id = t.id "
        "WHERE b.user_id = ? ORDER BY b.created_at DESC",
        (session["user_id"],),
    ).fetchall()
    conn.close()

    return render_template("cabinet.html", types=types, bookings=bookings, errors=errors, form=form)


# ------------------------------------------------------------------ АДМИНКА
@bp.route("/admin")
@admin_required
def admin_panel():
    status_filter = request.args.get("status", "")
    page = max(int(request.args.get("page", 1) or 1), 1)

    conn = get_connection()
    base_query = (
        "SELECT b.*, t.name AS type_name, u.full_name AS client_name, "
        "u.phone AS client_phone, u.email AS client_email "
        "FROM bookings b "
        "JOIN photoshoot_types t ON b.photoshoot_type_id = t.id "
        "JOIN users u ON b.user_id = u.id "
    )
    params = []
    if status_filter in STATUS_LABELS:
        base_query += "WHERE b.status = ? "
        params.append(status_filter)
    base_query += "ORDER BY b.created_at DESC"

    all_rows = conn.execute(base_query, params).fetchall()
    total = len(all_rows)
    total_pages = max((total + PER_PAGE - 1) // PER_PAGE, 1)
    page = min(page, total_pages)
    start = (page - 1) * PER_PAGE
    rows = all_rows[start:start + PER_PAGE]

    counts = conn.execute(
        "SELECT status, COUNT(*) AS c FROM bookings GROUP BY status"
    ).fetchall()
    conn.close()

    counts_map = {c["status"]: c["c"] for c in counts}

    return render_template(
        "admin.html", bookings=rows, status_filter=status_filter,
        page=page, total_pages=total_pages, total=total, counts_map=counts_map,
    )


@bp.route("/admin/booking/<int:booking_id>/status", methods=["POST"])
@admin_required
def update_status(booking_id):
    new_status = request.form.get("status")
    if new_status not in STATUS_LABELS:
        return jsonify({"ok": False, "error": "Некорректный статус"}), 400

    conn = get_connection()
    conn.execute("UPDATE bookings SET status = ? WHERE id = ?", (new_status, booking_id))
    conn.commit()
    conn.close()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"ok": True, "status": new_status, "label": STATUS_LABELS[new_status]})

    flash("Статус заявки обновлён.", "success")
    return redirect(url_for("main.admin_panel"))
