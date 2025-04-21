package se.project.currency_converter;

import org.springframework.stereotype.Service;
import se.project.currency_converter.exceptions.CurrencyNotFound;

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

    public long convert(String fromCurrency, String toCurrency, long amount) {
        List<ExchangeRatesXML.CurrencyRate> rates = repository.getAvailableCurrencies().getRates();

        var fromRate = rates
                .stream()
                .filter(rate -> rate.getCurrency().equals(fromCurrency))
                .findFirst()
                .orElseThrow(() -> new CurrencyNotFound(fromCurrency))
                .getRate();

        var toRate = rates
                .stream()
                .filter(rate -> rate.getCurrency().equals(toCurrency))
                .findFirst()
                .orElseThrow(() -> new CurrencyNotFound(toCurrency))
                .getRate();

        return (long)((amount / fromRate) * toRate);
    }
}
