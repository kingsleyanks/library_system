import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from library.models import Book, Loan, Member


class MemberModelTests(TestCase):
    def test_total_fines_for_overdue_active_loan(self):
        member = Member.objects.create(
            member_id="MTEST1",
            name="Test Member",
            email="test@example.com",
            member_type="Student",
            max_books=3,
            loan_days=14,
        )
        book = Book.objects.create(
            isbn="ISBN-T1",
            title="Overdue Book",
            author="Author",
            genre="Tech",
            is_available=False,
            due_date=timezone.now().date() - datetime.timedelta(days=4),
        )
        Loan.objects.create(
            member=member,
            book=book,
            due_date=timezone.now().date() - datetime.timedelta(days=4),
        )

        self.assertEqual(member.get_total_fines(), 2.0)


class LibraryApiTests(TestCase):
    def setUp(self):
        self.member = Member.objects.create(
            member_id="M001",
            name="Alice",
            email="alice@example.com",
            member_type="Student",
            max_books=3,
            loan_days=14,
        )
        self.book = Book.objects.create(
            isbn="ISBN001",
            title="Clean Code",
            author="Robert Martin",
            genre="Tech",
        )

    def test_books_list_endpoint(self):
        response = self.client.get(reverse("api_book_list"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["isbn"], "ISBN001")

    def test_borrow_endpoint_creates_loan_and_marks_book_unavailable(self):
        response = self.client.post(
            reverse("api_borrow"),
            data={"member_id": self.member.member_id, "isbn": self.book.isbn},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.book.refresh_from_db()
        self.assertFalse(self.book.is_available)
        self.assertEqual(Loan.objects.filter(member=self.member, book=self.book).count(), 1)

    def test_return_endpoint_marks_book_available_and_closes_loan(self):
        borrow_response = self.client.post(
            reverse("api_borrow"),
            data={"member_id": self.member.member_id, "isbn": self.book.isbn},
            content_type="application/json",
        )
        self.assertEqual(borrow_response.status_code, 201)
        loan_id = borrow_response.json()["loan_id"]

        return_response = self.client.post(
            reverse("api_return"),
            data={"loan_id": loan_id, "member_id": self.member.member_id},
            content_type="application/json",
        )
        self.assertEqual(return_response.status_code, 200)

        self.book.refresh_from_db()
        loan = Loan.objects.get(id=loan_id)
        self.assertTrue(self.book.is_available)
        self.assertIsNotNone(loan.returned_on)

    def test_summary_endpoint_includes_counts_and_fines(self):
        due_date = timezone.now().date() - datetime.timedelta(days=2)
        self.book.is_available = False
        self.book.due_date = due_date
        self.book.save()
        Loan.objects.create(member=self.member, book=self.book, due_date=due_date)

        response = self.client.get(reverse("api_summary"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total_books"], 1)
        self.assertEqual(payload["available_books"], 0)
        self.assertEqual(payload["checked_out"], 1)
        self.assertEqual(payload["overdue_loans"], 1)
        self.assertEqual(payload["total_members"], 1)
        self.assertGreater(payload["total_fines_owed"], 0)


class LibraryTemplateViewTests(TestCase):
    def setUp(self):
        self.member = Member.objects.create(
            member_id="M100",
            name="Template User",
            email="template@example.com",
            member_type="Student",
            max_books=3,
            loan_days=14,
        )
        self.book = Book.objects.create(
            isbn="ISBN100",
            title="Template Book",
            author="Template Author",
            genre="Tech",
        )

    def test_dashboard_page_renders(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/dashboard.html")

    def test_book_list_page_renders(self):
        response = self.client.get(reverse("book_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/book_list.html")
        self.assertContains(response, self.book.title)

    def test_member_list_page_renders(self):
        response = self.client.get(reverse("member_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/member_list.html")
        self.assertContains(response, self.member.name)

    def test_forms_pages_render(self):
        self.assertEqual(self.client.get(reverse("book_add")).status_code, 200)
        self.assertEqual(self.client.get(reverse("member_add")).status_code, 200)
        self.assertEqual(self.client.get(reverse("borrow_book")).status_code, 200)
        self.assertEqual(self.client.get(reverse("return_book")).status_code, 200)

    def test_book_add_requires_all_fields(self):
        response = self.client.post(
            reverse("book_add"),
            data={"isbn": "ISBN200", "title": "", "author": "A", "genre": "Tech"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Book.objects.filter(isbn="ISBN200").exists())

    def test_member_add_rejects_duplicate_member_id(self):
        response = self.client.post(
            reverse("member_add"),
            data={
                "member_id": self.member.member_id,
                "name": "Another Name",
                "email": "another@example.com",
                "member_type": "Student",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Member.objects.filter(member_id=self.member.member_id).count(), 1)

    def test_borrow_flow_marks_book_unavailable(self):
        response = self.client.post(
            reverse("borrow_book"),
            data={"member_id": self.member.member_id, "isbn": self.book.isbn},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.book.refresh_from_db()
        self.assertFalse(self.book.is_available)
        self.assertEqual(
            Loan.objects.filter(member=self.member, book=self.book, returned_on__isnull=True).count(),
            1,
        )

    def test_return_flow_marks_book_available(self):
        loan = Loan.objects.create(
            member=self.member,
            book=self.book,
            due_date=timezone.now().date() + datetime.timedelta(days=7),
        )
        self.book.is_available = False
        self.book.due_date = loan.due_date
        self.book.save()

        response = self.client.post(reverse("return_book"), data={"loan_id": loan.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.book.refresh_from_db()
        loan.refresh_from_db()
        self.assertTrue(self.book.is_available)
        self.assertIsNotNone(loan.returned_on)
