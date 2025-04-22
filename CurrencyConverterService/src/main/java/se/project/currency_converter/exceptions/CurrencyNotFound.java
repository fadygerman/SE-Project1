package se.project.currency_converter.exceptions;

import org.springframework.ws.soap.server.endpoint.annotation.FaultCode;
import org.springframework.ws.soap.server.endpoint.annotation.SoapFault;

@SoapFault(faultCode = FaultCode.CLIENT)
public class CurrencyNotFound extends RuntimeException {
    public CurrencyNotFound(String currency) {
        super(String.format("Conversion to currency %s is not available!", currency));
    }
}
