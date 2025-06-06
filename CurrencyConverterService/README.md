# Currency Converter Web Service

## Overview
SOAP/WSDL Web Service for currency conversion powered by Java/Spring. Retrieves exchange rates from the European Central Bank (ECB) and exposes endpoints for the Car Rental application to convert prices between currencies.

## Features
- SOAP/WSDL-style web service architecture
- Automated daily exchange rate updates from ECB
- Cross-rates calculation between any supported currencies
- Integration with Car Rental Backend

## Planned Features
- Token-based authentication for API access
- Caching for improved performance

## Technologies
- Java 17+
- Spring Boot 3.x
- Spring WS (Web Services)
- Maven/Gradle build system
- Docker containerization

## Setup Instructions
1. Clone repository

There are three ways to run the application:
- [IntelliJ configuration](#intellij-configuration)
- [maven + java 21](#maven--java-21)
- [Docker](#docker)

### IntelliJ configuration
If you want to run the application from IntelliJ IDEA, you need to configure the following:

1. `mvn jaxb2:xjc` - Generate Java classes from XML schema
2. Find `./target/generated-sources/xjc/` directory and mark it as auto generated source
   - Right-click on the `jaxb` directory -> `Mark Directory as -> Generated Sources Root`

### maven + java 21
2. Build with Maven:
```
mvn clean install
```
3. Run the application:
```
java -jar target/currency-converter-service-0.0.1-SNAPSHOT.jar
```

### Docker
```
docker compose up
```

## How to use?
- WSDL available at `http://localhost:8080/ws/currencies.wsdl`

### Example Python client
- using [`zeep`](https://docs.python-zeep.org/en/master/)

```python
import zeep

client = zeep.Client('http://localhost:8080/ws/currencies.wsdl')

available_currencies = client.service.getAvailableCurrencies()
print(available_currencies)

converted_currency = client.service.convert('USD', 'EUR', 100)
print(converted_currency)
```

## Project Structure
```
CurrencyConverterService/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/carrentalapp/currency_converter/ # Java source code
│   │   └── resources/
│   │       ├── currencies.xsd/            # XML Schema definitions
│   │       └── application.yml # Configuration
│   └── test/
│       └── java/              # Unit tests
├── pom.xml                    # Maven dependencies
├── Dockerfile
├── docker-compose.yaml
└── README.md
```

## API Operations
- `convert(amount, sourceCurrency, targetCurrency)` - Convert an amount between currencies
- `getSupportedCurrencies()` - List all available currencies

## Integration with ECB
The service retrieves daily exchange rates from the European Central Bank using the following URL:
```
https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml
```

## Integration with Car Rental Backend
The Currency Converter Service is used by the Car Rental Backend to:
1. Convert car prices from USD to user's preferred currency
2. Calculate booking costs in multiple currencies
3. Provide up-to-date exchange rate information

## Testing
```
mvn test
```

## License
TBD
