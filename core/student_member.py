from core.member import Member

class StudentMember(Member):
    MAX_BOOKS = 3
    LOAN_PERIOD_DAYS = 14
    FINE_PER_DAY = 0.50
    
    def __init__(self, name, member_id, email, student_number, course):
        super().__init__(name, member_id, email)
        self.student_number = student_number
        self.course = course
        
    def get_member_type(self):
        return "Student"
    
    def __str__(self):
        parent_str = super().__str__()
        return f"{parent_str} \nCourse: {self.course} | Student Number: {self.student_number}"
    

    