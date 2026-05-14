# main.py

from services.library import Library
from models.book import Book
from models.student_member import StudentMember
from models.staff_member import StaffMember
from models.premium_member import PremiumMember
from models.librarian_member import LibrarianMember
import datetime

# ══════════════════════════════════════════════
# SETUP — seed data so the app isn't empty
# ══════════════════════════════════════════════

def seed_library(library):
    """Populate library with initial books and members."""
    books = [
        Book("Clean Code", "Robert Martin", "ISBN001", "Tech"),
        Book("The Pragmatic Programmer", "Andrew Hunt", "ISBN002", "Tech"),
        Book("Dune", "Frank Herbert", "ISBN003", "Sci-Fi"),
        Book("Atomic Habits", "James Clear", "ISBN004", "Self-Help"),
        Book("Deep Work", "Cal Newport", "ISBN005", "Productivity"),
    ]
    members = [
        StudentMember("Alice Johnson", "M001", "alice@uni.ac.uk", "SN001", "Computer Science"),
        StaffMember("Bob Smith", "M002", "bob@lib.ac.uk", "IT Department", "ST001"),
        PremiumMember("Carol White", "M003", "carol@email.com", "Gold"),
        LibrarianMember("Diana Prince", "M004", "diana@lib.ac.uk", "Catalog", "ST002", 3),
    ]
    for book in books:
        library.add_book(book)
    for member in members:
        library.register_member(member)

# ══════════════════════════════════════════════
# DISPLAY HELPERS
# ══════════════════════════════════════════════

def print_header(title):
    print("\n" + "═" * 45)
    print(f"  {title}")
    print("═" * 45)

def print_menu():
    print_header("LIBRARY MANAGEMENT SYSTEM")
    print("  1. Add Book")
    print("  2. Register Member")
    print("  3. Borrow Book")
    print("  4. Return Book")
    print("  5. Pay Fine")
    print("  6. Search Books")
    print("  7. View All Members")
    print("  8. View Overdue Books")
    print("  9. Library Summary")
    print("  10. Generate Full Report")
    print("  0. Exit")
    print("═" * 45)

# ══════════════════════════════════════════════
# MENU ACTIONS
# ══════════════════════════════════════════════

def add_book(library):
    print_header("ADD BOOK")
    title  = input("Title  : ").strip()
    author = input("Author : ").strip()
    isbn   = input("ISBN   : ").strip()
    genre  = input("Genre  : ").strip()
    book   = Book(title, author, isbn, genre)
    print(library.add_book(book))

def register_member(library):
    print_header("REGISTER MEMBER")
    print("Types: 1=Student  2=Staff  3=Premium  4=Librarian")
    member_type = input("Type   : ").strip()
    name      = input("Name      : ").strip()
    member_id = input("Member ID : ").strip()
    email     = input("Email     : ").strip()

    if member_type == "1":
        student_no = input("Student No : ").strip()
        course     = input("Course     : ").strip()
        member = StudentMember(name, member_id, email, student_no, course)
    elif member_type == "2":
        dept       = input("Department  : ").strip()
        staff_no   = input("Staff No    : ").strip()
        member = StaffMember(name, member_id, email, dept, staff_no)
    elif member_type == "3":
        tier   = input("Tier (Gold/Platinum) : ").strip()
        member = PremiumMember(name, member_id, email, tier)
    elif member_type == "4":
        dept       = input("Department  : ").strip()
        staff_no   = input("Staff No    : ").strip()
        level      = int(input("Access Level (1-3) : ").strip())
        member = LibrarianMember(name, member_id, email, dept, staff_no, level)
    else:
        print("Invalid member type.")
        return

    print(library.register_member(member))

def borrow_book(library):
    print_header("BORROW BOOK")
    member_id = input("Member ID : ").strip()
    isbn      = input("ISBN      : ").strip()
    print(library.borrow_book(member_id, isbn))

def return_book(library):
    print_header("RETURN BOOK")
    member_id = input("Member ID : ").strip()
    isbn      = input("ISBN      : ").strip()
    print(library.return_book(member_id, isbn))

def pay_fine(library):
    print_header("PAY FINE")
    member_id = input("Member ID : ").strip()
    member    = library.find_member(member_id)
    if not member:
        print(f"Member '{member_id}' not found.")
        return
    print(f"\nOutstanding fines: ${member.get_total_fines():.2f}")
    for line in member.get_fine_breakdown():
        print(line)
    try:
        amount = float(input("\nAmount to pay: $").strip())
        print(library.pay_fine(member_id, amount))
    except ValueError:
        print("Invalid amount entered.")

