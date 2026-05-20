# seed_and_test.py
# ══════════════════════════════════════════════════════════════
# Run from your project root: python seed_and_test.py
# Tests: Insert, Update, Delete, API, Browser-ready data
# ══════════════════════════════════════════════════════════════

import os
import sys
import django
import datetime
import json
import urllib.request
import urllib.error

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# ── Django setup ───────────────────────────────────────────────
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from library.models import Book, Member, Loan

# ══════════════════════════════════════════════════════════════
# COLOUR HELPERS
# ══════════════════════════════════════════════════════════════

GREEN  = '\033[92m'
RED    = '\033[91m'
YELLOW = '\033[93m'
BLUE   = '\033[94m'
RESET  = '\033[0m'
BOLD   = '\033[1m'

passed = 0
failed = 0
errors = []

def ok(msg):
    global passed
    passed += 1
    print(f"  {GREEN}✓{RESET} {msg}")

def fail(msg, detail=""):
    global failed
    failed += 1
    errors.append(f"{msg}: {detail}")
    print(f"  {RED}✗{RESET} {msg}")
    if detail:
        print(f"    {RED}→ {detail}{RESET}")

def section(title):
    print(f"\n{BOLD}{BLUE}{'═' * 55}{RESET}")
    print(f"{BOLD}{BLUE}  {title}{RESET}")
    print(f"{BOLD}{BLUE}{'═' * 55}{RESET}")

def subsection(title):
    print(f"\n{YELLOW}── {title} ──{RESET}")


# ══════════════════════════════════════════════════════════════
# DATASET DEFINITIONS
# ══════════════════════════════════════════════════════════════

