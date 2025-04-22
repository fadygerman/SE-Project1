import {BookingsApi, CarsApi, Configuration} from "@/openapi";
import {fetchAuthSession} from "@aws-amplify/auth";

async function makeConfig(): Promise<Configuration> {
    const session = await fetchAuthSession();
    const jwt = session.tokens?.idToken?.toString();
    console.log(session.tokens)
    console.log(jwt)
    if (!jwt) {
        throw new Error("No ID token found in session.");
    }

    return new Configuration({
        basePath: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
        accessToken: jwt,
    });
}

export const carsApi = await (async () => new CarsApi(await makeConfig()))();
export const bookingApi = await (async () => new BookingsApi(await makeConfig()))();