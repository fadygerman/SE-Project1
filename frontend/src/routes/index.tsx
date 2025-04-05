import { createFileRoute, redirect } from '@tanstack/react-router'

export const Route = createFileRoute('/')({
    component: () => null,
  
    beforeLoad: () => {
        return redirect({ to: '/cars' })
    
      },
  })