/* tslint:disable */
/* eslint-disable */
/**
 * Car Rental API
 * Backend API for Car Rental Application
 *
 * The version of the OpenAPI document: 0.1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


/**
 * 
 * @export
 */
export const Currency = {
    Usd: 'USD',
    Jpy: 'JPY',
    Bgn: 'BGN',
    Czk: 'CZK',
    Dkk: 'DKK',
    Gbp: 'GBP',
    Huf: 'HUF',
    Pln: 'PLN',
    Ron: 'RON',
    Sek: 'SEK',
    Chf: 'CHF',
    Isk: 'ISK',
    Nok: 'NOK',
    Try: 'TRY',
    Aud: 'AUD',
    Brl: 'BRL',
    Cad: 'CAD',
    Cny: 'CNY',
    Hkd: 'HKD',
    Idr: 'IDR',
    Ils: 'ILS',
    Inr: 'INR',
    Krw: 'KRW',
    Mxn: 'MXN',
    Myr: 'MYR',
    Nzd: 'NZD',
    Php: 'PHP',
    Sgd: 'SGD',
    Thb: 'THB',
    Zar: 'ZAR',
    Eur: 'EUR'
} as const;
export type Currency = typeof Currency[keyof typeof Currency];


export function instanceOfCurrency(value: any): boolean {
    for (const key in Currency) {
        if (Object.prototype.hasOwnProperty.call(Currency, key)) {
            if (Currency[key as keyof typeof Currency] === value) {
                return true;
            }
        }
    }
    return false;
}

export function CurrencyFromJSON(json: any): Currency {
    return CurrencyFromJSONTyped(json, false);
}

export function CurrencyFromJSONTyped(json: any, ignoreDiscriminator: boolean): Currency {
    return json as Currency;
}

export function CurrencyToJSON(value?: Currency | null): any {
    return value as any;
}

export function CurrencyToJSONTyped(value: any, ignoreDiscriminator: boolean): Currency {
    return value as Currency;
}

