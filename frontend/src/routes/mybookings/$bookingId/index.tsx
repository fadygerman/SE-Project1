import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/mybookings/$bookingId/')({
  component: RouteComponent,
})

function RouteComponent() {
    const { bookingId } = Route.useParams()
  return <div>{ bookingId }</div>
}
