import { createFileRoute, Link } from '@tanstack/react-router'; 
import { Breadcrumb, BreadcrumbItem, BreadcrumbList, BreadcrumbPage } from "@/components/ui/breadcrumb.tsx";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card.tsx";
import { useBookingsQuery } from "@/api/bookings";
import { Booking } from "@/openapi";

export const Route = createFileRoute('/mybookings/')({
  component: RouteComponent,
});



function RouteComponent() {
  const { data: bookings, error } = useBookingsQuery();// For debugging
  
  if (error) {
    return <div>Error loading bookings: {error.message}</div>;
  }

  if (!bookings) {
    return <div>Loading...</div>;
  }

  const formatDate = (date: Date) => {
    return date.toISOString().split('T')[0]; // formats to 'YYYY-MM-DD'
  };
  
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
        {bookings.map((booking: Booking) => ( 
          <Card key={booking.id} className="shadow-md">
            <CardHeader>
              <CardTitle>Booking ID: {booking.id}</CardTitle> {/* ✅ booking.id */}
            </CardHeader>
            <CardContent className="flex flex-col gap-3 text-sm text-muted-foreground">
              <div className="flex justify-between">
                <span className="font-semibold text-primary">Car:</span>
                <span>{booking.car?.name} {booking.car?.model}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-semibold text-primary">Name:</span>
                <span>{booking.user?.firstName} {booking.user?.lastName}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-semibold text-primary">Start Date:</span>
                <span>{formatDate(booking.startDate)}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-semibold text-primary">End Date:</span>
                <span>{formatDate(booking.endDate)}</span>
              </div>
              {booking.pickupDate && (
                <div className="flex justify-between">
                  <span className="font-semibold text-primary">Pickup Date:</span>
                  <span>{formatDate(booking.pickupDate)}</span>
                </div>
              )}
              {booking.returnDate && (
                <div className="flex justify-between">
                  <span className="font-semibold text-primary">Return Date:</span>
                  <span>{formatDate(booking.returnDate)}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="font-semibold text-primary">Total Cost:</span>
                <span>${booking.totalCost}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-semibold text-primary">Status:</span>
                <span>{booking.status}</span>
              </div>
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