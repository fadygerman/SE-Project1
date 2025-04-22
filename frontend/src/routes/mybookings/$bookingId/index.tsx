import {createFileRoute, Link} from '@tanstack/react-router';
import { useBookingIdQuery } from "@/api/bookings";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

export const Route = createFileRoute('/mybookings/$bookingId/')({
    component: RouteComponent,
});

function RouteComponent() {
    const { bookingId } = Route.useParams();
    const { data: booking, error, isLoading } = useBookingIdQuery(Number(bookingId));

    if (isLoading) {
        return <div>Loading booking details...</div>;
    }

    if (error) {
        return <div>Error loading booking: {error.message}</div>;
    }

    if (!booking) {
        return <div>No booking found.</div>;
    }

    return (
        <div className="container mx-auto p-4">
            <header className="mb-6">
                <h1 className="text-3xl font-bold">Booking Details</h1>
            </header>
            <Card className="shadow-md">
                <CardHeader>
                    <CardTitle>Booking ID: {booking.id}</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="mt-6">
                        <h2 className="text-2xl font-bold">Details</h2>
                        <Separator className="my-4" />
                        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                            <div>
                                <dt className="text-sm font-medium text-muted-foreground">User ID</dt>
                                <dd className="text-lg">{booking.user?.email}</dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-muted-foreground">Car ID</dt>
                                <Link to={"/cars/$carId"} params={{ carId: booking.carId }} >
                                    <dd className="text-lg">{booking.car.name}</dd>
                                </Link>
                            </div>
                            <div>
                            <dt className="text-sm font-medium text-muted-foreground">Start Date</dt>
                                <dd className="text-lg">{new Date(booking.startDate).toLocaleString()}</dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-muted-foreground">End Date</dt>
                                <dd className="text-lg">{new Date(booking.endDate).toLocaleString()}</dd>
                            </div>
                            {booking.pickupDate && (
                                <div>
                                    <dt className="text-sm font-medium text-muted-foreground">Pickup Date</dt>
                                    <dd className="text-lg">{booking.pickupDate}</dd>
                                </div>
                            )}
                            {booking.returnDate && (
                                <div>
                                    <dt className="text-sm font-medium text-muted-foreground">Return Date</dt>
                                    <dd className="text-lg">{booking.returnDate}</dd>
                                </div>
                            )}
                            <div>
                                <dt className="text-sm font-medium text-muted-foreground">Total Cost</dt>
                                <dd className="text-lg">${booking.totalCost}</dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-muted-foreground">Status</dt>
                                <dd className="text-lg">{booking.status}</dd>
                            </div>
                        </dl>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}