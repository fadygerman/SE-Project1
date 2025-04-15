import ProtectedRoute from '@/auth/ProtectedRoute'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/mybookings/')({
  component: RouteComponent,
})

function RouteComponent() {
  // This is the main page for the /mybookings route
  return (<ProtectedRoute>
        <div>Hello "/mybookings/"!</div>
    </ProtectedRoute>)
}

