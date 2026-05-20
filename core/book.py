# core/book.py
from datetime import datetime, timedelta

class Book:
    total_books = 0

    def __init__(self, title, author, isbn, genre):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.genre = genre
        self.is_available = True
        self.due_date = None  # ← ADD THIS. None means "not checked out yet"

        Book.total_books += 1

    # ── DELETE your return_date() method entirely ──────────────
    # It was computing a fresh date every call which is wrong.
    # due_date stored on the instance replaces it completely.

    def check_out(self, loan_days=14):   # ← ADD loan_days parameter
        if self.is_available:
            self.is_available = False
            # ← SET due_date here, once, at checkout time
            self.due_date = datetime.now() + timedelta(days=loan_days)
            return (f"'{self.title}' checked out. "
                    f"Due: {self.due_date.strftime('%d %b %Y')}")
        return f"Sorry, '{self.title}' is currently unavailable."

    def return_book(self):
        if not self.is_available:
            self.is_available = True
            self.due_date = None    # ← CLEAR due_date on return
            return f"'{self.title}' has been returned. Thank you!"
        return f"'{self.title}' is already available in the library."

    def is_overdue(self):
        """Convenience method — returns True if overdue, False otherwise."""
        if self.due_date and not self.is_available:
            return datetime.now() > self.due_date
        return False

    def days_overdue(self):
        """Returns number of days overdue, 0 if not overdue."""
        if self.is_overdue():
            return (datetime.now() - self.due_date).days
        return 0

    def __str__(self):
        status = "Available" if self.is_available else "Checked Out"
        due = f" | Due: {self.due_date.strftime('%d %b %Y')}" if self.due_date else ""
        overdue = " ⚠ OVERDUE" if self.is_overdue() else ""
        return (f"'{self.title}' by {self.author} "
                f"(ISBN: {self.isbn}, Genre: {self.genre}) "
                f"— {status}{due}{overdue}")