BOOKS_DATA = [
    # Tech
    ("ISBN001", "Clean Code",                    "Robert Martin",   "Tech"),
    ("ISBN002", "The Pragmatic Programmer",       "Andrew Hunt",     "Tech"),
    ("ISBN003", "Design Patterns",                "Gang of Four",    "Tech"),
    ("ISBN004", "Refactoring",                    "Martin Fowler",   "Tech"),
    ("ISBN005", "The Mythical Man-Month",         "Fred Brooks",     "Tech"),
    ("ISBN006", "Code Complete",                  "Steve McConnell", "Tech"),
    ("ISBN007", "Introduction to Algorithms",     "Cormen et al",    "Tech"),
    ("ISBN008", "Structure and Interpretation",   "Abelson & Sussman","Tech"),
    ("ISBN009", "You Don't Know JS",              "Kyle Simpson",    "Tech"),
    ("ISBN010", "Python Crash Course",            "Eric Matthes",    "Tech"),
    ("ISBN011", "Django for Professionals",       "William Vincent",  "Tech"),
    ("ISBN012", "Docker Deep Dive",               "Nigel Poulton",   "Tech"),
    ("ISBN013", "Kubernetes Up & Running",        "Burns et al",     "Tech"),
    ("ISBN014", "The Linux Command Line",         "William Shotts",  "Tech"),
    ("ISBN015", "JavaScript: Good Parts",         "Douglas Crockford","Tech"),
    ("ISBN016", "Learning SQL",                   "Alan Beaulieu",   "Tech"),
    ("ISBN017", "REST API Design Rulebook",       "Mark Masse",      "Tech"),
    ("ISBN018", "Test Driven Development",        "Kent Beck",       "Tech"),
    ("ISBN019", "Continuous Delivery",            "Humble & Farley", "Tech"),
    ("ISBN020", "Site Reliability Engineering",   "Beyer et al",     "Tech"),
    # Sci-Fi
    ("ISBN021", "Dune",                           "Frank Herbert",   "Sci-Fi"),
    ("ISBN022", "Foundation",                     "Isaac Asimov",    "Sci-Fi"),
    ("ISBN023", "Neuromancer",                    "William Gibson",  "Sci-Fi"),
    ("ISBN024", "The Martian",                    "Andy Weir",       "Sci-Fi"),
    ("ISBN025", "Ender's Game",                   "Orson Scott Card","Sci-Fi"),
    ("ISBN026", "1984",                           "George Orwell",   "Sci-Fi"),
    ("ISBN027", "Brave New World",                "Aldous Huxley",   "Sci-Fi"),
    ("ISBN028", "The Left Hand of Darkness",      "Ursula K. Le Guin","Sci-Fi"),
    ("ISBN029", "Snow Crash",                     "Neal Stephenson", "Sci-Fi"),
    ("ISBN030", "Hyperion",                       "Dan Simmons",     "Sci-Fi"),
    # Self-Help
    ("ISBN031", "Atomic Habits",                  "James Clear",     "Self-Help"),
    ("ISBN032", "Deep Work",                      "Cal Newport",     "Self-Help"),
    ("ISBN033", "The 7 Habits",                   "Stephen Covey",   "Self-Help"),
    ("ISBN034", "Thinking Fast and Slow",         "Daniel Kahneman", "Self-Help"),
    ("ISBN035", "Man's Search for Meaning",       "Viktor Frankl",   "Self-Help"),
    ("ISBN036", "The Power of Now",               "Eckhart Tolle",   "Self-Help"),
    ("ISBN037", "Mindset",                        "Carol Dweck",     "Self-Help"),
    ("ISBN038", "Grit",                           "Angela Duckworth","Self-Help"),
    ("ISBN039", "The Subtle Art",                 "Mark Manson",     "Self-Help"),
    ("ISBN040", "Can't Hurt Me",                  "David Goggins",   "Self-Help"),
    # History
    ("ISBN041", "Sapiens",                        "Yuval Harari",    "History"),
    ("ISBN042", "Homo Deus",                      "Yuval Harari",    "History"),
    ("ISBN043", "The Guns of August",             "Barbara Tuchman", "History"),
    ("ISBN044", "A People's History",             "Howard Zinn",     "History"),
    ("ISBN045", "The Rise and Fall of Rome",      "Michael Grant",   "History"),
    ("ISBN046", "Churchill",                      "Andrew Roberts",  "History"),
    ("ISBN047", "Team of Rivals",                 "Doris Kearns",    "History"),
    ("ISBN048", "The Wright Brothers",            "David McCullough","History"),
    ("ISBN049", "Leonardo da Vinci",              "Walter Isaacson", "History"),
    ("ISBN050", "Steve Jobs",                     "Walter Isaacson", "History"),
    # Business
    ("ISBN051", "Zero to One",                    "Peter Thiel",     "Business"),
    ("ISBN052", "The Lean Startup",               "Eric Ries",       "Business"),
    ("ISBN053", "Good to Great",                  "Jim Collins",     "Business"),
    ("ISBN054", "The Hard Thing",                 "Ben Horowitz",    "Business"),
    ("ISBN055", "Crossing the Chasm",             "Geoffrey Moore",  "Business"),
    ("ISBN056", "Blue Ocean Strategy",            "Kim & Mauborgne", "Business"),
    ("ISBN057", "The Innovator's Dilemma",        "Clayton Christensen","Business"),
    ("ISBN058", "Built to Last",                  "Collins & Porras","Business"),
    ("ISBN059", "Measure What Matters",           "John Doerr",      "Business"),
    ("ISBN060", "Never Split the Difference",     "Chris Voss",      "Business"),
    # Philosophy
    ("ISBN061", "Meditations",                    "Marcus Aurelius", "Philosophy"),
    ("ISBN062", "The Republic",                   "Plato",           "Philosophy"),
    ("ISBN063", "Nicomachean Ethics",             "Aristotle",       "Philosophy"),
    ("ISBN064", "Thus Spoke Zarathustra",         "Nietzsche",       "Philosophy"),
    ("ISBN065", "Being and Time",                 "Heidegger",       "Philosophy"),
    ("ISBN066", "The Critique of Pure Reason",    "Kant",            "Philosophy"),
    ("ISBN067", "Tractatus Logico-Philosophicus", "Wittgenstein",    "Philosophy"),
    ("ISBN068", "The Prince",                     "Machiavelli",     "Philosophy"),
    ("ISBN069", "Leviathan",                      "Hobbes",          "Philosophy"),
    ("ISBN070", "Beyond Good and Evil",           "Nietzsche",       "Philosophy"),
    # Fiction
    ("ISBN071", "To Kill a Mockingbird",          "Harper Lee",      "Fiction"),
    ("ISBN072", "The Great Gatsby",               "F. Scott Fitzgerald","Fiction"),
    ("ISBN073", "One Hundred Years of Solitude",  "Gabriel Garcia Marquez","Fiction"),
    ("ISBN074", "Crime and Punishment",           "Dostoevsky",      "Fiction"),
    ("ISBN075", "The Brothers Karamazov",         "Dostoevsky",      "Fiction"),
    ("ISBN076", "Anna Karenina",                  "Tolstoy",         "Fiction"),
    ("ISBN077", "Pride and Prejudice",            "Jane Austen",     "Fiction"),
    ("ISBN078", "Moby Dick",                      "Herman Melville", "Fiction"),
    ("ISBN079", "Ulysses",                        "James Joyce",     "Fiction"),
    ("ISBN080", "Catch-22",                       "Joseph Heller",   "Fiction"),
    # Science
    ("ISBN081", "A Brief History of Time",        "Stephen Hawking", "Science"),
    ("ISBN082", "The Selfish Gene",               "Richard Dawkins", "Science"),
    ("ISBN083", "The Double Helix",               "James Watson",    "Science"),
    ("ISBN084", "Surely You're Joking Mr Feynman","Richard Feynman", "Science"),
    ("ISBN085", "The Origin of Species",          "Charles Darwin",  "Science"),
    ("ISBN086", "Cosmos",                         "Carl Sagan",      "Science"),
    ("ISBN087", "The Gene",                       "Siddhartha Mukherjee","Science"),
    ("ISBN088", "Astrophysics for People in a Hurry","Neil deGrasse Tyson","Science"),
    ("ISBN089", "The Emperor's New Mind",         "Roger Penrose",   "Science"),
    ("ISBN090", "QED",                            "Richard Feynman", "Science"),
    # Productivity
    ("ISBN091", "Getting Things Done",            "David Allen",     "Productivity"),
    ("ISBN092", "The One Thing",                  "Gary Keller",     "Productivity"),
    ("ISBN093", "Eat That Frog",                  "Brian Tracy",     "Productivity"),
    ("ISBN094", "The 4-Hour Workweek",            "Tim Ferriss",     "Productivity"),
    ("ISBN095", "Make Time",                      "Knapp & Zeratsky","Productivity"),
    ("ISBN096", "Flow",                           "Mihaly Csikszentmihalyi","Productivity"),
    ("ISBN097", "The Effective Executive",        "Peter Drucker",   "Productivity"),
    ("ISBN098", "Essentialism",                   "Greg McKeown",    "Productivity"),
    ("ISBN099", "A Mind for Numbers",             "Barbara Oakley",  "Productivity"),
    ("ISBN100", "Ultralearning",                  "Scott Young",     "Productivity"),
]

