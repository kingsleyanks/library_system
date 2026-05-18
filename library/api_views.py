# library/api_views.py

from rest_framework.views     import APIView
from rest_framework.response  import Response
from rest_framework           import status
from database.db_manager      import DatabaseManager
from django.utils             import timezone
from django.db.models         import Q, Sum, F, ExpressionWrapper, FloatField
import datetime

from library.models       import Book, Member, Loan
from library.serializers  import (
    BookSerializer, MemberSerializer, LoanSerializer,
    LoanCreateSerializer, ReturnSerializer
)


# ══════════════════════════════════════════════
# BOOKS
# ══════════════════════════════════════════════

class BookListCreateView(APIView):
    """
    GET  /api/books/   → list all books
    POST /api/books/   → create a new book
    """

    def get(self, request):
        query  = request.query_params.get('q', '')
        genre  = request.query_params.get('genre', '')
        status_filter = request.query_params.get('status', '')

        books = Book.objects.all()

        if query:
            books = books.filter(
                Q(title__icontains=query)  |
                Q(author__icontains=query) |
                Q(isbn__icontains=query)
            )
        if genre:
            books = books.filter(genre__icontains=genre)
        if status_filter == 'available':
            books = books.filter(is_available=True)
        elif status_filter == 'checked_out':
            books = books.filter(is_available=False)

        serializer = BookSerializer(books, many=True)
        return Response({
            'count'  : books.count(),
            'results': serializer.data
        })

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class BookDetailView(APIView):
    """
    GET    /api/books/{isbn}/  → get one book
    PUT    /api/books/{isbn}/  → update a book
    DELETE /api/books/{isbn}/  → delete a book
    """

    def get_object(self, isbn):
        try:
            return Book.objects.get(isbn=isbn)
        except Book.DoesNotExist:
            return None

    def get(self, request, isbn):
        book = self.get_object(isbn)
        if not book:
            return Response(
                {'error': f"Book '{isbn}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(BookSerializer(book).data)

    def put(self, request, isbn):
        book = self.get_object(isbn)
        if not book:
            return Response(
                {'error': f"Book '{isbn}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, isbn):
        book = self.get_object(isbn)
        if not book:
            return Response(
                {'error': f"Book '{isbn}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        if not book.is_available:
            return Response(
                {'error': f"Cannot delete '{book.title}' — currently checked out."},
                status=status.HTTP_400_BAD_REQUEST
            )
        book.delete()
        return Response(
            {'message': f"'{book.title}' deleted."},
            status=status.HTTP_204_NO_CONTENT
        )


# ══════════════════════════════════════════════
# MEMBERS
# ══════════════════════════════════════════════

class MemberListCreateView(APIView):
    """
    GET  /api/members/  → list all members
    POST /api/members/  → register a new member
    """

    def get(self, request):
        members    = Member.objects.all().order_by('name')
        serializer = MemberSerializer(members, many=True)
        return Response({
            'count'  : members.count(),
            'results': serializer.data
        })

    def post(self, request):
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            # Set limits based on member type
            limits = {
                'Student'  : {'max_books': 3,   'loan_days': 14},
                'Staff'    : {'max_books': 10,  'loan_days': 30},
                'Premium'  : {'max_books': 8,   'loan_days': 21},
                'Librarian': {'max_books': 999, 'loan_days': 30},
            }
            member_type = serializer.validated_data.get('member_type', 'Student')
            config      = limits.get(member_type, {'max_books': 5, 'loan_days': 14})
            serializer.save(**config)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class MemberDetailView(APIView):
    """GET /api/members/{member_id}/ → get one member with their loans."""

    def get(self, request, member_id):
        try:
            member = Member.objects.get(member_id=member_id)
        except Member.DoesNotExist:
            return Response(
                {'error': f"Member '{member_id}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        active_loans = Loan.objects.filter(
            member=member, returned_on__isnull=True
        )
        loan_history = Loan.objects.filter(
            member=member, returned_on__isnull=False
        ).order_by('-returned_on')

        return Response({
            'member'      : MemberSerializer(member).data,
            'active_loans': LoanSerializer(active_loans, many=True).data,
            'loan_history': LoanSerializer(loan_history, many=True).data,
            'total_fines' : member.get_total_fines(),
        })


# ══════════════════════════════════════════════
# LOANS
# ══════════════════════════════════════════════

class BorrowBookView(APIView):
    """POST /api/loans/borrow/ → borrow a book."""

    def post(self, request):
        serializer = LoanCreateSerializer(data=request.data)
        if serializer.is_valid():
            member   = serializer.validated_data['member']
            book     = serializer.validated_data['book']
            due_date = (
                timezone.now().date() +
                datetime.timedelta(days=member.loan_days)
            )

            loan             = Loan.objects.create(
                member   = member,
                book     = book,
                due_date = due_date
            )
            book.is_available = False
            book.due_date     = due_date
            book.save()

            return Response({
                'message' : f"'{book.title}' checked out to {member.name}.",
                'due_date': due_date,
                'loan_id' : loan.id,
            }, status=status.HTTP_201_CREATED)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ReturnBookView(APIView):
    """POST /api/loans/return/ → return a book."""

    def post(self, request):
        serializer = ReturnSerializer(data=request.data)
        if serializer.is_valid():
            loan             = Loan.objects.get(
                id=serializer.validated_data['loan_id']
            )
            loan.returned_on      = timezone.now().date()
            loan.book.is_available = True
            loan.book.due_date    = None
            loan.book.save()
            loan.save()

            return Response({
                'message': f"'{loan.book.title}' returned successfully.",
                'loan_id': loan.id,
            })

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class OverdueLoansView(APIView):
    """GET /api/loans/overdue/ → list all overdue loans."""

    def get(self, request):
        overdue_loans = Loan.objects.filter(
            returned_on__isnull=True,
            due_date__lt=timezone.now().date()
        ).select_related('member', 'book').order_by('due_date')

        return Response({
            'count'  : overdue_loans.count(),
            'results': LoanSerializer(overdue_loans, many=True).data
        })


# ══════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════

class LibrarySummaryView(APIView):
    """GET /api/reports/summary/ → high level library stats."""

    def get(self, request):
        total_books     = Book.objects.count()
        available_books = Book.objects.filter(is_available=True).count()
        overdue_count   = Loan.objects.filter(
            returned_on__isnull=True,
            due_date__lt=timezone.now().date()
        ).count()
        total_members   = Member.objects.count()
        # total_fines     = sum(
        #     m.get_total_fines() for m in Member.objects.all()
        # )
        today = timezone.now().date()
        total_fines = (
            Loan.objects
            .filter(returned_on__isnull=True, due_date__lt=today)
            .annotate(days=ExpressionWrapper(
                today - F('due_date'), output_field=FloatField()
            ))
            .aggregate(total=Sum('days'))['total'] or 0
        ) * 0.50

        return Response({
            'total_books'    : total_books,
            'available_books': available_books,
            'checked_out'    : total_books - available_books,
            'overdue_loans'  : overdue_count,
            'total_members'  : total_members,
            'total_fines_owed': round(total_fines, 2),
        })
        
class MemberReportView(APIView):
    """GET /api/members/{member_id}/report/ → detailed member report."""

    def get(self, request, member_id):
        db_manager = DatabaseManager()
        try:
            report = db_manager.get_member_report(member_id)
            if not report:
                return Response(
                    {'error': f"Member '{member_id}' not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(dict(report), status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )