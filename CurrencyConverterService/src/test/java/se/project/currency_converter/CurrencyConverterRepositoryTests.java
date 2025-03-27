package se.project.currency_converter;


import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;

public class CurrencyConverterRepositoryTests {

    CurrencyConverterRepository repo;

    @BeforeEach
    void setUp() {
        repo = new CurrencyConverterRepository();
    }

    @Test
    void testGetAvailableCurrencies() {
        var availableCurrencies = repo.getAvailableCurrencies();
        assertFalse(availableCurrencies.getTime().isEmpty());
    }
}
