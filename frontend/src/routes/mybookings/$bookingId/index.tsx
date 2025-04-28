import {createFileRoute, Link} from '@tanstack/react-router';
import {
    useBookingIdQuery,
    useCancelBookingMutation,
    useCompleteBookingWithWindow, usePickUpBookingMutation,
    useReturnBookingMutation
} from "@/api/bookings";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import MapComponent from '@/components/maps/MapComponent';

export const Route = createFileRoute('/mybookings/$bookingId/')({
    component: RouteComponent,
});

function RouteComponent() {
    const { bookingId } = Route.useParams();
    const { data: booking, error, isLoading } = useBookingIdQuery(Number(bookingId));
    const formatDate = (date: Date) => {
        return date.toISOString().split('T')[0]; // formats to 'YYYY-MM-DD'
    };

    const returnBooking = useCompleteBookingWithWindow(booking!);
    const cancelBooking = useCancelBookingMutation(
        Number(bookingId),
        booking?.carId ?? 0
    );
    const pickUpBooking       = usePickUpBookingMutation(
        (bookingId),
        booking?.carId ?? 0
    )


    const isFinalized =
        booking?.status === 'COMPLETED' || booking?.status === 'CANCELED';

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
        <div style={{ width: "100%" }} className="min-h-screen">
        <div className="container mx-auto p-4">
            <header className="mb-6">
                <h1 className="text-3xl font-bold">Booking Details</h1>
            </header>
            <Card className="shadow-md mb" >
                <CardHeader>
                    <CardTitle>Booking ID: {booking.id}</CardTitle>
                </CardHeader>
                <Separator  />
                <CardContent >
                    <div className="mt-6">
             
                        <h2 className="text-2xl font-bold mt-4">Booking</h2>
                        <Separator className="my-4" />
                        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                      
                            <div>
                            <dt className="text-sm font-medium text-muted-foreground">Start Date</dt>
                                <dd className="text-lg">{formatDate(booking.startDate)}</dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-muted-foreground">End Date</dt>
                                <dd className="text-lg">{formatDate(booking.endDate)}</dd>
                            </div>
                            {booking.pickupDate && (
                                <div>
                                    <dt className="text-sm font-medium text-muted-foreground">Pickup Date</dt>
                                    <dd className="text-lg">{formatDate(booking.pickupDate).toLocaleString()}</dd>
                                </div>
                            )}
                            {booking.returnDate && (
                                <div>
                                    <dt className="text-sm font-medium text-muted-foreground">Return Date</dt>
                                    <dd className="text-lg">{formatDate(booking.returnDate).toLocaleString()}</dd>
                                </div>
                            )}
                            <div>
                                <dt className="text-sm font-medium text-muted-foreground">Planned Pick Up Time</dt>
                                <dd className="text-lg">{booking.plannedPickupTime}</dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-muted-foreground">Car</dt>
                                <dd className="text-lg">{booking.car?.name} {booking.car?.model}</dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-muted-foreground">Total Cost</dt>
                                <dd className="text-lg">{booking.totalCost} {booking.currencyCode}</dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-muted-foreground">Status</dt>
                                <dd className="text-lg">{booking.status}</dd>
                            </div>
                        </dl>
                        
                        
                        <h2 className="text-2xl font-bold mt-8">User</h2>
                        <Separator className="my-4" />
                        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                            <div>
                                <dt className="text-sm font-medium text-muted-foreground">Name</dt>
                                <dd className="text-lg">{booking.user?.firstName}</dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-muted-foreground">Family Name</dt>
                                
                                <dd className="text-lg">{booking.user?.lastName}</dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-muted-foreground"></dt>
                                <dd className="text-lg"></dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-muted-foreground">E-Mail</dt>
                                <dd className="text-lg">{booking.user?.email}</dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-muted-foreground">Phone Number </dt>
                                <dd className="text-lg">{booking.user?.phoneNumber}</dd>
                            </div>
                        </dl>
                        <h2 className="text-2xl font-bold mt-8">Car</h2>
                        <Separator className="my-4" />
                        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-[1fr_2fr]">
                            <div style={{ maxHeight: '200px',minHeight: '150px', width: '100%', backgroundColor:"white", borderRadius:"10px", marginLeft:"auto ", marginRight:"auto"}} className="flex items-center justify-center">  
                                <img
                                src={`/assets/car_images/car-${booking.car?.id}.jpg`}
                                alt={booking.car?.name}
                                className="h-full w-auto object-contain"
                                style={{ objectFit: "cover", borderRadius: "10px" }}
                                />
                            </div>
                            <div>
                                <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                                    <div>
                                        <dt className="text-sm font-medium text-muted-foreground">Name</dt>
                                        <dd className="text-lg">{booking.car?.name}</dd>
                                    </div>
                                    <div>
                                        <Link to={"/cars/$carId"} params={{ carId: booking.carId.toString() }} >
                                            <dt className="text-sm font-medium text-muted-foreground">Model</dt>
                                            <dd className="text-lg">{booking.car?.model}</dd>
                                        </Link>
                                    </div>
                                    <div>
                                    <dt className="text-sm font-medium text-muted-foreground">Price Per Day</dt>
                                        <dd className="text-lg">{booking.car?.pricePerDay} {booking.currencyCode}</dd>
                                    </div>

                                </dl>
                            </div>
                           
                        </dl>

                    </div>
                </CardContent>
            </Card>

            {!isFinalized && (
                <div className="flex space-x-4 mt-6">
                    {booking.status === 'PLANNED' && (
                        <>
                            <button
                                onClick={() => pickUpBooking.mutate(undefined, {
                                    onSuccess: () => {
                                        window.location.reload();
                                    },
                                })}
                                disabled={pickUpBooking.isLoading}
                                className="btn btn-primary"
                            >
                                {pickUpBooking.isLoading ? 'Picking up…' : 'Pick Up Car'}
                            </button>
                            <button
                                onClick={() => cancelBooking.mutate()}
                                disabled={cancelBooking.isLoading}
                                className="btn btn-warning"
                            >
                                {cancelBooking.isLoading ? 'Canceling…' : 'Cancel Booking'}
                            </button>
                        </>
                    )}

                    {/* Once ACTIVE, only allow return */}
                    {booking.status === 'ACTIVE' && (
                        <button
                            onClick={() => returnBooking.mutate()}
                            disabled={returnBooking.isLoading}
                            className="btn btn-primary"
                        >
                            {returnBooking.isLoading ? 'Returning…' : 'Return Car'}
                        </button>
                    )}
                </div>
            )}
            
            
                {booking.car && (
                    <Card className='mt-5 shadow-md'>
                        <CardHeader>
                            <CardTitle>Car Location: {booking.car?.longitude}, {booking.car?.latitude}</CardTitle>
                        </CardHeader>
                        <MapComponent center={{ lat: booking.car.latitude ?? 0, lng: booking.car.longitude ?? 0}} car={booking.car} />
                    </Card>
                )}
            
        </div>
    </div>
    );
}