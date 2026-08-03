from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


# Create database and table
def init_db():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL,
            age INTEGER,
            roll_number TEXT,
            phone TEXT,
            year TEXT
        )
    """)

    conn.commit()
    conn.close()
  


# Home page - display all students
@app.route("/")
def index():

    search = request.args.get("search", "")
    course = request.args.get("course", "")

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    # Search and filter query
    query = "SELECT * FROM students WHERE 1=1"
    params = []

    if search:
        query += """
            AND (
                name LIKE ?
                OR roll_number LIKE ?
                OR email LIKE ?
            )
        """

        search_value = f"%{search}%"

        params.extend([
            search_value,
            search_value,
            search_value
        ])

    if course:
        query += " AND course = ?"
        params.append(course)

    query += " ORDER BY id DESC"

    cursor.execute(query, params)

    students = cursor.fetchall()


    # Total students
    cursor.execute(
        "SELECT COUNT(*) FROM students"
    )

    total_students = cursor.fetchone()[0]


    # CSE students
    cursor.execute(
        "SELECT COUNT(*) FROM students WHERE course = ?",
        ("CSE",)
    )

    cse_students = cursor.fetchone()[0]


    # Data Science students
    cursor.execute(
        "SELECT COUNT(*) FROM students WHERE course = ?",
        ("CSE (Data Science)",)
    )

    ds_students = cursor.fetchone()[0]


    # Other students
    cursor.execute("""
        SELECT COUNT(*)
        FROM students
        WHERE course NOT IN (?, ?)
    """, ("CSE", "CSE (Data Science)"))

    other_students = cursor.fetchone()[0]


    conn.close()


    return render_template(
        "index.html",
        students=students,
        total_students=total_students,
        cse_students=cse_students,
        ds_students=ds_students,
        other_students=other_students,
        search=search,
        selected_course=course
    )

# Add student
@app.route("/add", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        roll_number = request.form["roll_number"]
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        course = request.form["course"]
        year = request.form["year"]

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students
            (roll_number, name, email, phone, course, year, age)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            roll_number,
            name,
            email,
            phone,
            course,
            year,
            0
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_student.html")


# Delete student
@app.route("/delete/<int:id>")
def delete_student(id):

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect("/")


# Edit student
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    if request.method == "POST":

        roll_number = request.form["roll_number"]
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        course = request.form["course"]
        year = request.form["year"]

        cursor.execute("""
            UPDATE students
            SET roll_number = ?,
                name = ?,
                email = ?,
                phone = ?,
                course = ?,
                year = ?
            WHERE id = ?
        """, (
            roll_number,
            name,
            email,
            phone,
            course,
            year,
            id
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    )

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_student.html",
        student=student
    )

init_db()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)