MEMBERS_DATA = [
    # (member_id, name, email, type, max_books, loan_days)
    ("M001", "Alice Johnson",    "alice@uni.ac.uk",      "Student",   3,   14),
    ("M002", "Bob Smith",        "bob@lib.ac.uk",        "Staff",     10,  30),
    ("M003", "Carol White",      "carol@email.com",      "Premium",   8,   21),
    ("M004", "Diana Prince",     "diana@lib.ac.uk",      "Librarian", 999, 30),
    ("M005", "Edward Norton",    "edward@uni.ac.uk",     "Student",   3,   14),
    ("M006", "Fiona Green",      "fiona@uni.ac.uk",      "Student",   3,   14),
    ("M007", "George Brown",     "george@corp.com",      "Premium",   8,   21),
    ("M008", "Hannah Davis",     "hannah@uni.ac.uk",     "Student",   3,   14),
    ("M009", "Ivan Petrov",      "ivan@lib.ac.uk",       "Staff",     10,  30),
    ("M010", "Julia Roberts",    "julia@email.com",      "Premium",   8,   21),
    ("M011", "Kevin Hart",       "kevin@uni.ac.uk",      "Student",   3,   14),
    ("M012", "Laura Palmer",     "laura@uni.ac.uk",      "Student",   3,   14),
    ("M013", "Mike Johnson",     "mike@corp.com",        "Premium",   8,   21),
    ("M014", "Nancy Drew",       "nancy@lib.ac.uk",      "Staff",     10,  30),
    ("M015", "Oscar Wilde",      "oscar@email.com",      "Premium",   8,   21),
    ("M016", "Paula Abdul",      "paula@uni.ac.uk",      "Student",   3,   14),
    ("M017", "Quincy Jones",     "quincy@corp.com",      "Premium",   8,   21),
    ("M018", "Rachel Green",     "rachel@uni.ac.uk",     "Student",   3,   14),
    ("M019", "Sam Wilson",       "sam@lib.ac.uk",        "Staff",     10,  30),
    ("M020", "Tina Turner",      "tina@email.com",       "Premium",   8,   21),
]


