package se.project.currency_converter;

import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class CurrencyConverterService {
    private final CurrencyConverterRepository repository;

    public CurrencyConverterService(CurrencyConverterRepository repository) {
        this.repository = repository;
    }

    public List<String> getAvailableCurrencies() {

        return repository.getAvailableCurrencies()
                .getRates()
                .stream()
                .map(ExchangeRatesXML.CurrencyRate::getCurrency)
                .toList();
    }
}
