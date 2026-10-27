#!/usr/bin/python3
import os
import sys
import json
import pymysql
import passwords  

host = os.environ.get("HTTP_HOST", "localhost")
script_name = os.environ.get("SCRIPT_NAME", "/cgi-bin/school")
BASE_URL = f"http://{host}{script_name}"

def get_connection():
    return pymysql.connect(
        host=passwords.host,
        user=passwords.user,
        password=passwords.passwd,
        db="school_db",
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def respond(status, headers=[], body=None):
    print(f"Status: {status}")
    for k, v in headers:
        print(f"{k}: {v}")
    print("Content-Type: application/json\n")
    if body:
        print(json.dumps(body, indent=2))

def redirect(url):
    respond("303 See Other", [("Location", url)])

def error_404(): 
    respond("404 Not Found")

def error_400(msg="Bad Request"): 
    respond("400 Bad Request", body={"error": msg})

def error_405(allowed): 
    respond("405 Method Not Allowed", [("Allow", allowed)])

def handle_students(path, method):
    conn = get_connection()
    cur = conn.cursor()
    if len(path) == 0:
        if method == "GET":
            cur.execute("SELECT * FROM students")
            students = cur.fetchall()
            for s in students:
                s['link'] = f"{BASE_URL}/students/{s['id']}"
            respond("200 OK", body=students)

        elif method == "POST":
            body = json.load(sys.stdin)
            if set(body.keys()) != {"id", "name"} or not isinstance(body["id"], int):
                error_400()
                return
            try:
                cur.execute("INSERT INTO students (id, name) VALUES (%s, %s)", (body["id"], body["name"]))
                conn.commit()
                redirect(f"{BASE_URL}/students/{body['id']}")
            except:
                error_400("ID already exists")
        else:
            error_405("GET,POST")

    elif len(path) == 1:
        try:
            student_id = int(path[0])
        except:
            error_400("Invalid ID")
            return

        cur.execute("SELECT * FROM students WHERE id=%s", (student_id,))
        student = cur.fetchone()
        if not student:
            error_404()
            return

        if method == "GET":
            cur.execute("SELECT course_id FROM registrations WHERE student_id=%s", (student_id,))
            student['courses'] = [row['course_id'] for row in cur.fetchall()]
            student['link'] = f"{BASE_URL}/students/{student_id}"
            respond("200 OK", body=student)

        elif method == "PUT":
            body = json.load(sys.stdin)
            if list(body.keys()) != ["name"]:
                error_400()
                return
            cur.execute("UPDATE students SET name=%s WHERE id=%s", (body['name'], student_id))
            conn.commit()
            redirect(f"{BASE_URL}/students/{student_id}")

        elif method == "DELETE":
            cur.execute("DELETE FROM registrations WHERE student_id=%s", (student_id,))
            cur.execute("DELETE FROM students WHERE id=%s", (student_id,))
            conn.commit()
            redirect(f"{BASE_URL}/students")

        else:
            error_405("GET,PUT,DELETE")

    elif len(path) == 2 and path[1] == "courses":
        student_id = int(path[0])
        body = json.load(sys.stdin)
        course_id = body

        cur.execute("SELECT * FROM courses WHERE id=%s", (course_id,))
        if not cur.fetchone():
            error_400("Course does not exist")
            return

        try:
            cur.execute("INSERT INTO registrations (student_id, course_id) VALUES (%s, %s)",
                        (student_id, course_id))
            conn.commit()
        except:
            pass

        redirect(f"{BASE_URL}/students/{student_id}")
    else:
        error_404()
    cur.close()

def handle_courses(path, method):
    conn = get_connection()
    cur = conn.cursor()
    if len(path) == 0:
        if method == "GET":
            cur.execute("SELECT * FROM courses")
            courses = cur.fetchall()
            for c in courses:
                c['link'] = f"{BASE_URL}/courses/{c['id']}"
            respond("200 OK", body=courses)

        elif method == "POST":
            body = json.load(sys.stdin)
            if set(body.keys()) != {"id"}:
                error_400()
                return
            try:
                cur.execute("INSERT INTO courses (id) VALUES (%s)", (body["id"],))
                conn.commit()
                redirect(f"{BASE_URL}/courses/{body['id']}")
            except:
                error_400("Course ID already exists")
        else:
            error_405("GET,POST")

    elif len(path) == 1:
        course_id = path[0]
        cur.execute("SELECT * FROM courses WHERE id=%s", (course_id,))
        course = cur.fetchone()
        if not course:
            error_404()
            return

        if method == "GET":
            course['link'] = f"{BASE_URL}/courses/{course['id']}"
            respond("200 OK", body=course)

        elif method == "DELETE":
            cur.execute("SELECT * FROM registrations WHERE course_id=%s", (course_id,))
            if cur.fetchone():
                error_400("Course is still registered by a student")
                return
            cur.execute("DELETE FROM courses WHERE id=%s", (course_id,))
            conn.commit()
            redirect(f"{BASE_URL}/courses")
        else:
            error_405("GET,DELETE")
    else:
        error_404()
    cur.close()

def main():
    path = os.environ.get('PATH_INFO', '').strip('/').split('/')
    method = os.environ['REQUEST_METHOD']

    if path[0] == "students":
        handle_students(path[1:], method)
    elif path[0] == "courses":
        handle_courses(path[1:], method)
    elif path[0] == "debug":
        if method == "GET":
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM students")
            students = cur.fetchall()
            cur.execute("SELECT * FROM courses")
            courses = cur.fetchall()
            cur.execute("SELECT * FROM registrations")
            regs = cur.fetchall()
            respond("200 OK", body={"students": students, "courses": courses, "registrations": regs})
            cur.close()
        else:
            error_405("GET")
    else:
        error_404()

if __name__ == "__main__":
    try:
        main()
    except:
        print("Content-Type: text/html\n")
