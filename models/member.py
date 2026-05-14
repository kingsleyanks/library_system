# models/member.py
import datetime

class Member:
    FINE_PER_DAY = 0.50  # Easy to update in one place
    MAX_BOOKS = 5       # ← Add this default

    def __init__(self, name, member_id, email):
        self.name = name
        self.member_id = member_id
        self.email = email
        self.borrowed_books = []
        self.paid_fines = 0.0  # Track total fines paid over lifetime

    # ── Borrowing ──────────────────────────────────────────────
    def get_number_of_borrowed_books(self):
        return len(self.borrowed_books)
    
    def check_if_can_borrow(self):
        return len(self.borrowed_books) < self.MAX_BOOKS
    
    def borrow_book(self, book):
        # ── Guard 1: borrowing limit ───────────────────────────────
        if not self.check_if_can_borrow():
            return (f"Borrowing limit reached. "
                    f"{self.name} can only borrow {self.MAX_BOOKS} book(s) at a time. "
                    f"Currently borrowed: {self.get_number_of_borrowed_books()}")

        # ── Guard 2: outstanding fines block borrowing ─────────────
        if self.get_total_fines() > 0:
            return (f"Cannot borrow. {self.name} has ${self.get_total_fines():.2f} "
                    f"in outstanding fines. Please pay before borrowing.")

        # ── Guard 3: already borrowed this book ───────────────────
        if book in self.borrowed_books:
            return f"'{book.title}' is already borrowed by {self.name}."
    
        result = book.check_out()
        if not book.is_available and book not in self.borrowed_books:
            self.borrowed_books.append(book)
        return result

    def return_book(self, book):
        if book in self.borrowed_books:
            self.borrowed_books.remove(book)
            return book.return_book()
        return f"'{book.title}' was not borrowed by {self.name}."

    # ── Fines ───────────────────────────────────────────────────

    def _calculate_fine_for_book(self, book):
        """Calculate overdue fine for a single book. Private helper."""
        if book.due_date and book.due_date < datetime.datetime.now():
            days_overdue = (datetime.datetime.now() - book.due_date).days
            return round(days_overdue * self.FINE_PER_DAY, 2)
        return 0

    def get_total_fines(self):
        """Return total outstanding fines across all borrowed books."""
        return round(sum(self._calculate_fine_for_book(b) for b in self.borrowed_books), 2)

    def get_fine_breakdown(self):
        """Return a detailed breakdown of fines per book."""
        breakdown = []
        for book in self.borrowed_books:
            fine = self._calculate_fine_for_book(book)
            if fine > 0:
                days = (datetime.datetime.now() - book.due_date).days
                breakdown.append(f"  '{book.title}' — {days} days overdue — ${fine:.2f}")
        return breakdown if breakdown else ["  No overdue books."]

    def pay_fine(self, amount):
        outstanding = self.get_total_fines()
        if outstanding == 0:
            return "You have no outstanding fines."
        if amount >= outstanding:
            self.paid_fines += outstanding
            return f"Fine of ${outstanding:.2f} paid in full. Change: ${amount - outstanding:.2f}"
        else:
            self.paid_fines += amount
            return f"Partial payment of ${amount:.2f} made. Still outstanding: ${outstanding - amount:.2f}"
        
    def get_number_of_borrowed_books(self):
        return len(self.borrowed_books)
    
    def check_if_can_borrow(self):
        return len(self.borrowed_books) < self.MAX_BOOKS

    # ── Display ─────────────────────────────────────────────────

    def __str__(self):
        fines = self.get_total_fines()
        books = [b.title for b in self.borrowed_books] or ["None"]
        return (
            f"Member : {self.name} (ID: {self.member_id})\n"
            f"Email  : {self.email}\n"
            f"Books  : {', '.join(books)}\n"
            f"Fines  : ${fines:.2f} outstanding | ${self.paid_fines:.2f} paid"
        )