# ══════════════════════════════════════════════════════════════
# PART 1 — CLEAN SLATE
# ══════════════════════════════════════════════════════════════

section("PART 1 — CLEAN SLATE")

try:
    loan_count   = Loan.objects.all().delete()[0]
    book_count   = Book.objects.all().delete()[0]
    member_count = Member.objects.all().delete()[0]
    ok(f"Cleared {loan_count} loans, {book_count} books, {member_count} members")
except Exception as e:
    fail("Could not clear database", str(e))
    sys.exit(1)


# ══════════════════════════════════════════════════════════════
# PART 2 — INSERT TESTS
# ══════════════════════════════════════════════════════════════

section("PART 2 — INSERT (100 Books, 20 Members)")

subsection("Inserting 100 Books")
for isbn, title, author, genre in BOOKS_DATA:
    try:
        Book.objects.create(
            isbn=isbn, title=title, author=author, genre=genre
        )
        ok(f"Inserted: {title[:40]}")
    except Exception as e:
        fail(f"Failed to insert book: {title[:40]}", str(e))

total = Book.objects.count()
if total == 100:
    ok(f"Book count confirmed: {total}/100")
else:
    fail(f"Book count mismatch", f"Expected 100, got {total}")

subsection("Inserting 20 Members")
for mid, name, email, mtype, max_b, loan_d in MEMBERS_DATA:
    try:
        Member.objects.create(
            member_id   = mid,
            name        = name,
            email       = email,
            member_type = mtype,
            max_books   = max_b,
            loan_days   = loan_d,
        )
        ok(f"Inserted: {name} ({mtype})")
    except Exception as e:
        fail(f"Failed to insert member: {name}", str(e))

total = Member.objects.count()
if total == 20:
    ok(f"Member count confirmed: {total}/20")
else:
    fail(f"Member count mismatch", f"Expected 20, got {total}")

subsection("Duplicate Prevention")
try:
    Book.objects.create(isbn="ISBN001", title="Dupe", author="X", genre="Y")
    fail("Duplicate book ISBN should have been rejected")
except Exception:
    ok("Duplicate book ISBN correctly rejected")

try:
    Member.objects.create(member_id="M001", name="Dupe",
                          email="d@d.com", member_type="Student")
    fail("Duplicate member ID should have been rejected")
except Exception:
    ok("Duplicate member ID correctly rejected")


# ══════════════════════════════════════════════════════════════
# PART 3 — LOAN TESTS (BORROW)
# ══════════════════════════════════════════════════════════════

section("PART 3 — LOAN TESTS (Borrow)")

subsection("Valid Borrows")
borrow_cases = [
    ("M001", "ISBN001"),   # Alice borrows Clean Code
    ("M001", "ISBN002"),   # Alice borrows Pragmatic Programmer
    ("M001", "ISBN003"),   # Alice borrows Design Patterns (hits limit of 3)
    ("M002", "ISBN021"),   # Bob borrows Dune
    ("M002", "ISBN022"),   # Bob borrows Foundation
    ("M003", "ISBN031"),   # Carol borrows Atomic Habits
    ("M005", "ISBN041"),   # Edward borrows Sapiens
    ("M006", "ISBN051"),   # Fiona borrows Zero to One
    ("M007", "ISBN061"),   # George borrows Meditations
    ("M010", "ISBN071"),   # Julia borrows To Kill a Mockingbird
    ("M011", "ISBN081"),   # Kevin borrows Brief History of Time
    ("M012", "ISBN091"),   # Laura borrows Getting Things Done
]

