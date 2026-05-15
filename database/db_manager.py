# database/db_manager.py
from database.db_connection import DatabaseConnection
import datetime


class DatabaseManager:
    """
    Provides methods to interact with the database.
    Uses DatabaseConnection for managing connections. 
    All database operations for the Library system.
    Each method opens a connection, does its job, closes it.
    """
    # ══════════════════════════════════════════════
    # SETUP
    # ══════════════════════════════════════════════
    
    def initialise_database(self):
        """
        Creates the necessary tables if they don't exist.
        """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                isbn        TEXT PRIMARY KEY,
                title       TEXT NOT NULL,
                author      TEXT NOT NULL,
                genre       TEXT NOT NULL,
                is_available INTEGER DEFAULT 1,
                due_date    TEXT
            )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    member_id   TEXT PRIMARY KEY,
                    name        TEXT NOT NULL,
                    email       TEXT NOT NULL,
                    member_type TEXT NOT NULL,
                    max_books   INTEGER DEFAULT 5,
                    loan_days   INTEGER DEFAULT 14,
                    paid_fines  REAL DEFAULT 0.0
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loans (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id   TEXT NOT NULL,
                    isbn        TEXT NOT NULL,
                    borrowed_on TEXT NOT NULL,
                    due_date    TEXT NOT NULL,
                    returned_on TEXT,
                    FOREIGN KEY (member_id) REFERENCES members(member_id),
                    FOREIGN KEY (isbn)      REFERENCES books(isbn)
                )
            """)
            
            print("✓ Database initialised")
            
    # ══════════════════════════════════════════════
    # BOOKS OPERATIONS
    # ══════════════════════════════════════════════
    
    def add_book(self, book):
        """
        Adds a new book to the database.
        """
        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO books (isbn, title, author, genre, is_available) 
                    VALUES (?, ?, ?, ?, ?)
                """, (book.isbn, book.title, book.author, book.genre, 1))
                return f"'{book.title}' added to database"
        except Exception as e:
            return f"Error adding book: {str(e)}"
        
    def get_all_books(self):
        """Returns a list of all books in the database as a list of dictionaries."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books")
            return cursor.fetchall()
        
    def get_availalable_books(self):
        """Returns only available books"""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books WHERE is_available = 1")
            return cursor.fetchall()
        
    def get_overdue_books(self):
        """ Returns all overdue books loans with book and member details """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT books.title,
                          books.author,
                          books.genre,
                          books.year,
                          members.name AS member_name,
                          members.email AS member_email,
                          loans.due_date,
                          julianday('now') - julianday(loans.due_date) AS days_overdue
                FROM loans 
                JOIN books ON loans.isbn = books.isbn 
                JOIN members ON loans.member_id = members.member_id 
                WHERE loans.returned_on IS NULL AND date(loans.due_date) < date('now')
                order by days_overdue DESC
            """)
            return cursor.fetchall()
        
    def update_book_availability(self, isbn, is_available, due_date=None):
        """Updates the availability status of a book."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE books 
                SET is_available = ?, due_date = ? 
                WHERE isbn = ?
            """, (1 if is_available else 0, due_date, isbn))
            
    def remove_book(self, isbn):
        """Removes a book from the database."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("Select is_available FROM books WHERE isbn = ?", (isbn,))
            row = cursor.fetchone()
            if row and row["is_available"] == 1:
                cursor.execute("DELETE FROM books WHERE isbn = ?", (isbn,))
                return f"Book with ISBN {isbn} removed from database"
            return f"Book with ISBN {isbn} is not available or does not exist"
        
        
    # ══════════════════════════════════════════════
    # MEMBERS OPERATIONS    
    # ══════════════════════════════════════════════
    
    def register_member(self, member):
        """ Insert a member into the database """
        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO members (member_id, name, email, member_type, max_books, loan_days)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (member.member_id,
                      member.name,
                      member.email,
                      member.get_member_type(),
                      member.MAX_BOOKS if member.MAX_BOOKS != float('inf') else 9999,
                      member.LOAN_PERIOD_DAYS))
                return f"Member '{member.name}' registered successfully"
        except Exception as e:
            return f"Error registering member: {str(e)}"
        
    def get_all_members(self):
        """Return all members."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members ORDER BY name")
            return cursor.fetchall()
        
    def get_member_loans(self, member_id):
        """Return all active loans for a member."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    books.title,
                    books.isbn,
                    loans.borrowed_on,
                    loans.due_date,
                    CASE
                        WHEN loans.due_date < DATE('now') THEN 'OVERDUE'
                        ELSE 'On Time'
                    END AS status
                FROM loans
                JOIN books ON loans.isbn = books.isbn
                WHERE loans.member_id  = ?
                AND   loans.returned_on IS NULL
                ORDER BY loans.due_date
            """, (member_id,))
            return cursor.fetchall()
        
    
    # ══════════════════════════════════════════════
    # LOAN OPERATIONS
    # ══════════════════════════════════════════════

    def record_loan(self, member_id, isbn, loan_days=14):
        """Record a new loan in the database."""
        today    = datetime.date.today().isoformat()
        due_date = (
            datetime.date.today() + datetime.timedelta(days=loan_days)
        ).isoformat()

        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO loans (member_id, isbn, borrowed_on, due_date)
                VALUES (?, ?, ?, ?)
            """, (member_id, isbn, today, due_date))

            # Update book availability
            cursor.execute("""
                UPDATE books SET is_available = 0, due_date = ?
                WHERE isbn = ?
            """, (due_date, isbn))

        return due_date

    def record_return(self, member_id, isbn):
        """Mark a loan as returned and restore book availability."""
        today = datetime.date.today().isoformat()
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE loans
                SET returned_on = ?
                WHERE member_id    = ?
                AND   isbn         = ?
                AND   returned_on IS NULL
            """, (today, member_id, isbn))

            cursor.execute("""
                UPDATE books
                SET is_available = 1,
                    due_date     = NULL
                WHERE isbn = ?
            """, (isbn,))

    # ══════════════════════════════════════════════
    # REPORTS
    # ══════════════════════════════════════════════

    def get_full_report(self):
        """Pull all report data in one query."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            # Summary stats
            cursor.execute("""
                SELECT
                    COUNT(*)                          AS total_books,
                    SUM(is_available)                 AS available,
                    COUNT(*) - SUM(is_available)      AS checked_out
                FROM books
            """)
            stats = cursor.fetchone()

            # Overdue count
            cursor.execute("""
                SELECT COUNT(*) AS overdue
                FROM loans
                WHERE returned_on IS NULL
                AND   due_date < DATE('now')
            """)
            overdue = cursor.fetchone()

            return dict(stats), dict(overdue)
        
    def get_member_report(self, member_id):
        """Full member report in one SQL query."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                WITH currently_borrowed AS (
                SELECT 
                    member_id,
                    COUNT(isbn) AS books_currently_borrowed
                FROM loans
                WHERE returned_on IS NULL
                GROUP BY  member_id
            ),
            ever_borrowed AS (
                SELECT member_id,
                    COUNT(isbn) AS total_books_ever_borrowed
                FROM loans
                GROUP BY  member_id
            ),
            total_days_overdue AS (
                SELECT member_id,
                    SUM(JULIANDAY('now') - JULIANDAY(due_date)) AS total_days_overdue
                FROM 
                    loans
                WHERE 
                   returned_on IS NULL 
                    AND DATE(due_date) < DATE('now')
                GROUP BY member_id
            )
            SELECT 
                members.member_id,
                members.name AS member_name,
                members.member_type,
                COALESCE(cb.books_currently_borrowed, 0) AS books_currently_borrowed,
                COALESCE(eb.total_books_ever_borrowed, 0) AS total_books_ever_borrowed,
                COALESCE(td.total_days_overdue, 0) AS total_days_overdue,
                COALESCE(td.total_days_overdue, 0) * 0.50 AS total_fines_owed
            FROM 
                members
            LEFT JOIN 
                currently_borrowed cb ON members.member_id = cb.member_id
            LEFT JOIN 
                ever_borrowed eb ON members.member_id = eb.member_id
            LEFT JOIN 
                total_days_overdue td ON members.member_id = td.member_id
            where members.member_id = ?
            """, (member_id,))
            return cursor.fetchone()