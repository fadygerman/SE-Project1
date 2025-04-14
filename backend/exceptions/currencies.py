class InvalidCurrencyException(Exception):
    def __init__(self, currency_code: str):
        self.currency_code = currency_code
        self.message = f"Invalid currency code: {currency_code}"
        super().__init__(self.message) 