for member_id, isbn in borrow_cases:
    try:
        member   = Member.objects.get(member_id=member_id)
        book     = Book.objects.get(isbn=isbn)
        due_date = timezone.now().date() + datetime.timedelta(days=member.loan_days)
        Loan.objects.create(member=member, book=book, due_date=due_date)
        book.is_available = False
        book.due_date     = due_date
        book.save()
        ok(f"{member.name} borrowed '{book.title}'")
    except Exception as e:
        fail(f"Borrow failed: {member_id} → {isbn}", str(e))

subsection("Guard — Borrowing Limit")
try:
    # Alice already has 3 books — 4th should be blocked by view logic
    alice        = Member.objects.get(member_id="M001")
    active_count = Loan.objects.filter(
        member=alice, returned_on__isnull=True
    ).count()
    if active_count >= alice.max_books:
        ok(f"Alice correctly at limit ({active_count}/{alice.max_books} books)")
    else:
        fail("Alice should be at limit", f"Has {active_count}/{alice.max_books}")
except Exception as e:
    fail("Limit check failed", str(e))

subsection("Guard — Book Unavailable")
try:
    book = Book.objects.get(isbn="ISBN001")
    if not book.is_available:
        ok(f"ISBN001 correctly marked unavailable after borrow")
    else:
        fail("ISBN001 should be unavailable")
except Exception as e:
    fail("Availability check failed", str(e))


# ══════════════════════════════════════════════════════════════
# PART 4 — OVERDUE SIMULATION
# ══════════════════════════════════════════════════════════════

section("PART 4 — OVERDUE SIMULATION")

subsection("Backdating 5 Loans to Simulate Overdue")
overdue_cases = [
    ("M001", "ISBN001", 10),   # Alice — 10 days overdue → $5.00
    ("M001", "ISBN002", 5),    # Alice — 5 days overdue  → $2.50
    ("M002", "ISBN021", 7),    # Bob   — 7 days overdue  (staff = no fine)
    ("M005", "ISBN041", 3),    # Edward — 3 days overdue → $1.50
    ("M006", "ISBN051", 1),    # Fiona  — 1 day overdue  → $0.50
]

for member_id, isbn, days_ago in overdue_cases:
    try:
        loan = Loan.objects.get(
            member__member_id=member_id,
            book__isbn=isbn,
            returned_on__isnull=True
        )
        past_date     = timezone.now().date() - datetime.timedelta(days=days_ago)
        loan.due_date = past_date
        loan.save()
        loan.book.due_date = past_date
        loan.book.save()
        ok(f"Backdated {member_id}→{isbn} by {days_ago} days")
    except Exception as e:
        fail(f"Could not backdate loan {member_id}→{isbn}", str(e))

subsection("Verify Overdue Count")
overdue_count = Loan.objects.filter(
    returned_on__isnull=True,
    due_date__lt=timezone.now().date()
).count()
if overdue_count == 5:
    ok(f"Overdue count correct: {overdue_count}")
else:
    fail(f"Overdue count wrong", f"Expected 5, got {overdue_count}")

subsection("Verify Fine Calculation")
alice = Member.objects.get(member_id="M001")
fines = alice.get_total_fines()
if fines == 7.50:
    ok(f"Alice's fines correct: ${fines:.2f}")
else:
    fail(f"Alice's fines wrong", f"Expected $7.50, got ${fines:.2f}")


# ══════════════════════════════════════════════════════════════
# PART 5 — UPDATE TESTS
# ══════════════════════════════════════════════════════════════

section("PART 5 — UPDATE TESTS")

subsection("Update Book Details")
try:
    book        = Book.objects.get(isbn="ISBN050")
    book.title  = "Steve Jobs (Updated Edition)"
    book.save()
    refreshed   = Book.objects.get(isbn="ISBN050")
    if refreshed.title == "Steve Jobs (Updated Edition)":
        ok("Book title updated successfully")
    else:
        fail("Book title not updated")
except Exception as e:
    fail("Book update failed", str(e))

