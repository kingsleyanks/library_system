from django.contrib import admin

# Register your models here.
from django.contrib import admin
from library.models import Book, Member, Loan

admin.site.register(Book)
admin.site.register(Member)
admin.site.register(Loan)