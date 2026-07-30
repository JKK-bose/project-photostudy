import re

LOGIN_RE = re.compile(r"^[A-Za-z0-9_]{4,20}$")
PASSWORD_RE = re.compile(r"^(?=.*[A-Za-zА-Яа-я])(?=.*\d).{6,}$")
FULLNAME_RE = re.compile(r"^[А-Яа-яЁёA-Za-z\- ]{5,150}$")
PHONE_RE = re.compile(r"^\+?\d{10,15}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_registration(full_name, login, password, phone, email):
    """Возвращает словарь {поле: текст_ошибки}. Пустой словарь = данные валидны."""
    errors = {}

    full_name = (full_name or "").strip()
    login = (login or "").strip()
    phone = (phone or "").strip()
    email = (email or "").strip()

    if not full_name:
        errors["full_name"] = "Укажите ФИО."
    elif not FULLNAME_RE.match(full_name) or len(full_name.split()) < 2:
        errors["full_name"] = "ФИО должно содержать минимум фамилию и имя, только буквы, пробел и дефис."

    if not login:
        errors["login"] = "Укажите логин."
    elif not LOGIN_RE.match(login):
        errors["login"] = "Логин: 4–20 символов, латинские буквы, цифры и «_»."

    if not password:
        errors["password"] = "Укажите пароль."
    elif not PASSWORD_RE.match(password):
        errors["password"] = "Пароль минимум 6 символов и должен содержать буквы и цифры."

    if not phone:
        errors["phone"] = "Укажите телефон."
    elif not PHONE_RE.match(phone.replace(" ", "").replace("-", "")):
        errors["phone"] = "Телефон должен содержать от 10 до 15 цифр, можно с «+»."

    if not email:
        errors["email"] = "Укажите email."
    elif not EMAIL_RE.match(email):
        errors["email"] = "Некорректный формат email."

    return errors


def validate_booking(booking_date, booking_time, photoshoot_type_id, payment_method):
    errors = {}
    if not booking_date:
        errors["booking_date"] = "Укажите дату съёмки."
    if not booking_time:
        errors["booking_time"] = "Укажите время съёмки."
    if not photoshoot_type_id:
        errors["photoshoot_type_id"] = "Выберите вариант фотосессии."
    if payment_method not in ("cash", "card", "online"):
        errors["payment_method"] = "Выберите способ оплаты."
    return errors
