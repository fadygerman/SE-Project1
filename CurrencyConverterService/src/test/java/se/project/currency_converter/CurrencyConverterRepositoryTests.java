package se.project.currency_converter;

import com.fasterxml.jackson.dataformat.xml.XmlMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestClient;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.nio.charset.StandardCharsets;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class CurrencyConverterRepositoryTests {

    private CurrencyConverterRepository repo;

    @Mock
    private RestClient restClient;

    @SuppressWarnings("rawtypes")
    @Mock
    private RestClient.RequestHeadersUriSpec uriSpec;

    @SuppressWarnings("rawtypes")
    @Mock
    private RestClient.RequestHeadersSpec headersSpec;

    @Mock
    private RestClient.ResponseSpec responseSpec;

    @SuppressWarnings("unchecked")
    @BeforeEach
    void setUp() {
        when(restClient.get()).thenReturn(uriSpec);
        when(uriSpec.uri(anyString())).thenReturn(headersSpec);
        when(headersSpec.retrieve()).thenReturn(responseSpec);

        repo = new CurrencyConverterRepository();
        ReflectionTestUtils.setField(repo, "restClient", restClient);
    }

    @Test
    void testGetAvailableCurrencies() throws Exception {
        String mockXml = """
            <gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01" xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref">
              <Cube>
                <Cube time="2024-06-01">
                  <Cube currency="USD" rate="1.2"/>
                </Cube>
              </Cube>
            </gesmes:Envelope>
        """;

        when(responseSpec.body(byte[].class)).thenReturn(mockXml.getBytes(StandardCharsets.UTF_8));

        var cube = repo.getAvailableCurrencies();

        Optional<ExchangeRatesXML.CurrencyRate> eur = cube.getRates().stream()
            .filter(rate -> rate.getCurrency().equals("EUR"))
            .findFirst();

        Optional<ExchangeRatesXML.CurrencyRate> usd = cube.getRates().stream()
            .filter(rate -> rate.getCurrency().equals("USD"))
            .findFirst();

        assertNotNull(cube);
        assertEquals("2024-06-01", cube.getTime());
        assertTrue(eur.isPresent());
        assertEquals(1.0, eur.get().getRate());
        assertTrue(usd.isPresent());
        assertEquals(1.2, usd.get().getRate());
    }


    // Integration Tests:

    // @BeforeEach
    // void setUp() {
    //     repo = new CurrencyConverterRepository();
    // }

    // @Test
    // void testGetAvailableCurrencies() {
    //     var availableCurrencies = repo.getAvailableCurrencies();
    //     assertFalse(availableCurrencies.getTime().isEmpty());
    // }
}
