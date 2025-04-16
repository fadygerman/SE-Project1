import os
from decimal import Decimal

import requests
import zeep

_currency_converter_client_instance = None

# singleton pattern
def get_currency_converter_client_instance():
    global _currency_converter_client_instance
    if _currency_converter_client_instance is None:
        _currency_converter_client_instance = CurrencyConverterClient()
    return _currency_converter_client_instance

class CurrencyConverterClient:
    def __init__(self):
        self.jwt_token = get_jwt_token()
        self.client = get_currency_converter_client(self.jwt_token)
        
    def get_available_currencies(self) -> list:
        return self.client.service.getAvailableCurrencies()

    def convert(self, from_currency: str, to_currency: str, amount: Decimal) -> Decimal:
        price_in_cent = int(amount * 100)
        converted_price_in_cent = self.client.service.convert(from_currency, to_currency, price_in_cent)
        return (Decimal(converted_price_in_cent) / Decimal('100')).quantize(Decimal('0.00'))
    
    def get_currency_rate(self, from_currency: str, to_currency: str) -> Decimal:
        currency_rate_in_cent = self.client.service.convert(from_currency, to_currency, 100)
        return (Decimal(currency_rate_in_cent) / Decimal('100')).quantize(Decimal('0.00'))

def get_jwt_token() -> str:
        client_id = os.getenv("AUTH0_CURRENCY_CONVERTER_CLIENT_ID")
        client_secret = os.getenv("AUTH0_CURRENCY_CONVERTER_CLIENT_SECRET")

        response = requests.post(
            'https://dev-nrarsg0w7pf50t7d.us.auth0.com/oauth/token',
            json= {
                "client_id": client_id,
                "client_secret": client_secret,
                "audience": "https://dev-nrarsg0w7pf50t7d.us.auth0.com/api/v2/",
                "grant_type": "client_credentials"
            },
            headers={'content-type': 'application/json'}
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get JWT token: {response.json()}")

        return response.json()['access_token']
    
    
def get_currency_converter_client(jwt_token: str) -> zeep.Client:

    # jwt_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Inh1OVo4UC0zMzBKMG9NOVV1V1MzQiJ9.eyJpc3MiOiJodHRwczovL2Rldi1ucmFyc2cwdzdwZjUwdDdkLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJ0T3JBOVlzWjJ3aWwySlRxNjM3YTczbjRoY0lQd1c4REBjbGllbnRzIiwiYXVkIjoiaHR0cHM6Ly9kZXYtbnJhcnNnMHc3cGY1MHQ3ZC51cy5hdXRoMC5jb20vYXBpL3YyLyIsImlhdCI6MTc0Mzg2ODU5OSwiZXhwIjoxNzQzOTU0OTk5LCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJhenAiOiJ0T3JBOVlzWjJ3aWwySlRxNjM3YTczbjRoY0lQd1c4RCJ9.KsXmFhfHlh5UOiZvaKRL57SwuJ8W9qR_NFFEENYsL1iN0xs5vwzABUphfdBZ-rFAcnHjk7vhkIWv74i9iQASvJQmxvpuEZH3tttem_ew-qBGhM-we6_V1x3SM9CSuUUIZg7TOZQNh0gWoC1IWpqdvWWrMinzi-QGBDZPVkKuPTpoJ8HerRym7CO60DFcmCCuiyNtxJWt3TdwyKdUuYOfEnhVjRh0A0vYNcl7Z9vuAhRFgLdNGuB0sgO7HiPPD3D0cp7Q3B5TSvioLOHArd_oW5MlIdKUp_TYCGU9eJ0KRPVfAqlggZYvpNltPuOrRxLTuW01EY7gRqzr57V8Cvh2pA'
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {jwt_token}'})

    transport = zeep.Transport(session=session)
    try:
        return zeep.Client('http://localhost:8080/ws/currencies.wsdl', transport=transport)
    except Exception as e:
        raise ConnectionError(f"Error connecting to currency converter service: {e}")
