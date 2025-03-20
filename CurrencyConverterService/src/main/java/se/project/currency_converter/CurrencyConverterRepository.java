package se.project.currency_converter;

import com.fasterxml.jackson.dataformat.xml.XmlMapper;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.ArrayList;
import java.util.List;

@Component
public class CurrencyConverterRepository {

    private final RestClient restClient = RestClient.create();

    public CurrencyConverterRepository() {}

    public ExchangeRatesXML.Cube getAvailableCurrencies() {
        byte[] xml = restClient.get()
                .uri("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml")
                .retrieve()
                .body(byte[].class);

        ExchangeRatesXML exchangeRates;
        try {
            exchangeRates = new XmlMapper().readValue(xml, ExchangeRatesXML.class);
        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException(e);
        }

        return exchangeRates.getCubeWrapper().getCube();
    }
}
