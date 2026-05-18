from django.db import models
from django.utils import timezone

# Create your models here.
class Book(models.Model):
    isbn            = models.CharField(max_length=20, primary_key=True)
    title           = models.CharField(max_length=200)
    author          = models.CharField(max_length=100)
    genre           = models.CharField(max_length=50)
    is_available    = models.BooleanField(default=True)
    due_date        = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['title'] # Sort books by title
        
    def is_overdue(self):
    
        if self.due_date and not self.is_available:
            return self.due_date < timezone.now().date()
        return False
    
    def days_overdue(self):
        
        if self.is_overdue():
            return (timezone.now().date() - self.due_date).days
        return 0
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    
class Member(models.Model):
    MEMBER_TYPES = [
        ('Student',   'Student'),
        ('Staff',     'Staff'),
        ('Premium',   'Premium'),
        ('Librarian', 'Librarian'),
    ]
    
    member_id   = models.CharField(max_length=20, primary_key=True)
    name        = models.CharField(max_length=100)
    email       = models.EmailField()
    member_type = models.CharField(max_length=20, choices=MEMBER_TYPES)
    max_books   = models.IntegerField(default=5)
    loan_days   = models.IntegerField(default=14)
    paid_fines  = models.FloatField(default=0.0)
    
    def get_total_fines(self):
        """Calculates total outstanding fines for the member."""

        total = 0
        for loan in self.loan_set.filter(returned_on__isnull=True):
            if loan.due_date < timezone.now().date():
                days = (timezone.now().date() - loan.due_date).days
                total += days * 0.50
        return round(total, 2)
    
    def borrowed_books_count(self):
        return self.loan_set.filter(returned_on__isnull=True).count()

    def __str__(self):
        return f"{self.name} ({self.member_type})"
    
class Loan(models.Model):
    member      = models.ForeignKey(Member, on_delete=models.PROTECT)
    book        = models.ForeignKey(Book,   on_delete=models.PROTECT)
    borrowed_on = models.DateField(auto_now_add=True)
    due_date    = models.DateField()
    returned_on = models.DateField(null=True, blank=True)

    def is_overdue(self):

        if self.returned_on:
            return False
        return timezone.now().date() > self.due_date

    def __str__(self):
        return f"{self.member.name} — {self.book.title}"