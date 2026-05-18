# library/serializers.py

from rest_framework import serializers
from library.models import Book, Member, Loan
from django.utils import timezone


class BookSerializer(serializers.ModelSerializer):
    """
    Converts Book objects to/from JSON.
    ModelSerializer automatically maps model fields to JSON fields.
    """
    is_overdue   = serializers.SerializerMethodField()
    days_overdue = serializers.SerializerMethodField()

    class Meta:
        model  = Book
        fields = [
            'isbn', 'title', 'author', 'genre',
            'is_available', 'due_date',
            'is_overdue', 'days_overdue'    # ← computed fields
        ]
        # isbn is set by user — not auto-generated
        read_only_fields = ['is_available', 'due_date']

    def get_is_overdue(self, obj):
        """SerializerMethodField calls this to compute the value."""
        return obj.is_overdue()

    def get_days_overdue(self, obj):
        return obj.days_overdue()


class MemberSerializer(serializers.ModelSerializer):
    total_fines          = serializers.SerializerMethodField()
    borrowed_books_count = serializers.SerializerMethodField()

    class Meta:
        model  = Member
        fields = [
            'member_id', 'name', 'email', 'member_type',
            'max_books', 'loan_days', 'paid_fines',
            'total_fines', 'borrowed_books_count'
        ]
        read_only_fields = ['paid_fines']

    def get_total_fines(self, obj):
        return obj.get_total_fines()

    def get_borrowed_books_count(self, obj):
        return obj.borrowed_books_count()

class LoanListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for loan list endpoints.
    Avoids expensive nested serializers and computed fields.
    """

    book_title  = serializers.CharField(source='book.title', read_only=True)
    member_name = serializers.CharField(source='member.name', read_only=True)

    class Meta:
        model = Loan
        fields = [
            'id',
            'book_title',
            'member_name',
            'borrowed_on',
            'due_date',
            'returned_on',
        ]

class LoanSerializer(serializers.ModelSerializer):
    """Detailed loan with nested book and member info."""
    book   = BookSerializer(read_only=True)
    member = MemberSerializer(read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model  = Loan
        fields = [
            'id', 'member', 'book',
            'borrowed_on', 'due_date', 'returned_on',
            'is_overdue'
        ]

    def get_is_overdue(self, obj):
        return obj.is_overdue()

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.select_related('book', 'member')

    def get_serializer_class(self):
        if self.action == 'list':
            return LoanListSerializer
        return LoanSerializer
    
class LoanCreateSerializer(serializers.Serializer):
    """
    Used specifically for creating loans — takes IDs not nested objects.
    Separate from LoanSerializer to keep reads and writes clean.
    """
    member_id = serializers.CharField()
    isbn      = serializers.CharField()

    def validate(self, data):
        """
        validate() runs after field-level validation.
        Raise ValidationError to reject the request with a clear message.
        """
        # Check member exists
        try:
            member = Member.objects.get(member_id=data['member_id'])
        except Member.DoesNotExist:
            raise serializers.ValidationError(
                {'member_id': f"Member '{data['member_id']}' not found."}
            )

        # Check book exists
        try:
            book = Book.objects.get(isbn=data['isbn'])
        except Book.DoesNotExist:
            raise serializers.ValidationError(
                {'isbn': f"Book '{data['isbn']}' not found."}
            )

        # Check book is available
        if not book.is_available:
            raise serializers.ValidationError(
                {'isbn': f"'{book.title}' is currently unavailable."}
            )

        # Check borrowing limit
        active_loans = Loan.objects.filter(
            member=member, returned_on__isnull=True
        ).count()
        if active_loans >= member.max_books:
            raise serializers.ValidationError(
                {'member_id': f"{member.name} has reached their borrowing limit."}
            )

        # Check outstanding fines
        if member.get_total_fines() > 0:
            raise serializers.ValidationError(
                {'member_id': f"{member.name} has ${member.get_total_fines():.2f} in outstanding fines."}
            )

        # Attach objects so the view can use them without re-querying
        data['member'] = member
        data['book']   = book
        return data


class ReturnSerializer(serializers.Serializer):
    """
    Used for returning a book.

    Optional member_id adds ownership validation so users
    cannot return loans belonging to someone else.
    """
    loan_id   = serializers.IntegerField()
    member_id = serializers.CharField(required=False)

    def validate(self, data):
        loan_id = data.get('loan_id')
        member_id = data.get('member_id')

        # Validate active loan exists
        try:
            loan = Loan.objects.select_related('member').get(
                id=loan_id,
                returned_on__isnull=True
            )
        except Loan.DoesNotExist:
            raise serializers.ValidationError({
                'loan_id': f"Active loan with ID {loan_id} not found."
            })

        # If member_id provided, verify ownership
        if member_id is not None:
            if loan.member.member_id != member_id:
                raise serializers.ValidationError({
                    'member_id': (
                        f"Loan {loan_id} does not belong to member "
                        f"'{member_id}'."
                    )
                })

        # Attach resolved objects for reuse in the view
        data['loan'] = loan
        return data