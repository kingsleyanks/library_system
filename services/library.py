from models.book import Book
from database.db_connection import DatabaseConnection
from models.member import Member
from services.algorithms import *
from database.db_manager import DatabaseManager

class Library:
    def __init__(self, name):
        self.name        = name
        self.books       = {}         # still cache in memory for speed
        self.members     = {}
        self.db          = DatabaseManager()
        self.db.initialise_database()
        self._load_from_database() 
        
    # ══════════════════════════════════════════════
    # BOOK MANAGEMENT
    # ══════════════════════════════════════════════
    def _load_from_database(self):
        """Load all books and members from DB into memory on startup."""
        for row in self.db.get_all_books():
            book              = Book(row["title"], row["author"],
                                     row["isbn"],  row["genre"])
            book.is_available = bool(row["is_available"])
            book.due_date     = row["due_date"]
            self.books[book.isbn] = book

        print(f"✓ Loaded {len(self.books)} books from database")
        
        # ── Load members ───────────────────────────────────────────
        for row in self.db.get_all_members():
            # Recreate the right member type based on what's stored
            member_type = row["member_type"]

            if "Student" in member_type:
                from models.student_member import StudentMember
                member = StudentMember(
                    row["name"], row["member_id"], row["email"], "N/A", "N/A"
                )
            elif "Staff" in member_type:
                from models.staff_member import StaffMember
                member = StaffMember(
                    row["name"], row["member_id"], row["email"], "N/A", "N/A"
                )
            elif "Premium" in member_type:
                from models.premium_member import PremiumMember
                member = PremiumMember(
                    row["name"], row["member_id"], row["email"], "Gold"
                )
            elif "Librarian" in member_type:
                from models.librarian_member import LibrarianMember
                member = LibrarianMember(
                    row["name"], row["member_id"], row["email"], "N/A", "N/A", 1
                )
            else:
                from models.member import Member
                member = Member(row["name"], row["member_id"], row["email"])

            member.paid_fines = row["paid_fines"]
            self.members[member.member_id] = member

        print(f"✓ Loaded {len(self.members)} members from database")
    
    def add_book(self, book):
        
        if book.isbn in self.books:
            return f"Book with ISBN {book.isbn} already exists in the library."
        self.books[book.isbn] = book 
        self.db.add_book(book)          # ← persist to database
        return f"'{book.title}' added to the library. Total books: {len(self.books)}"
    
    def remove_book(self, isbn):
        if isbn not in self.books:
            return f"Book with ISBN {isbn} does not exist in the library."
        book = self.books.get(isbn)
        if not book.is_available:
            return f"Cannot remove '{book.title}' as it is currently checked out."
        del self.books[isbn]
        return f"'{book.title}' removed from the library. Total books: {len(self.books)}"
    
    def find_book_by_isbn(self, isbn):
        """Direct lookup by ISBN — O(1)."""
        return self.books.get(isbn, None)

    def search_books(self, query):
        """Search by title, author, or genre — case insensitive."""
        query = query.lower()
        results = [
            book for book in self.books.values()
            if query in book.title.lower()
            or query in book.author.lower()
            or query in book.genre.lower()
        ]
        return results if results else []

    def get_available_books(self):
        """Return all books currently available."""
        return [b for b in self.books.values() if b.is_available]

    def get_overdue_books(self):
        """Return all books currently overdue."""
        return [b for b in self.books.values() if b.is_overdue()]

    # ══════════════════════════════════════════════
    # MEMBER MANAGEMENT
    # ══════════════════════════════════════════════

    def register_member(self, member):
        """Register a new member."""
        if member.member_id in self.members:
            return f"Member ID {member.member_id} already registered."
        self.members[member.member_id] = member
        self.db.register_member(member)     # ← persist to database
        return f"{member.get_member_type()} '{member.name}' registered successfully."

    def remove_member(self, member_id):
        """Remove a member — only if they have no borrowed books."""
        if member_id not in self.members:
            return f"No member found with ID {member_id}."
        member = self.members[member_id]
        if member.borrowed_books:
            return (f"Cannot remove '{member.name}' — "
                    f"they have {member.get_number_of_borrowed_books()} book(s) on loan.")
        del self.members[member_id]
        return f"Member '{member.name}' removed."

    def find_member(self, member_id):
        """Direct lookup by member ID."""
        return self.members.get(member_id, None)
    
    
    
    # ══════════════════════════════════════════════
    # LOAN MANAGEMENT
    # ══════════════════════════════════════════════

    def borrow_book(self, member_id, isbn):
        """Process a book loan — validates both member and book exist."""
        member = self.find_member(member_id)
        if not member:
            return f"Member ID '{member_id}' not found."

        book = self.find_book_by_isbn(isbn)
        if not book:
            return f"Book ISBN '{isbn}' not found in catalog."

        result = member.borrow_book(book)
        
        # If borrow was successful, update the book's availability in the library
        if not book.is_available:
            self.db.update_book_availability(book.isbn, False)  # ← persist change to database
            self.db.record_loan(member_id, isbn, member.LOAN_PERIOD_DAYS)  # ← record the loan in the database
            
        return result

    def return_book(self, member_id, isbn):
        """Process a book return."""
        member = self.find_member(member_id)
        if not member:
            return f"Member ID '{member_id}' not found."

        book = self.find_book_by_isbn(isbn)
        if not book:
            return f"Book ISBN '{isbn}' not found in catalog."

        result = member.return_book(book)
        if book.is_available:  # If return was successful, update the book's availability in the library
            self.db.update_book_availability(book.isbn, True)  # ← persist change to database
            self.db.record_return(member_id, isbn)  # ← record the return in the database
            
        return result

    def pay_fine(self, member_id, amount):
        """Process a fine payment for a member."""
        member = self.find_member(member_id)
        if not member:
            return f"Member ID '{member_id}' not found."
        return member.pay_fine(amount)
    # ══════════════════════════════════════════════
    # SORTING
    # ══════════════════════════════════════════════
    
    def get_catalog_sorted(self, sort_by="title", algorithm = "merge"):
        """Return the catalog sorted by a specified key and algorithm."""
        key_map = {
            "title" : lambda b: b.title,
            "author": lambda b: b.author,
            "genre" : lambda b: b.genre
        }
        if sort_by not in key_map:
            return list(self.books.values())  # Return unsorted if invalid key
        key        = key_map[sort_by]       # ✅ extract the lambda
        books_list = list(self.books.values())


        if algorithm == "quick":
            return quick_sort(books_list, key=key)
        return merge_sort(books_list, key=key)
    
    # ══════════════════════════════════════════════
    # BINARY SEARCH
    # ══════════════════════════════════════════════

    def binary_search_by_title(self, title):
        """
        Fast binary search by title.
        Sorts first, then searches — O(n log n) sort + O(log n) search.
        """
        sorted_books = self.get_catalog_sorted(sort_by="title")
        return binary_search(sorted_books, title, key=lambda b: b.title)

    def binary_search_by_author(self, author):
        """Binary search by author name."""
        sorted_books = self.get_catalog_sorted(sort_by="author")
        return binary_search(sorted_books, author, key=lambda b: b.author)

    # ══════════════════════════════════════════════
    # REPORTS
    # ══════════════════════════════════════════════

    def get_catalog_summary(self):
        """High level stats for the library."""
        total     = len(self.books)
        available = len(self.get_available_books())
        overdue   = len(self.get_overdue_books())
        return {
            "total_books"    : total,
            "available"      : available,
            "checked_out"    : total - available,
            "overdue"        : overdue,
            "total_members"  : len(self.members)
        }
        
    def generate_report(self):
        """Generate a detailed report of the full library status."""
        summary = self.get_catalog_summary()
        all_books    = list(self.books.values())
        all_members  = list(self.members.values())
        
        # ── Use recursive_count_overdue ────────────────────────
        overdue_count = recursive_count_overdue(all_books)

        # ── Use sort_members_by_fines ──────────────────────────
        sorted_members = sort_members_by_fines(all_members)

        # ── Header ─────────────────────────────────────────────────
        lines = [
            "═" * 50,
            f"  LIBRARY REPORT — {self.name}",
            "═" * 50,
            f"  Total Books    : {summary['total_books']}",
            f"  Available      : {summary['available']}",
            f"  Checked Out    : {summary['checked_out']}",
            f"  Overdue        : {overdue_count}",
            f"  Total Members  : {summary['total_members']}",
            "─" * 50,
        ]

        # ── Overdue books section ───────────────────────────────────
        overdue_books = self.get_overdue_books()
        lines.append(f"\n  OVERDUE BOOKS ({len(overdue_books)})")
        if overdue_books:
            for book in overdue_books:
                lines.append(
                    f"    • '{book.title}' — "
                    f"{book.days_overdue()} day(s) overdue"
                )
        else:
            lines.append("    No overdue books.")

        # ── Members section ─────────────────────────────────────────
        lines.append(f"\n  MEMBER FINES SUMMARY")
        lines.append("─" * 50)

        total_fines_across_all = 0

        for member in self.members.values():             # ← use member directly
            borrowed = member.get_number_of_borrowed_books()
            overdue  = len([b for b in member.borrowed_books if b.is_overdue()])
            fines    = member.get_total_fines()
            total_fines_across_all += fines

            lines.append(
                f"  {member.get_member_type():<20} {member.name} "
                f"(ID: {member.member_id})"
            )
            lines.append(
                f"    Borrowed: {borrowed} | "
                f"Overdue: {overdue} | "
                f"Fines: ${fines:.2f}"
            )

        # ── Footer ──────────────────────────────────────────────────
        lines.append("─" * 50)
        lines.append(f"  Total Outstanding Fines : ${total_fines_across_all:.2f}")
        lines.append("═" * 50)

        return "\n".join(lines)   # ← One return, after loop completes

    def __str__(self):
        summary = self.get_catalog_summary()
        return (
            f"Library : {self.name}\n"
            f"Books   : {summary['total_books']} total | "
            f"{summary['available']} available | "
            f"{summary['checked_out']} checked out | "
            f"{summary['overdue']} overdue\n"
            f"Members : {summary['total_members']} registered"
        )