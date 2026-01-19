# VIOLATION

class PaymentGateway:
    def pay(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("amount must be >= 0")

class VipGateway(PaymentGateway):
    def pay(self, amount: float) -> None:
        # VIOLATION: siết chặt hơn base
        if amount < 10:
            raise ValueError("VIP requires amount >= 10")
        
# REFACTOR

class PaymentGateway:

    def __init__(self, min_amount: float = 0.0):
        self.min_amount = min_amount

    def min_amount(self) -> float: 
        return self.min_amount

    def pay(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("amount must be >= 0")
        if amount < self.min_amount:
            raise ValueError(f"amount must be >= {self.min_amount}")

class VipGateway(PaymentGateway):

    def __init__(self):
        super().__init__(10)
