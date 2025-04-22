// src/clientApi.ts
import {
    AuthApi,
    CarsApi,
    BookingsApi,
    Configuration,
    type UserRegister,
    type HTTPValidationError,
} from '@/openapi';
import { fetchAuthSession } from '@aws-amplify/auth';

/* ──────────────────────────────────────────────────────────
 *  makeConfig – builds an OpenAPI Configuration
 * ────────────────────────────────────────────────────────── */
async function makeConfig(useIdToken = false): Promise<Configuration> {
    const session = await fetchAuthSession();

    const raw = useIdToken
        ? session.tokens?.idToken?.toString()
        : session.tokens?.accessToken?.toString();

    if (!raw) {
        throw new Error(
            `No ${useIdToken ? 'ID' : 'access'} token found. Is the user signed in?`
        );
    }

    return new Configuration({
        basePath: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
        accessToken: () => raw, // generator expects a function
    });
}

/* ──────────────────────────────────────────────────────────
 *  registerCurrentUser – calls /auth/register‑cognito‑user
 *  exactly once, using the ID token’s richer claims
 * ────────────────────────────────────────────────────────── */
async function registerCurrentUser(): Promise<void> {
    const session = await fetchAuthSession();
    const claims = session.tokens?.idToken?.payload as any;

    const payload: UserRegister = {
        firstName: claims.given_name ?? 'Unknown',
        lastName: claims.family_name ?? 'User',
        email: claims.email ?? `no-email-${claims.sub}@example.com`,
        phoneNumber: (claims.phone_number ?? '0000000000').replace(/\s+/g, ''),
        cognitoId: claims.sub,
    };

    const authApi = new AuthApi(await makeConfig(true)); // uses ID token

    try {
        await authApi.registerCognitoUserApiV1AuthRegisterCognitoUserPost({
            userRegister: payload,
        });
        console.info('[registerCurrentUser] ✔ user registered/updated');
    } catch (e: any) {
        // If something is still wrong, log FastAPI’s validation detail
        const detail: HTTPValidationError | undefined = e?.body;
        console.error('[registerCurrentUser] 422 detail:', detail);
        // swallow the error so the app keeps running
    }
}

/* ──────────────────────────────────────────────────────────
 *  Run the registration once, then export the normal APIs
 *  (which use Access‑Token configs)
 * ────────────────────────────────────────────────────────── */
await registerCurrentUser();

export const carsApi = await (async () => new CarsApi(await makeConfig()))();
export const bookingApi = await (async () => new BookingsApi(await makeConfig()))();
