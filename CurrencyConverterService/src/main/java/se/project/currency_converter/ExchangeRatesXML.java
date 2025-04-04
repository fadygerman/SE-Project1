package se.project.currency_converter;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
@Getter
class ExchangeRatesXML {

    @JsonProperty("Cube")
    private CubeWrapper cubeWrapper;

    @JsonIgnoreProperties(ignoreUnknown = true)
    @Getter
    static class CubeWrapper {
        @JsonProperty("Cube")
        private Cube cube;
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    @Getter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Cube {
        @JsonProperty("time")
        private String time;

        @JsonProperty("Cube")
        @JacksonXmlElementWrapper(useWrapping = false)
        private List<CurrencyRate> rates;
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    @Getter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CurrencyRate {
        @JsonProperty("currency")
        private String currency;

        @JsonProperty("rate")
        private double rate;
    }
}
