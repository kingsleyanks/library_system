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
    """Used for returning a book — just needs the loan ID."""
    loan_id = serializers.IntegerField()

    def validate_loan_id(self, value):
        """validate_<fieldname>() runs for that specific field."""
        try:
            loan = Loan.objects.get(id=value, returned_on__isnull=True)
        except Loan.DoesNotExist:
            raise serializers.ValidationError(
                f"Active loan with ID {value} not found."
            )
        return value