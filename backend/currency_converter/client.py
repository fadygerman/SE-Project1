import os

import zeep
import requests
import dotenv

def get_jwt_token() -> str:
    dotenv.load_dotenv()
    client_id = os.getenv("COGNITO_CURRENCY_CONVERTER_CLIENT_ID")
    client_secret = os.getenv("COGNITO_CURRENCY_CONVERTER_CLIENT_SECRET")

    response = requests.post(
        'https://eu-central-1hcdydivfb.auth.eu-central-1.amazoncognito.com/oauth2/token',
        data=f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}&scope=default-m2m-resource-server-ww7zvj/read",
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get JWT token: {response.json()}")

    return response.json()['access_token']

def get_currency_converter_client(jwt_token: str) -> zeep.Client:

    # jwt_token = 'eyJraWQiOiJoODJkaXBpQm9nT0J6UllLNzZuaVFUYXRJcnc3dmlMZlwvTnFoV0JYMDcwVT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIxa3E4N3JpMW03NWFqdWE4c21sc3UwZmc2dCIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiZGVmYXVsdC1tMm0tcmVzb3VyY2Utc2VydmVyLXd3N3p2alwvcmVhZCIsImF1dGhfdGltZSI6MTc0MzI1MTEyNiwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmV1LWNlbnRyYWwtMS5hbWF6b25hd3MuY29tXC9ldS1jZW50cmFsLTFfSGNkWURJVkZCIiwiZXhwIjoxNzQzMjU0NzI2LCJpYXQiOjE3NDMyNTExMjYsInZlcnNpb24iOjIsImp0aSI6IjBhNWIwNzRlLTUzMjYtNDM3ZS1iMWIxLTViN2I1NWMwMTE0MiIsImNsaWVudF9pZCI6IjFrcTg3cmkxbTc1YWp1YThzbWxzdTBmZzZ0In0.mmy_OtR_6WuJCj9JFYQEJnyXxVhntDAceg8tWA8qOLRqEKGdvqWA0Sxmr9GFrT6pMhoy6xnxa6h_DL1lMIc3pxlH_TKfbFcxPnrzrALF94OJsP0hMyKXUd22gphcZawkHWC-Wpsp1AOGUWW_eC1jS79GuLk3z79YVeR8yaUXsyKYSwVUUYTIleMZPbgUaTnu_0oYKEt0enqJaIENCMJVl7eQqfDBxO32i7eKnNImpJ8GH-iLzRhWc_oJ28lklEKrf4SKWv6CezOSYAs69YKEVD929r_LGnsrJnYIghBDtkzpt6Gci99Vock44clTbtOkWMHKllgVIrFjUbHyVVQmCg'
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {jwt_token}'})

    transport = zeep.Transport(session=session)

    return zeep.Client('http://localhost:8080/ws/currencies.wsdl', transport=transport)
