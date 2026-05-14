# Library System

This project is a Library Management System designed to manage books and members in a library. It allows members to borrow and return books, calculate fines for overdue books, and manage the library's inventory efficiently.

## Features
- Add and manage books in the library.
- Register and manage library members.
- Borrow and return books.
- Calculate fines for overdue books.
- Track borrowed books for each member.

## Project Structure
```
library_system/
│
├── main.py          # Entry point of the application
├── models/          # Contains data models for the library system
│   ├── book.py      # Book class to manage book-related operations
│   └── member.py    # Member class to manage member-related operations
└── services/        # Contains service logic for the library system
    └── library.py   # Library service to manage overall operations
```

## How to Run
1. Navigate to the `library_system` directory.
2. Run the `main.py` file using Python:
   ```
   python main.py
   ```

## Requirements
- Python 3.10 or higher

## Future Enhancements
- Add a database to persist data.
- Implement a user interface for better usability.
- Add support for multiple libraries.