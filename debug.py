# debug.py
import sqlite3
import os

print("═" * 50)
print("STEP 1 — Check database file")
print("═" * 50)
if os.path.exists("library.db"):
    os.remove("library.db")
    print("✓ Deleted old library.db")
else:
    print("✓ No old database found")

print("\n═" * 50)
print("STEP 2 — Test DatabaseManager directly")
print("═" * 50)
try:
    from database.db_manager import DatabaseManager
    db = DatabaseManager()
    print("✓ DatabaseManager imported")
except Exception as e:
    print(f"✗ Import failed: {e}")

try:
    db.initialise_database()
    print("✓ initialise_database() called")
except Exception as e:
    print(f"✗ initialise_database() failed: {e}")

# Check tables were actually created
print("\n═" * 50)
print("STEP 3 — Check tables exist in DB")
print("═" * 50)
try:
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    if tables:
        for table in tables:
            print(f"✓ Table found: {table[0]}")
    else:
        print("✗ NO TABLES FOUND — initialise_database() did not create tables")
    conn.close()
except Exception as e:
    print(f"✗ Table check failed: {e}")

print("\n═" * 50)
print("STEP 4 — Test add_book directly")
print("═" * 50)
try:
    from models.book import Book
    book = Book("Clean Code", "Robert Martin", "ISBN001", "Tech")
    print("✓ Book created")
    result = db.add_book(book)
    print(f"✓ add_book() returned: {result}")
except Exception as e:
    print(f"✗ add_book() failed: {e}")

# Check if book actually saved
print("\n═" * 50)
print("STEP 5 — Check book saved to DB")
print("═" * 50)
try:
    conn = sqlite3.connect("library.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"✓ Book in DB: {dict(row)}")
    else:
        print("✗ NO BOOKS IN DATABASE — add_book() did not save")
    conn.close()
except Exception as e:
    print(f"✗ Read failed: {e}")

print("\n═" * 50)
print("STEP 6 — Test register_member directly")
print("═" * 50)
try:
    from models.student_member import StudentMember
    alice = StudentMember("Alice", "M001", "alice@uni.ac.uk", "SN001", "CS")
    print("✓ Member created")
    result = db.register_member(alice)
    print(f"✓ register_member() returned: {result}")
except Exception as e:
    print(f"✗ register_member() failed: {e}")

# Check if member actually saved
print("\n═" * 50)
print("STEP 7 — Check member saved to DB")
print("═" * 50)
try:
    conn = sqlite3.connect("library.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"✓ Member in DB: {dict(row)}")
    else:
        print("✗ NO MEMBERS IN DATABASE — register_member() did not save")
    conn.close()
except Exception as e:
    print(f"✗ Read failed: {e}")

print("\n═" * 50)
print("STEP 8 — Print db_manager.py contents")
print("═" * 50)
with open("database/db_manager.py", "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines, 1):
        print(f"{i:3}  {line}", end="")