def search_books(library):
    print_header("SEARCH BOOKS")
    query   = input("Search (title / author / genre) : ").strip()
    results = library.search_books(query)
    if results:
        print(f"\n{len(results)} result(s) found:")
        for book in results:
            print(f"  {book}")
    else:
        print("No books found.")

def view_all_members(library):
    print_header("ALL MEMBERS")
    if not library.members:
        print("No members registered.")
        return
    for member in library.members.values():
        print(f"\n{member}")
        print("-" * 40)

def view_overdue_books(library):
    print_header("OVERDUE BOOKS")
    overdue = library.get_overdue_books()
    if not overdue:
        print("No overdue books.")
        return
    print(f"{len(overdue)} overdue book(s):\n")
    for book in overdue:
        print(f"  {book}")

def generate_report(library):
    print(library.generate_report())
    
def library_summary(library):
    print_header("LIBRARY SUMMARY")
    get_catalog_summary = library.get_catalog_summary()
    print(f"Total Books     : {get_catalog_summary['total_books']}")
    print(f"Available Books : {get_catalog_summary['available']}")
    print(f"Checked Out     : {get_catalog_summary['checked_out']}")
    print(f"Overdue Books   : {get_catalog_summary['overdue']}")
    print(f"Total Members   : {get_catalog_summary['total_members']}")
    print(library)

# ══════════════════════════════════════════════
# MAIN LOOP
# ══════════════════════════════════════════════

def main():
    library = Library("City Central Library")
    seed_library(library)

    actions = {
        "1": add_book,
        "2": register_member,
        "3": borrow_book,
        "4": return_book,
        "5": pay_fine,
        "6": search_books,
        "7": view_all_members,
        "8": view_overdue_books,
        "9": library_summary,
        "10": generate_report,
        "0": None
    }

    print(f"\nWelcome to {library.name}!")

    while True:
        print_menu()
        choice = input("  Select option : ").strip()

        if choice == "0":
            print("\nGoodbye!\n")
            break
        elif choice in actions:
            actions[choice](library)   # ← Dictionary dispatch — no if/elif chain
        else:
            print("Invalid option. Please try again.")


from services.library import Library
from services.algorithms import merge_sort, quick_sort, binary_search
from models.book import Book

lib = Library("City Central Library")
books = [
    Book("Dune",                    "Frank Herbert",  "ISBN001", "Sci-Fi"),
    Book("Clean Code",              "Robert Martin",  "ISBN002", "Tech"),
    Book("Atomic Habits",           "James Clear",    "ISBN003", "Self-Help"),
    Book("The Pragmatic Programmer","Andrew Hunt",    "ISBN004", "Tech"),
    Book("Deep Work",               "Cal Newport",    "ISBN005", "Productivity"),
]
for book in books:
    lib.add_book(book)

book_list = list(lib.books.values())


# ── Merge Sort ─────────────────────────────────────────────────
print("═" * 50)
print("MERGE SORT — by title")
print("═" * 50)
sorted_books = merge_sort(book_list, key=lambda b: b.title)
for i, book in enumerate(sorted_books, 1):
    print(f"  {i}. {book.title}")

print("\nMERGE SORT — by author")
print("═" * 50)
sorted_books = merge_sort(book_list, key=lambda b: b.author)
for i, book in enumerate(sorted_books, 1):
    print(f"  {i}. {book.author:<20} — {book.title}")

# ── Quick Sort ─────────────────────────────────────────────────
print("\nQUICK SORT — by genre")
print("═" * 50)
sorted_books = quick_sort(book_list, key=lambda b: b.genre)
for i, book in enumerate(sorted_books, 1):
    print(f"  {i}. {book.genre:<15} — {book.title}")

# ── Binary Search ───────────────────────────────────────────────
print("\nBINARY SEARCH")
print("═" * 50)
sorted_books = merge_sort(book_list, key=lambda b: b.title)

tests = ["Clean Code", "Dune", "Harry Potter"]
for query in tests:
    result = binary_search(sorted_books, query, key=lambda b: b.title)
    if result:
        print(f"  ✓ Found  : '{result.title}' by {result.author}")
    else:
        print(f"  ✗ Not found : '{query}'")

# ── Library integration ─────────────────────────────────────────
print("\nLIBRARY SORTED CATALOG")
print("═" * 50)
for book in lib.get_catalog_sorted(sort_by="title", algorithm="merge"):
    print(f"  {book}")

print("\nBINARY SEARCH VIA LIBRARY")
print("═" * 50)
result = lib.binary_search_by_title("atomic habits")
print(f"  Search 'atomic habits' → {result.title if result else 'Not found'}")
result = lib.binary_search_by_author("cal newport")
print(f"  Search 'cal newport'   → {result.title if result else 'Not found'}")

if __name__ == "__main__":
    main()
    
    
