package se.project.currency_converter;

import https.www_w3schools.ConvertRequest;
import https.www_w3schools.ConvertResponse;
import https.www_w3schools.GetAvailableCurrenciesRequest;
import https.www_w3schools.GetAvailableCurrenciesResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import se.project.currency_converter.exceptions.CurrencyNotFound;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class CurrencyConverterControllerTests {

    private CurrencyConverterController controller;

    @Mock
    private CurrencyConverterService service;

    @BeforeEach
    void setUp() {
        service = mock(CurrencyConverterService.class);
        controller = new CurrencyConverterController(service);
    }

    @Test
    @DisplayName("All available currencies are returned")
    void testGetAvailableCurrencies() {
        var listOfCurrencies = List.of("USD", "EUR", "PLN");
        when(service.getAvailableCurrencies()).thenReturn(listOfCurrencies);
        GetAvailableCurrenciesRequest request = new GetAvailableCurrenciesRequest();
        GetAvailableCurrenciesResponse response = controller.getAvailableCurrencies(request);
        assertEquals(listOfCurrencies, response.getCurrencies());
    }

    @Test
    @DisplayName("Conversion is correct")
    void testConvert() {
        var fromCurrency = "USD";
        var toCurrency = "EUR";
        var amount = 10000L;
        var convertedAmount = 9000L;

        when(service.convert(fromCurrency, toCurrency, amount)).thenReturn(convertedAmount);

        ConvertRequest request = new ConvertRequest();
        request.setFromCurrency(fromCurrency);
        request.setToCurrency(toCurrency);
        request.setAmount(amount);

        ConvertResponse response = controller.convert(request);

        assertEquals(convertedAmount, response.getConvertedAmount());
    }

    @Test
    @DisplayName("Incorrect currency triggers CurrencyNotFound")
    void testConvert_withUnknownCurrency() {
        ConvertRequest request = new ConvertRequest();
        request.setFromCurrency("A");
        request.setToCurrency("EUR");
        request.setAmount(100L);

        when(service.convert("A", "EUR", 100L))
            .thenThrow(new CurrencyNotFound("A"));

        try {
            controller.convert(request);
        } catch (CurrencyNotFound ex) {
            assertEquals("Conversion to currency A is not available!", ex.getMessage());
        }
    }



}