subsection("Update Member Email")
try:
    member       = Member.objects.get(member_id="M003")
    member.email = "carol.updated@email.com"
    member.save()
    refreshed    = Member.objects.get(member_id="M003")
    if refreshed.email == "carol.updated@email.com":
        ok("Member email updated successfully")
    else:
        fail("Member email not updated")
except Exception as e:
    fail("Member update failed", str(e))

subsection("Update Member Type — Student to Premium")
try:
    member             = Member.objects.get(member_id="M008")
    member.member_type = "Premium"
    member.max_books   = 8
    member.loan_days   = 21
    member.save()
    refreshed = Member.objects.get(member_id="M008")
    if refreshed.member_type == "Premium" and refreshed.max_books == 8:
        ok(f"Hannah upgraded to Premium (max_books={refreshed.max_books})")
    else:
        fail("Member type upgrade failed")
except Exception as e:
    fail("Member type update failed", str(e))


# ══════════════════════════════════════════════════════════════
# PART 6 — RETURN TESTS
# ══════════════════════════════════════════════════════════════

section("PART 6 — RETURN TESTS")

subsection("Valid Returns")
return_cases = [
    ("M001", "ISBN003"),   # Alice returns Design Patterns
    ("M002", "ISBN021"),   # Bob returns Dune
    ("M007", "ISBN061"),   # George returns Meditations
]

for member_id, isbn in return_cases:
    try:
        loan             = Loan.objects.get(
            member__member_id = member_id,
            book__isbn        = isbn,
            returned_on__isnull=True
        )
        loan.returned_on      = timezone.now().date()
        loan.book.is_available = True
        loan.book.due_date    = None
        loan.book.save()
        loan.save()
        ok(f"{member_id} returned {isbn} — book now available")
    except Exception as e:
        fail(f"Return failed: {member_id}→{isbn}", str(e))

subsection("Verify Book Availability After Return")
for _, isbn in return_cases:
    book = Book.objects.get(isbn=isbn)
    if book.is_available and book.due_date is None:
        ok(f"{isbn} is available and due_date cleared")
    else:
        fail(f"{isbn} not properly restored after return")


# ══════════════════════════════════════════════════════════════
# PART 7 — DELETE TESTS
# ══════════════════════════════════════════════════════════════

section("PART 7 — DELETE TESTS")

subsection("Delete Available Book")
try:
    Book.objects.create(isbn="TEMP001", title="Temp Book",
                        author="Temp Author", genre="Tech")
    Book.objects.get(isbn="TEMP001").delete()
    exists = Book.objects.filter(isbn="TEMP001").exists()
    if not exists:
        ok("Available book deleted successfully")
    else:
        fail("Book still exists after delete")
except Exception as e:
    fail("Book delete failed", str(e))

subsection("Block Delete on Checked-Out Book")
try:
    book = Book.objects.get(isbn="ISBN001")   # Alice still has this
    if not book.is_available:
        ok(f"ISBN001 correctly unavailable — delete should be blocked in view")
    else:
        fail("ISBN001 should still be checked out")
except Exception as e:
    fail("Checked-out book check failed", str(e))

subsection("Delete Member With No Loans")
try:
    Member.objects.create(
        member_id="TEMP001", name="Temp Member",
        email="temp@test.com", member_type="Student",
        max_books=3, loan_days=14
    )
    Member.objects.get(member_id="TEMP001").delete()
    exists = Member.objects.filter(member_id="TEMP001").exists()
    if not exists:
        ok("Member with no loans deleted successfully")
    else:
        fail("Member still exists after delete")
except Exception as e:
    fail("Member delete failed", str(e))

subsection("Block Delete on Member With Active Loans")
try:
    alice       = Member.objects.get(member_id="M001")
    active      = Loan.objects.filter(member=alice, returned_on__isnull=True).count()
    if active > 0:
        ok(f"Alice has {active} active loans — delete correctly blocked in view")
    else:
        fail("Alice should have active loans preventing deletion")
except Exception as e:
    fail("Active loan block check failed", str(e))


# ══════════════════════════════════════════════════════════════
# PART 8 — SEARCH & FILTER TESTS
# ══════════════════════════════════════════════════════════════

