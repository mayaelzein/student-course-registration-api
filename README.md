# Student Course Registration API

A Python REST API for managing students, courses, and course registrations using a MySQL database hosted on AWS.

Developed as part of CSC coursework. The project originally used JSON-file storage before transitioning to a relational MySQL database.

## Features

- **RESTful operations:** Implements GET, POST, PUT, and DELETE endpoints for managing student and course records.
- **Course registration:** Manages student-course relationships using a relational registration table.
- **JSON handling:** Processes JSON request bodies and generates JSON responses.
- **Validation and error handling:** Handles invalid requests, missing records, duplicate identifiers, and registration constraints using appropriate HTTP status codes.
- **Database integration:** Uses PyMySQL and parameterized SQL queries for database operations.
- **Cloud persistence:** Integrates with a MySQL database hosted on AWS.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/students` | Retrieve all students |
| POST | `/students` | Create a student |
| GET | `/students/{id}` | Retrieve a student |
| PUT | `/students/{id}` | Update a student's name |
| DELETE | `/students/{id}` | Delete a student |
| POST | `/students/{id}/courses` | Register a student for a course |
| GET | `/courses` | Retrieve all courses |
| POST | `/courses` | Create a course |
| GET | `/courses/{id}` | Retrieve a course |
| DELETE | `/courses/{id}` | Delete a course |

GET endpoints return JSON responses, while successful modification requests return HTTP 303 redirects.

## Database Design

The MySQL database uses three relational tables:

| Table | Description |
| --- | --- |
| `students` | Stores student IDs and names |
| `courses` | Stores course IDs |
| `registrations` | Associates students with courses |

The `registrations` table implements a many-to-many relationship between students and courses using:

- `student_id` — Foreign key referencing `students.id`
- `course_id` — Foreign key referencing `courses.id`
- Composite primary key (`student_id`, `course_id`)

Database operations use parameterized SQL queries, and foreign key constraints help maintain referential integrity.

The `TABLES.txt` file contains the original MySQL table definitions obtained using `SHOW CREATE TABLE`.

## Setup

### Requirements

- Python 3
- MySQL
- PyMySQL
- CGI-compatible web server

Install PyMySQL:

```bash
pip install pymysql
```

### Database Configuration

The application expects a MySQL database named `school_db` containing the `students`, `courses`, and `registrations` tables.

Database credentials are imported from a separate `passwords.py` module, which is not included in this repository.

Create a `passwords.py` file with the following variables:

```python
host = "YOUR_DATABASE_HOST"
user = "YOUR_DATABASE_USER"
passwd = "YOUR_DATABASE_PASSWORD"
```

The application uses CGI environment variables, including `PATH_INFO` and `REQUEST_METHOD`, to route HTTP requests. Running the API requires a configured CGI-compatible web server and an accessible MySQL database.
