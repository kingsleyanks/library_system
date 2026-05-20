# models/staff_member.py

from core.member import Member

class StaffMember(Member):
    MAX_BOOKS = 10
    LOAN_PERIOD_DAYS = 30
    FINE_PER_DAY = 0.00     # No fines for staff

    def __init__(self, name, member_id, email, department, staff_number):
        super().__init__(name, member_id, email)
        self.department = department
        self.staff_number = staff_number

    def get_member_type(self):
        return "Staff"

    # Override fine methods entirely — staff have no fines
    def _calculate_fine_for_book(self, book):
        return 0    # Always zero regardless of overdue status

    def get_total_fines(self):
        return 0

    def get_fine_breakdown(self):
        return ["  Staff members are exempt from fines."]

    def pay_fine(self, amount):
        return "Staff members have no fines."

    def __str__(self):
        parent_str = super().__str__()
        return f"{parent_str}\nDept   : {self.department} | Staff No: {self.staff_number}"