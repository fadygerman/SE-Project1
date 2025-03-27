package se.project.currency_converter.exceptions;

public class CurrencyNotFound extends RuntimeException {
    public CurrencyNotFound(String message) {
        super(message);
    }
}
