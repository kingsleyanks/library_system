# models/librarian_member.py
from models.member import Member

class LibrarianMember(Member):
    LOAN_PERIOD_DAYS = 30
    FINE_PER_DAY = 0.00     # Exempt — but overriding methods makes this explicit

    def __init__(self, name, member_id, email, department, staff_number, access_level):
        if access_level not in (1, 2, 3):
            raise ValueError(f"Access level must be 1, 2, or 3. Got: {access_level}")

        super().__init__(name, member_id, email)
        self.department = department
        self.staff_number = staff_number
        self.access_level = access_level

    # ── Borrowing ──────────────────────────────────────────────

    def check_if_can_borrow(self):
        """Librarians have unlimited borrowing."""
        return True

    # ── Fines ──────────────────────────────────────────────────

    def _calculate_fine_for_book(self, book):
        return 0

    def get_total_fines(self):
        return 0

    def get_fine_breakdown(self):
        return ["  Librarians are exempt from fines."]

    def pay_fine(self, amount):
        return "Librarians have no fines."

    # ── Catalog Management ─────────────────────────────────────

    def can_manage_catalog(self):
        """Level 2 and above can manage the catalog."""
        return self.access_level >= 2

    def can_manage_members(self):
        """Level 3 only can manage member accounts."""
        return self.access_level == 3

    def get_access_description(self):
        """Human-readable description of access rights."""
        descriptions = {
            1: "Read-only — can browse catalog",
            2: "Editor — can add/remove books",
            3: "Admin — full system access"
        }
        return descriptions[self.access_level]

    # ── Identity ───────────────────────────────────────────────

    def get_member_type(self):
        return f"Librarian (Level {self.access_level})"

    def __str__(self):
        parent_str = super().__str__()
        return (
            f"{parent_str}\n"
            f"Dept   : {self.department} | Staff No: {self.staff_number}\n"
            f"Access : Level {self.access_level} — {self.get_access_description()}"
        )