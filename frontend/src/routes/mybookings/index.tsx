import { createFileRoute, Link } from '@tanstack/react-router';
import { Breadcrumb, BreadcrumbItem, BreadcrumbList, BreadcrumbPage } from "@/components/ui/breadcrumb.tsx";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card.tsx";
import { useBookingsQuery } from "@/api/bookings";

export const Route = createFileRoute('/mybookings/')({
  component: RouteComponent,
});

function RouteComponent() {
  const { data: bookings, error } = useBookingsQuery();

  if (error) {
    return <div>Error loading bookings: {error.message}</div>;
  }

  if (!bookings) {
    return <div>Loading...</div>;
  }

  return (
      <div className="container mx-auto p-4">
        <header className="mb-6">
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbPage>My Bookings</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
          <h1 className="mt-4 text-3xl font-bold">My Bookings</h1>
        </header>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
          {bookings?.map((booking) => (
              <Card key={booking.id} className="shadow-md">
                <CardHeader>
                  <CardTitle>Booking ID: {booking.id}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p><strong>User ID:</strong> {booking.user_id}</p>
                  <p><strong>Car ID:</strong> {booking.car_id}</p>
                  <p><strong>Start Date:</strong> {booking.start_date}</p>
                  <p><strong>End Date:</strong> {booking.end_date}</p>
                  {booking.pickup_date && <p><strong>Pickup Date:</strong> {booking.pickup_date}</p>}
                  {booking.return_date && <p><strong>Return Date:</strong> {booking.return_date}</p>}
                  <p><strong>Total Cost:</strong> ${booking.total_cost}</p>
                  <p><strong>Status:</strong> {booking.status}</p>
                </CardContent>
                <CardFooter>
                  <Link to={`/mybookings/${booking.id}`} className="text-blue-500 hover:underline">
                    View Details
                  </Link>
                </CardFooter>
              </Card>
          ))}
        </div>
      </div>
  );
}