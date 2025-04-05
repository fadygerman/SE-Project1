import os

import zeep
import requests
import dotenv

def get_jwt_token() -> str:
    dotenv.load_dotenv()
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
