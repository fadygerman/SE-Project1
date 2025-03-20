package se.project.currency_converter;

import https.www_w3schools.ConvertRequest;
import https.www_w3schools.ConvertResponse;
import https.www_w3schools.GetAvailableCurrenciesRequest;
import https.www_w3schools.GetAvailableCurrenciesResponse;
import org.springframework.ws.server.endpoint.annotation.Endpoint;
import org.springframework.ws.server.endpoint.annotation.PayloadRoot;
import org.springframework.ws.server.endpoint.annotation.RequestPayload;
import org.springframework.ws.server.endpoint.annotation.ResponsePayload;

@Endpoint
public class CurrencyConverterController {
    private static final String NAMESPACE_URI = "https://www.w3schools.com";

    private final CurrencyConverterService service;

    public CurrencyConverterController(CurrencyConverterService service) {
        this.service = service;
    }

    @PayloadRoot(namespace = NAMESPACE_URI, localPart = "getAvailableCurrenciesRequest")
    @ResponsePayload
    public GetAvailableCurrenciesResponse getAvailableCurrencies(@RequestPayload GetAvailableCurrenciesRequest request) {
        GetAvailableCurrenciesResponse response = new GetAvailableCurrenciesResponse();
        response.getCurrencies().addAll(service.getAvailableCurrencies());
        return response;
    }

    @PayloadRoot(namespace = NAMESPACE_URI, localPart = "convertRequest")
    @ResponsePayload
    public ConvertResponse convert(@RequestPayload ConvertRequest request) {
        long convertedAmount = service.convert(request.getFromCurrency(), request.getToCurrency(), request.getAmount());

        ConvertResponse response = new ConvertResponse();
        response.setConvertedAmount(convertedAmount);
        return response;
    }
}
