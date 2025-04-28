import './index.css'
import { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider, createRouter } from '@tanstack/react-router'

// Import the generated route tree
import { routeTree } from './routeTree.gen'
import AuthWrapper from './auth/AuthWrapper'
import { CurrencyProvider } from './components/currency/CurrencyWrapper'

// Create a new router instance
const router = createRouter({ routeTree })

// Register the router instance for type safety
declare module '@tanstack/react-router' {
    interface Register {
        router: typeof router
    }
}

// Render the app
const rootElement = document.getElementById('root')!
if (!rootElement.innerHTML) {
    const root = ReactDOM.createRoot(rootElement)
    root.render(
        <StrictMode>
            <AuthWrapper user={undefined} signOut={undefined} >
                <CurrencyProvider>
                    <RouterProvider router={router} />
                </CurrencyProvider>
                
            </AuthWrapper>
        </StrictMode>,
    )
}
