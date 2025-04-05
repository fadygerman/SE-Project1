import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/mybookings/')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/mybookings/"!</div>
}
