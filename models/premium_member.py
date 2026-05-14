# models/premium_member.py

from models.member import Member
import datetime

class PremiumMember(Member):
    MAX_BOOKS = 8
    LOAN_PERIOD_DAYS = 21
    FINE_PER_DAY = 0.25     # Half the standard fine rate

    def __init__(self, name, member_id, email, subscription_tier):
        super().__init__(name, member_id, email)
        self.subscription_tier = subscription_tier          # 'Gold' or 'Platinum'
        self.subscription_start = datetime.datetime.now()

    def get_member_type(self):
        return f"Premium ({self.subscription_tier})"

    def subscription_expiry(self):
        return self.subscription_start + datetime.timedelta(days=30)

    def __str__(self):
        parent_str = super().__str__()
        expiry = self.subscription_expiry().strftime('%d %b %Y')
        return f"{parent_str}\nTier   : {self.subscription_tier} | Renews: {expiry}"