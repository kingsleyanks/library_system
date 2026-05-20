# library/constants.py

FINE_PER_DAY = 0.50

MEMBER_LIMITS = {
    'Student': {'max_books': 5, 'loan_days': 14},
    'Staff': {'max_books': 10, 'loan_days': 30},
    'Premium': {'max_books': 8, 'loan_days': 21},
    'Librarian': {'max_books': 999, 'loan_days': 30},
}