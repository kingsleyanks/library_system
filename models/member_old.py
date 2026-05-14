#models/member.py

import datetime


class Member:
    def __init__(self, name, member_id, email):
        self.name = name
        self.member_id = member_id
        self.email = email
        self.borrowed_books = []  # List to keep track of borrowed books
        
    def borrow_book(self, book):
        result = book.check_out()  # Attempt to check out the book
        if book.is_available == False and book not in self.borrowed_books:  # If the book was successfully checked out
            self.borrowed_books.append(book)  # Add the book to the member's borrowed books list
        return result  # Return the result of the checkout attempt
    
    def return_book(self, book):
        if book in self.borrowed_books:
            self.borrowed_books.remove(book)  # Remove the book from the member's borrowed books list
            return book.return_book()  # Return the book to the library
        return f"'{book.title}' was not borrowed by {self.name}."  #
    
    def add_fine(self, book):
        # Placeholder for fine calculation logic
        fine =0
        if book.return_date() < datetime.datetime.now():
            days_overdue = (datetime.datetime.now() - book.return_date()).days
            fine = days_overdue * 0.50  # Example fine calculation: $0.50 per day overdue
            return fine, f"'{book.title}' is overdue by {days_overdue} days. Fine: ${fine:.2f}"
        else:
            return fine, f"'{book.title}' is not overdue."
       
    
    def pay_fine(self, amount):
        # Placeholder for fine calculation logic
        outstanding_fine = 0
        for book in self.borrowed_books:
            fine, _ = self.add_fine(book)
            outstanding_fine += fine

        if amount >= outstanding_fine:
            return f"Fine paid in full. Change: ${amount - outstanding_fine:.2f}"
        else:
            remaining_fine = outstanding_fine - amount
            return f"Partial payment made. Outstanding fine: ${remaining_fine:.2f}"
    
    def __str__(self):
        outstanding_fine = 0
        for book in self.borrowed_books:
            fine, _ = self.add_fine(book)
            outstanding_fine += fine
        return f"Member: {self.name} | (ID: {self.member_id} | Borrowed Books: {[book.title for book in self.borrowed_books]} | Outstanding Fines: ${outstanding_fine:.2f})"