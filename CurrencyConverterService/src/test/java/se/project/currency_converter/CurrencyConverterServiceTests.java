package se.project.currency_converter;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class CurrencyConverterServiceTests {

    private CurrencyConverterService service;

    @Mock
    private CurrencyConverterRepository repository;

    private final ExchangeRatesXML.CurrencyRate eurRate = new ExchangeRatesXML.CurrencyRate("EUR", 1.0);
    private final ExchangeRatesXML.CurrencyRate usdRate = new ExchangeRatesXML.CurrencyRate("USD", 1.1);
    private final ExchangeRatesXML.CurrencyRate plnRate = new ExchangeRatesXML.CurrencyRate("PLN", 4.2);

    @BeforeEach
    void setUp() {
        List<ExchangeRatesXML.CurrencyRate> rates = List.of(eurRate, usdRate, plnRate);
        ExchangeRatesXML.Cube cube = new ExchangeRatesXML.Cube("2025-03-20", rates);

        repository = mock(CurrencyConverterRepository.class);
        when(repository.getAvailableCurrencies()).thenReturn(cube);

        service = new CurrencyConverterService(repository);
    }

    @Test
    void testGetAvailableCurrencies() {
        var availableCurrencies = service.getAvailableCurrencies();
        for (ExchangeRatesXML.CurrencyRate rate : List.of(eurRate, usdRate, plnRate)) {
            assertTrue(availableCurrencies.contains(rate.getCurrency()));
        }
    }

    @Test
    @DisplayName("Convert USD to EUR")
    void testConvert() {
        var amount = 10000;
        var fromCurrency = "USD";
        var toCurrency = "EUR";
        var convertedAmount = service.convert(fromCurrency, toCurrency, amount);
        assertEquals(convertedAmount, (long)(amount / usdRate.getRate()));
    }

    @Test
    @DisplayName("Convert PLN to USD")
    void testConvert2() {
        var amount = 10000;
        var fromCurrency = "USD";
        var toCurrency = "PLN";
        var convertedAmount = service.convert(fromCurrency, toCurrency, amount);
        assertEquals(convertedAmount, (long)((amount / usdRate.getRate()) * plnRate.getRate()));
    }
}