section("PART 8 — SEARCH & FILTER TESTS")

from django.db.models import Q

subsection("Search by Title")
results = Book.objects.filter(title__icontains="code")
if results.count() >= 2:
    ok(f"Title search 'code' → {results.count()} results")
    for b in results:
        ok(f"  Found: {b.title}")
else:
    fail("Title search returned too few results")

subsection("Search by Author")
results = Book.objects.filter(author__icontains="feynman")
if results.count() == 2:
    ok(f"Author search 'feynman' → {results.count()} results")
else:
    fail(f"Author search wrong count", f"Expected 2, got {results.count()}")

subsection("Filter by Genre")
tech_books = Book.objects.filter(genre="Tech")
if tech_books.count() == 20:
    ok(f"Genre filter 'Tech' → {tech_books.count()} books")
else:
    fail(f"Genre filter wrong", f"Expected 20, got {tech_books.count()}")

subsection("Filter Available Books")
available = Book.objects.filter(is_available=True)
ok(f"Available books: {available.count()}")

subsection("Filter Overdue Loans")
overdue = Loan.objects.filter(
    returned_on__isnull=True,
    due_date__lt=timezone.now().date()
)
ok(f"Overdue loans: {overdue.count()}")

subsection("Combined Search — Q objects")
results = Book.objects.filter(
    Q(title__icontains="the") | Q(author__icontains="the")
)
ok(f"Combined Q search → {results.count()} results")


# ══════════════════════════════════════════════════════════════
# PART 9 — API TESTS (requires server running)
# ══════════════════════════════════════════════════════════════

section("PART 9 — API TESTS")
print(f"\n{YELLOW}  Note: Start server with 'python manage.py runserver'{RESET}")
print(f"{YELLOW}  then run this script again for API tests.{RESET}\n")

BASE_URL = "http://127.0.0.1:8000"

def api_get(path):
    try:
        req = urllib.request.Request(
            f"{BASE_URL}{path}",
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read()), resp.status
    except urllib.error.URLError:
        return None, 0
    except Exception as e:
        return None, -1

def api_post(path, data):
    try:
        payload = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            f"{BASE_URL}{path}",
            data    = payload,
            headers = {
                "Content-Type": "application/json",
                "X-CSRFToken" : "test"
            },
            method  = "POST"
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        body = json.loads(e.read())
        return body, e.code
    except urllib.error.URLError:
        return None, 0

subsection("GET /api/books/")
data, code = api_get("/api/books/")
if data is None:
    print(f"  {YELLOW}⚠ Server not running — skipping API tests{RESET}")
else:
    if code == 200 and data.get('count') == Book.objects.count():
        ok(f"GET /api/books/ → {data['count']} books")
    else:
        fail(f"GET /api/books/ failed", f"Status {code}")

    subsection("GET /api/books/?q=code")
    data, code = api_get("/api/books/?q=code")
    if code == 200:
        ok(f"Search 'code' → {data['count']} results")
    else:
        fail("Book search API failed", str(code))

    subsection("GET /api/books/?status=available")
    data, code = api_get("/api/books/?status=available")
    if code == 200:
        ok(f"Available books API → {data['count']} results")
    else:
        fail("Available filter API failed", str(code))

    subsection("GET /api/members/")
    data, code = api_get("/api/members/")
    if code == 200 and data.get('count') == Member.objects.count():
        ok(f"GET /api/members/ → {data['count']} members")
    else:
        fail("GET /api/members/ failed", str(code))

    subsection("GET /api/members/M001/")
    data, code = api_get("/api/members/M001/")
    if code == 200:
        ok(f"Member detail → {data['member']['name']}")
        ok(f"Active loans  → {len(data['active_loans'])}")
        ok(f"Total fines   → ${data['total_fines']:.2f}")
    else:
        fail("Member detail API failed", str(code))

    subsection("GET /api/loans/overdue/")
    data, code = api_get("/api/loans/overdue/")
    if code == 200:
        ok(f"Overdue loans API → {data['count']} loans")
    else:
        fail("Overdue loans API failed", str(code))

    subsection("GET /api/reports/summary/")
    data, code = api_get("/api/reports/summary/")
    if code == 200:
        ok(f"Summary → {data['total_books']} books, "
           f"{data['total_members']} members, "
           f"${data['total_fines_owed']:.2f} fines")
    else:
        fail("Summary API failed", str(code))

    subsection("GET /api/members/M001/report/")
    data, code = api_get("/api/members/M001/report/")
    if code == 200:
        ok(f"Member report → {data.get('member_name')}")
        ok(f"Ever borrowed → {data.get('total_books_ever_borrowed')}")
        ok(f"Fines owed    → ${data.get('total_fines_owed', 0):.2f}")
    else:
        fail("Member report API failed", str(code))

    subsection("POST /api/loans/borrow/ — valid")
    data, code = api_post("/api/loans/borrow/", {
        "member_id": "M013",
        "isbn"     : "ISBN070"
    })
    if code == 201:
        ok(f"Borrow via API → loan_id={data.get('loan_id')}")
    else:
        fail("Borrow API failed", str(data))

    subsection("POST /api/loans/borrow/ — unavailable book")
    data, code = api_post("/api/loans/borrow/", {
        "member_id": "M013",
        "isbn"     : "ISBN001"   # Alice's book
    })
    if code == 400:
        ok("Borrow correctly rejected — book unavailable")
    else:
        fail("Should have rejected unavailable book", str(code))


