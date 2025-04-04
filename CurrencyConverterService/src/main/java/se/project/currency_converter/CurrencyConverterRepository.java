package se.project.currency_converter;

import com.fasterxml.jackson.dataformat.xml.XmlMapper;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
public class CurrencyConverterRepository {

    // TODO: Inject RestClient, it will allow to do proper unit testing (by injecting a mock)
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
            // TODO: Throw custom exception
            e.printStackTrace();
            throw new RuntimeException(e);
        }

        ExchangeRatesXML.Cube cube = exchangeRates.getCubeWrapper().getCube();

        cube.getRates().add(new ExchangeRatesXML.CurrencyRate("EUR", 1.0));

        return cube;
    }
}
