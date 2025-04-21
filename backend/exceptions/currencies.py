class InvalidCurrencyException(Exception):
    def __init__(self, currency_code: str):
        self.currency_code = currency_code
        self.message = f"Invalid currency code: {currency_code}"
        super().__init__(self.message)

class CurrencyServiceUnavailableException(Exception):
    def __init__(self, error_details: str = ""):
        self.error_details = error_details
        self.message = f"Currency service is unavailable: {error_details}" if error_details else "Currency service is unavailable"
        super().__init__(self.message) 