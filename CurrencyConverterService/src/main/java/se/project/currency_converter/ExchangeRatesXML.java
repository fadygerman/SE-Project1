package se.project.currency_converter;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;

import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
class ExchangeRatesXML {

    @JsonProperty("Cube")
    private CubeWrapper cubeWrapper;

    public CubeWrapper getCubeWrapper() {
        return cubeWrapper;
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    static class CubeWrapper {
        @JsonProperty("Cube")
        private Cube cube;

        public Cube getCube() {
            return cube;
        }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Cube {
        @JsonProperty("time")
        private String time;

        @JsonProperty("Cube")
        @JacksonXmlElementWrapper(useWrapping = false)
        private List<CurrencyRate> rates;

        public String getTime() {
            return time;
        }

        public List<CurrencyRate> getRates() {
            return rates;
        }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class CurrencyRate {
        @JsonProperty("currency")
        private String currency;

        @JsonProperty("rate")
        private double rate;

        public String getCurrency() {
            return currency;
        }

        public double getRate() {
            return rate;
        }
    }
}
