import sqlite3
import os

class DatabaseConnection:
    """
    Manages the SQLite database connection.
    Uses a context manager so connection always closes cleanly.
    """
    DB_PATH = "library.db"
    
    def __init__(self):
        self.connection = None
    
    def __enter__(self):
        "Opens connection with entering 'with' block"
        self.connection = sqlite3.connect(self.DB_PATH)
        self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        "Closes connection with exiting 'with' block"
        if exc_type:
            self.connection.rollback() # Rollback if there was an exception
        else:
            self.connection.commit() # Commit if everything was successful
        self.connection.close()