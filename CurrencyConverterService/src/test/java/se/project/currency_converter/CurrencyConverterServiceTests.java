package se.project.currency_converter;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertTrue;

public class CurrencyConverterServiceTests {

    private CurrencyConverterService service;

    @BeforeEach
    void setUp() {
        CurrencyConverterRepository repository = new CurrencyConverterRepository();
        service = new CurrencyConverterService(repository);
    }

    @Test
    void testGetAvailableCurrencies() {
        var availableCurrencies = service.getAvailableCurrencies();
        assertTrue(availableCurrencies.contains("USD"));
    }
}
