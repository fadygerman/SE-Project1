// src/components/ProtectedRoute.tsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../auth/AuthWrapper';  // Assuming this hook provides authentication context
import { useNavigate } from '@tanstack/react-router';

// @ts-expect-error Amplify is not typed
function ProtectedRoute({children}) {
    const { user } = useAuth();  // Get user from context
    const [loading, setLoading] = useState(true); // Track loading state
    const navigate = useNavigate();

    useEffect(() => {
        // Check if the user is authenticated from context
        if (!user) {
            // If no user is authenticated, redirect to the home/welcome page
            navigate({ to: '/' }); // Corrected navigation logic
        } else {
            setLoading(false); // User is authenticated, proceed with rendering
        }
    }, [navigate, user]);

    // Show loading state while checking authentication
    if (loading) {
        return <div>Loading...</div>;
    }

    // If authenticated, render the protected content
    return <>{children}</>;
};

export default ProtectedRoute;
