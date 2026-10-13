from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)


# إنشاء قاعدة البيانات
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            ip TEXT,
            status TEXT,
            time TEXT
        )
    """)

    conn.commit()
    conn.close()


# الصفحة الرئيسية
@app.route("/")
def login():
    return render_template("login.html")


# استقبال محاولة تسجيل الدخول
@app.route("/login", methods=["POST"])
def login_attempt():

    username = request.form["username"]
    password = request.form["password"]

    ip = request.remote_addr
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # بيانات الحساب التجريبي
    correct_username = "admin"
    correct_password = "2411"

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # تسجيل دخول صحيح
    if username == correct_username and password == correct_password:

        status = "SUCCESS"

    # تسجيل دخول خاطئ
    else:

        # عدد المحاولات الفاشلة السابقة لنفس IP
        cursor.execute("""
            SELECT COUNT(*)
            FROM attempts
            WHERE ip = ? AND status != 'SUCCESS'
        """, (ip,))

        failed_attempts = cursor.fetchone()[0]

        # المحاولة الثانية أو أكثر = اكتشاف هجوم
        if failed_attempts >= 1:
            status = "BRUTE FORCE DETECTED"
        else:
            status = "FAILED"

    # حفظ المحاولة
    cursor.execute("""
        INSERT INTO attempts (username, ip, status, time)
        VALUES (?, ?, ?, ?)
    """, (username, ip, status, current_time))

    conn.commit()
    conn.close()

    # الدخول الصحيح
    if status == "SUCCESS":
        return redirect("/dashboard")

    # محاولة فاشلة
    return render_template(
        "login.html",
        message=status
    )
    return render_template(
        "login.html",
        message=status
    )


# Test Attack
@app.route("/test_attack", methods=["POST"])
def test_attack():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    username = "test_user"
    ip = "127.0.0.1"

    cursor.execute(
        "DELETE FROM attempts WHERE username = ?",
        (username,)
    )

    for i in range(2):

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO attempts (username, ip, status, time)
            VALUES (?, ?, ?, ?)
        """, (username, ip, "FAILED", current_time))

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO attempts (username, ip, status, time)
        VALUES (?, ?, ?, ?)
    """, (username, ip, "BRUTE FORCE DETECTED", current_time))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# Dashboard
@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # جميع المحاولات
    cursor.execute("""
        SELECT id, username, ip, status, time
        FROM attempts
        ORDER BY id DESC
    """)

    attempts = cursor.fetchall()

    # إجمالي المحاولات
    cursor.execute("""
        SELECT COUNT(*)
        FROM attempts
    """)

    total_attempts = cursor.fetchone()[0]

    # المحاولات الفاشلة
    cursor.execute("""
        SELECT COUNT(*)
        FROM attempts
        WHERE status != 'SUCCESS'
    """)

    failed_attempts = cursor.fetchone()[0]

    # الهجمات المكتشفة
    cursor.execute("""
        SELECT COUNT(*)
        FROM attempts
        WHERE status = 'BRUTE FORCE DETECTED'
    """)

    detected_attacks = cursor.fetchone()[0]

    # تسجيلات الدخول الناجحة
    cursor.execute("""
        SELECT COUNT(*)
        FROM attempts
        WHERE status = 'SUCCESS'
    """)

    successful_logins = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        attempts=attempts,
        total_attempts=total_attempts,
        failed_attempts=failed_attempts,
        detected_attacks=detected_attacks,
        successful_logins=successful_logins
    )


# تشغيل قاعدة البيانات
init_db()


if __name__ == "__main__":
    app.run(debug=True)