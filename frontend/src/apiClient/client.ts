import {BookingsApi, CarsApi, Configuration, DefaultApi} from "@/openapi";

const config = new Configuration({
    basePath: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
});

export const carsApi = new CarsApi(config);
export const bookingApi = new BookingsApi(config);
export const currencyApi = new CarsApi(config);