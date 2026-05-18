# library/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from database.db_manager import DatabaseManager
import datetime

from library.models import Book, Member, Loan
from library.constants import MEMBER_LIMITS

# ══════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════

def dashboard(request):
    total_books         = Book.objects.count()
    total_members       = Member.objects.count()
    available_books     = Book.objects.filter(is_available=True).count()
    overdue_loans_qs = Loan.objects.filter(
    due_date__lt=timezone.now().date(),
    returned_on__isnull=True).select_related('book', 'member')
    context = {
        'total_books'    : total_books,
        'available_books': available_books,
        'checked_out'    : total_books - available_books,
        'total_members'  : total_members,
        'overdue_loans'  : overdue_loans_qs,          # queryset for template loop
        'overdue_count'  : overdue_loans_qs.count(),  # integer for stat card
    }
    return render(request, 'library/dashboard.html', context)

# ══════════════════════════════════════════════
# BOOKS
# ══════════════════════════════════════════════

def book_list(request):
    """Show all books with search and filter."""
    query  = request.GET.get('q', '')       # get search term from URL
    genre  = request.GET.get('genre', '')
    status = request.GET.get('status', '')

    books = Book.objects.all()

    if query:
        # Q objects let you combine conditions with OR
        books = books.filter(
            Q(title__icontains=query)  |
            Q(author__icontains=query) |
            Q(isbn__icontains=query)
        )
    if genre:
        books = books.filter(genre=genre)
    if status == 'available':
        books = books.filter(is_available=True)
    elif status == 'checked_out':
        books = books.filter(is_available=False)

    genres = Book.objects.values_list('genre', flat=True).distinct()

    context = {
        'books'  : books,
        'query'  : query,
        'genres' : genres,
        'status' : status,
    }
    return render(request, 'library/book_list.html', context)

def book_detail(request, isbn):
    """Show a single book and its loan history."""
    book  = get_object_or_404(Book, isbn=isbn)
    loans = Loan.objects.filter(book=book).order_by('-borrowed_on')
    context = {
        'book'  : book,
        'loans' : loans,
    }
    return render(request, 'library/book_detail.html', context)


def book_add(request):
    """Add a new book — handles both GET (show form) and POST (save)."""
    if request.method == 'POST':
        isbn   = request.POST.get('isbn').strip()
        title  = request.POST.get('title').strip()
        author = request.POST.get('author').strip()
        genre  = request.POST.get('genre').strip()

        # Validate
        if not all([isbn, title, author, genre]):
            messages.error(request, 'All fields are required.')
            return render(request, 'library/book_form.html')

        if Book.objects.filter(isbn=isbn).exists():
            messages.error(request, f'ISBN {isbn} already exists.')
            return render(request, 'library/book_form.html')

        Book.objects.create(
            isbn=isbn, title=title, author=author, genre=genre
        )
        messages.success(request, f"'{title}' added successfully.")
        return redirect('book_list')

    # GET request — just show the empty form
    return render(request, 'library/book_form.html')


# ══════════════════════════════════════════════
# MEMBERS
# ══════════════════════════════════════════════

def member_list(request):
    """Show all members."""
    members = Member.objects.all().order_by('name')
    context = {'members': members}
    return render(request, 'library/member_list.html', context)


def member_detail(request, member_id):
    """Show a single member and their active loans."""
    member       = get_object_or_404(Member, member_id=member_id)
    active_loans = Loan.objects.filter(
        member=member, returned_on__isnull=True
    )
    loan_history = Loan.objects.filter(
        member=member, returned_on__isnull=False
    ).order_by('-returned_on')

    context = {
        'member'      : member,
        'active_loans': active_loans,
        'loan_history': loan_history,
        'total_fines' : member.get_total_fines(),
    }
    return render(request, 'library/member_detail.html', context)


def member_add(request):
    """Register a new member."""
    if request.method == 'POST':
        member_id   = request.POST.get('member_id').strip()
        name        = request.POST.get('name').strip()
        email       = request.POST.get('email').strip()
        member_type = request.POST.get('member_type').strip()

        if not all([member_id, name, email, member_type]):
            messages.error(request, 'All fields are required.')
            return render(request, 'library/member_form.html')

        if Member.objects.filter(member_id=member_id).exists():
            messages.error(request, f'Member ID {member_id} already exists.')
            return render(request, 'library/member_form.html')

        # Use MEMBER_LIMITS constant
        config = MEMBER_LIMITS.get(member_type, {'max_books': 5, 'loan_days': 14})


        Member.objects.create(
            member_id   = member_id,
            name        = name,
            email       = email,
            member_type = member_type,
            max_books   = config['max_books'],
            loan_days   = config['loan_days'],
        )
        messages.success(request, f"Member '{name}' registered.")
        return redirect('member_list')

    return render(request, 'library/member_form.html')


# ══════════════════════════════════════════════
# LOANS
# ══════════════════════════════════════════════

def borrow_book(request):
    """Process a book loan."""
    if request.method == 'POST':
        member_id = request.POST.get('member_id').strip()
        isbn      = request.POST.get('isbn').strip()

        member = get_object_or_404(Member, member_id=member_id)
        book   = get_object_or_404(Book,   isbn=isbn)

        # Guard 1 — book available
        if not book.is_available:
            messages.error(request, f"'{book.title}' is not available.")
            return redirect('borrow_book')

        # Guard 2 — borrowing limit
        active_loans = Loan.objects.filter(
            member=member, returned_on__isnull=True
        ).count()
        if active_loans >= member.max_books:
            messages.error(
                request,
                f"{member.name} has reached their borrowing limit "
                f"({member.max_books} books)."
            )
            return redirect('borrow_book')

        # Guard 3 — outstanding fines
        if member.get_total_fines() > 0:
            messages.error(
                request,
                f"{member.name} has ${member.get_total_fines():.2f} "
                f"in outstanding fines."
            )
            return redirect('borrow_book')

        # All clear — create loan
        due_date = timezone.now().date() + datetime.timedelta(
            days=member.loan_days
        )
        Loan.objects.create(member=member, book=book, due_date=due_date)
        book.is_available = False
        book.due_date     = due_date
        book.save()

        messages.success(
            request,
            f"'{book.title}' checked out to {member.name}. "
            f"Due: {due_date.strftime('%d %b %Y')}"
        )
        return redirect('dashboard')

    # GET — show borrow form
    members = Member.objects.all().order_by('name')
    books   = Book.objects.filter(is_available=True).order_by('title')
    context = {'members': members, 'books': books}
    return render(request, 'library/borrow_form.html', context)


def return_book(request):
    """Process a book return."""
    if request.method == 'POST':
        loan_id = request.POST.get('loan_id')
        loan    = get_object_or_404(Loan, id=loan_id)

        loan.returned_on      = timezone.now().date()
        loan.book.is_available = True
        loan.book.due_date    = None
        loan.book.save()
        loan.save()

        messages.success(
            request, f"'{loan.book.title}' returned successfully."
        )
        return redirect('dashboard')

    # GET — show active loans to return
    active_loans = Loan.objects.filter(
        returned_on__isnull=True
    ).select_related('member', 'book').order_by('due_date')
    return render(
        request, 'library/return_form.html', {'loans': active_loans}
    )
    
# ══════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════

def member_report(request, member_id):
    """Render the member report in an HTML template."""
    db_manager = DatabaseManager()
    try:
        report = db_manager.get_member_report(member_id)
        return render(request, 'library/member_report.html', {'report': report})
    except Exception as e:
        messages.error(request, f"Error fetching report: {str(e)}")
        return redirect('member_list')