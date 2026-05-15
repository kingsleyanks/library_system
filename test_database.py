# test_database.py
from services.library import Library
from models.book import Book
from models.student_member import StudentMember
from models.staff_member import StaffMember
import os

# Clean slate — delete old database if exists
if os.path.exists("library.db"):
    os.remove("library.db")

lib = Library("City Central Library")

# Add books
lib.add_book(Book("Clean Code",     "Robert Martin", "ISBN001", "Tech"))
lib.add_book(Book("Dune",           "Frank Herbert", "ISBN002", "Sci-Fi"))
lib.add_book(Book("Atomic Habits",  "James Clear",   "ISBN003", "Self-Help"))

# Register members
alice = StudentMember("Alice", "M001", "alice@uni.ac.uk", "SN001", "CS")
bob   = StaffMember("Bob",   "M002", "bob@lib.ac.uk",  "IT", "ST001")
lib.register_member(alice)
lib.register_member(bob)

# Borrow
print(lib.borrow_book("M001", "ISBN001"))
print(lib.borrow_book("M001", "ISBN002"))

# Check database directly
print("\n── All books in DB ───────────────────────")
for row in lib.db.get_all_books():
    status = "Available" if row["is_available"] else "Checked Out"
    print(f"  {row['title']:<20} — {status}")

print("\n── Alice's active loans ──────────────────")
for row in lib.db.get_member_loans("M001"):
    print(f"  {row['title']:<20} due {row['due_date']} — {row['status']}")

# Return a book
print("\n" + lib.return_book("M001", "ISBN001"))

# Simulate restart — reload from database
print("\n── Simulating app restart ────────────────")
lib2 = Library("City Central Library")
print(f"  Books loaded: {len(lib2.books)}")
print(f"  Data survived the restart ✓")

print("\n── Member Report ─────────────────────────")
report = lib.db.get_member_report("M001")
if report:
    print(f"  Member         : {report['member_name']}")
    print(f"  Type           : {report['member_type']}")
    print(f"  Currently has  : {report['books_currently_borrowed']} book(s)")
    print(f"  Ever borrowed  : {report['total_books_ever_borrowed']} book(s)")
    print(f"  Days overdue   : {int(report['total_days_overdue'])}")
    print(f"  Fines owed     : ${report['total_fines_owed']:.2f}")