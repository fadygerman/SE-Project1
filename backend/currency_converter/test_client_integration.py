import os
from decimal import Decimal

import dotenv
import pytest
import zeep.exceptions

from currency_converter.client import CurrencyConverterClient, get_currency_converter_client, get_jwt_token
from exceptions.currencies import CurrencyServiceUnavailableException


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()

@pytest.fixture(scope="session")
def check_credentials():
    if not (os.getenv("AUTH0_CURRENCY_CONVERTER_CLIENT_ID") and 
            os.getenv("AUTH0_CURRENCY_CONVERTER_CLIENT_SECRET")):
        pytest.skip("AUTH0 credentials not set in environment variables")

@pytest.fixture(scope="session")
def jwt_token(check_credentials):
    return get_jwt_token()

@pytest.fixture(scope="session")
def client(jwt_token):
    return get_currency_converter_client(jwt_token)

@pytest.fixture(scope="session")
def currency_converter_client_fake_token():
    return get_currency_converter_client("fake-token")

@pytest.fixture(scope="session")
def currency_converter_client():
    return CurrencyConverterClient()

def test_get_jwt_token_integration(check_credentials):
    """Integration test for get_jwt_token function.
    This test will use the real AUTH0 API to get a JWT token.
    """
    token = get_jwt_token()
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0
    
    parts = token.split('.')
    assert len(parts) == 3

def test_get_jwt_token_integration_fake_token():
    """Integration test for get_jwt_token function.
    This test will use the real AUTH0 API to get a JWT token.
    """
    
    with pytest.raises(CurrencyServiceUnavailableException):
        client = get_currency_converter_client("fake-token")
    

def test_prepare_currency_converter_client_integration(jwt_token):
    """
    ATTENTION: Currency converter must be running
    """
    
    client = get_currency_converter_client(jwt_token)
    assert client is not None
    assert hasattr(client.service, 'convert')
    assert hasattr(client.service, 'getAvailableCurrencies')

def test_integration_convert_currency(client):
    """Integration test for currency conversion using the SOAP service.
    This test will perform a real currency conversion.
    ATTENTION: Currency converter must be running
    """
    result = client.service.convert('USD', 'EUR', 100)
    
    assert result is not None
    assert isinstance(result, int)
    assert result > 0, "Conversion result should be positive"

def test_integration_convert_currency_wrong_currency_name(client):
    
    wrong_currency_name = 'WRO'
    try:
        client.service.convert(wrong_currency_name, 'EUR', Decimal("100.00"))
        pytest.fail("Expected exception was not raised")
    except zeep.exceptions.Fault as e:
        if hasattr(e, 'message'):
            print(f"Exception message attribute: {e.message}")
        if hasattr(e, 'code'):
            print(f"Exception code: {e.code}")
            
        assert wrong_currency_name in str(e)
        assert "not available" in str(e).lower()

def test_integration_get_available_currencies(client):
    """Integration test for getting available currencies using the SOAP service.
    ATTENTION: Currency converter must be running
    """
    currencies = client.service.getAvailableCurrencies()
    
    assert currencies is not None
    assert isinstance(currencies, list)
    assert len(currencies) > 0, "Should return at least one currency"
    
    common_currencies = ['USD', 'EUR', 'GBP', 'JPY']
    for currency in common_currencies:
        assert currency in currencies, f"{currency} should be in the list of available currencies"

def test_currency_converter_client_get_available_currencies(currency_converter_client):
    available_currencies = currency_converter_client.get_available_currencies()
    assert available_currencies is not None
    
def test_currency_convert_client_convert(currency_converter_client):
    result = currency_converter_client.convert('USD', 'EUR', Decimal("100.00"))
    assert result is not None
    assert isinstance(result, Decimal)
    assert result > 0

def test_currency_converter_client_get_currency_rate(currency_converter_client):
    result = currency_converter_client.get_currency_rate('USD', 'EUR')
    assert result is not None
    assert isinstance(result, Decimal)
    assert result > 0