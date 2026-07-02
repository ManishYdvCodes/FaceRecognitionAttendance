import sqlite3

conn = sqlite3.connect("students.db")

cursor = conn.cursor()

cursor.execute("""
INSERT INTO students
VALUES
(100,'Manish','CSE','4th Year')
""")

conn.commit()
conn.close()

print("Student Added")