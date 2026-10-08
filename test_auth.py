"""
Smoke-tests the auth/RBAC flow end-to-end against a RUNNING server.

Requires: pip install requests
Usage:    python test_auth.py
          (make sure `uvicorn main:app --reload` is running first)

Each run uses freshly generated emails, so it's safe to run repeatedly —
no leftover state from a previous run will cause false failures.
"""
import sys
import uuid

import requests

BASE_URL = "http://localhost:8000"

PASSED = []
FAILED = []


def check(label, condition, extra=""):
    if condition:
        PASSED.append(label)
        print(f"  OK   {label}")
    else:
        FAILED.append(label)
        print(f"  FAIL {label}  {extra}")


def register_student(email, password):
    return requests.post(f"{BASE_URL}/students", json={
        "name": "Anna", "surname": "Kowalska", "birthyear": 2002,
        "semester": 3, "email": email, "password": password,
    })


def register_teacher(email, password):
    return requests.post(f"{BASE_URL}/teachers", json={
        "name": "Jan", "surname": "Nowak", "birthyear": 1980,
        "specialization": "Polish Literature", "email": email, "password": password,
    })


def login(email, password):
    # Form-encoded, NOT json — matches OAuth2PasswordRequestForm
    r = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    if r.status_code != 200:
        return None
    return r.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def main():
    run_id = uuid.uuid4().hex[:8]
    student_email = f"student_{run_id}@test.com"
    teacher_email = f"teacher_{run_id}@test.com"
    password = "testpass123"

    print(f"\n--- Setup (run id: {run_id}) ---")

    r = register_student(student_email, password)
    check("Register student -> 200", r.status_code == 200, r.text)
    student_id = r.json()["ID"] if r.status_code == 200 else None

    r = register_teacher(teacher_email, password)
    check("Register teacher -> 200", r.status_code == 200, r.text)
    teacher_id = r.json()["ID"] if r.status_code == 200 else None

    student_token = login(student_email, password)
    check("Student login succeeds", student_token is not None)

    teacher_token = login(teacher_email, password)
    check("Teacher login succeeds", teacher_token is not None)

    bad_token = login(student_email, "wrong-password")
    check("Login with wrong password fails", bad_token is None)

    print("\n--- Unauthenticated access ---")

    r = requests.get(f"{BASE_URL}/courses")
    check("No token on GET /courses -> 401", r.status_code == 401, r.text)

    r = requests.get(f"{BASE_URL}/courses", headers={"Authorization": "Bearer garbage.token.here"})
    check("Garbage token on GET /courses -> 401", r.status_code == 401, r.text)

    if not (student_token and teacher_token and student_id and teacher_id):
        print("\nSetup failed — stopping early, fix the above before continuing.")
        summarize()
        return

    print("\n--- Role-based access control ---")

    r = requests.get(f"{BASE_URL}/courses", headers=auth_header(student_token))
    check("Student CAN GET /courses -> 200", r.status_code == 200, r.text)

    r = requests.post(f"{BASE_URL}/courses", json={"name": f"TestCourse_{run_id}", "semester": 1},
                       headers=auth_header(student_token))
    check("Student CANNOT POST /courses -> 403", r.status_code == 403, r.text)

    r = requests.post(f"{BASE_URL}/courses", json={"name": f"TestCourse_{run_id}", "semester": 1},
                       headers=auth_header(teacher_token))
    check("Teacher CAN POST /courses -> 200", r.status_code == 200, r.text)
    course_id = r.json()["ID"] if r.status_code == 200 else None

    if not course_id:
        print("\nCourse creation failed — stopping early.")
        summarize()
        return

    print("\n--- Object-level authorization (self-enrollment) ---")

    r = requests.post(f"{BASE_URL}/students/{student_id}/attends/{course_id}",
                       headers=auth_header(student_token))
    check("Student CAN enroll THEMSELVES -> 200", r.status_code == 200, r.text)

    fake_other_student_id = str(uuid.uuid4())
    r = requests.post(f"{BASE_URL}/students/{fake_other_student_id}/attends/{course_id}",
                       headers=auth_header(student_token))
    check("Student CANNOT enroll SOMEONE ELSE -> 403", r.status_code == 403, r.text)

    r = requests.post(f"{BASE_URL}/teachers/{teacher_id}/teaches/{course_id}",
                       headers=auth_header(teacher_token))
    check("Teacher CAN assign themselves to teach -> 200", r.status_code == 200, r.text)

    print("\n--- Verify relationships landed ---")

    r = requests.get(f"{BASE_URL}/courses/{course_id}/students", headers=auth_header(teacher_token))
    ids = [s["ID"] for s in r.json()] if r.status_code == 200 else []
    check("Course student list includes our student", student_id in ids, r.text)

    r = requests.get(f"{BASE_URL}/courses/{course_id}/teachers", headers=auth_header(student_token))
    ids = [t["ID"] for t in r.json()] if r.status_code == 200 else []
    check("Course teacher list includes our teacher", teacher_id in ids, r.text)

    summarize()


def summarize():
    print(f"\n=== {len(PASSED)} passed, {len(FAILED)} failed ===")
    if FAILED:
        print("Failed checks:")
        for f in FAILED:
            print(f"  - {f}")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print(f"\nCouldn't reach {BASE_URL} — is `uvicorn main:app --reload` running?")
        sys.exit(1)