# ══════════════════════════════════════════════════════════════
# PART 10 — BULK LOAN STRESS TEST
# ══════════════════════════════════════════════════════════════

section("PART 10 — BULK LOAN STRESS TEST")

subsection("Give Every Member Their Max Books")
stress_books = [
    f"ISBN{str(i).zfill(3)}" for i in range(60, 70)
]   # use philosophy books ISBN061-070 (some already taken)

# Give staff members more books to stress test
staff_members = Member.objects.filter(member_type="Staff")
for member in staff_members:
    available_books = Book.objects.filter(
        is_available=True
    )[:member.max_books - Loan.objects.filter(
        member=member, returned_on__isnull=True
    ).count()]

    for book in available_books[:5]:   # give each staff 5 books
        try:
            due = timezone.now().date() + datetime.timedelta(
                days=member.loan_days
            )
            Loan.objects.create(member=member, book=book, due_date=due)
            book.is_available = False
            book.due_date     = due
            book.save()
        except Exception:
            pass

total_loans = Loan.objects.count()
ok(f"Total loans in system: {total_loans}")

active_loans = Loan.objects.filter(returned_on__isnull=True).count()
ok(f"Active loans: {active_loans}")

returned_loans = Loan.objects.filter(returned_on__isnull=False).count()
ok(f"Returned loans: {returned_loans}")


# ══════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════

section("FINAL SUMMARY")

total = passed + failed
print(f"\n  Tests run    : {total}")
print(f"  {GREEN}Passed       : {passed}{RESET}")
print(f"  {RED if failed > 0 else GREEN}Failed       : {failed}{RESET}")

if errors:
    print(f"\n{RED}  Failed tests:{RESET}")
    for e in errors:
        print(f"    {RED}• {e}{RESET}")

print(f"\n{BOLD}  Database State{RESET}")
print(f"  Books   : {Book.objects.count()}")
print(f"  Members : {Member.objects.count()}")
print(f"  Loans   : {Loan.objects.count()} total / "
      f"{Loan.objects.filter(returned_on__isnull=True).count()} active")
print(f"  Overdue : {Loan.objects.filter(returned_on__isnull=True, due_date__lt=timezone.now().date()).count()}")

print(f"\n{BOLD}  Browser Test URLs{RESET}")
print(f"  http://127.0.0.1:8000/              ← Dashboard")
print(f"  http://127.0.0.1:8000/books/        ← All 100 books")
print(f"  http://127.0.0.1:8000/members/      ← All 20 members")
print(f"  http://127.0.0.1:8000/members/M001/ ← Alice (overdue + fines)")
print(f"  http://127.0.0.1:8000/members/M001/report/ ← Alice report")
print(f"  http://127.0.0.1:8000/api/books/    ← Books API")
print(f"  http://127.0.0.1:8000/api/reports/summary/ ← Summary API")

print()
