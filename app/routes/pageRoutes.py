from flask import Blueprint, render_template, send_from_directory

from config import UPLOAD_FOLDER


page_bp = Blueprint("pages", __name__)


@page_bp.get("/")
def home():
    return render_template("home.html")


@page_bp.get("/home")
def home_page():
    return render_template("home.html")


@page_bp.get("/portal")
def portal():
    return render_template("home.html")


@page_bp.get("/login")
def login_page():
    return render_template("dashboard.html")


@page_bp.get("/admin")
def admin():
    return render_template("dashboard.html")


@page_bp.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@page_bp.get("/register")
def register():
    return render_template("register.html")


@page_bp.get("/about")
def about():
    return render_template("about.html")


@page_bp.get("/database")
def database_page():
    return render_template("database.html")


@page_bp.get("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
