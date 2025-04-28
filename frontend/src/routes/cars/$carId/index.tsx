import { Breadcrumb, BreadcrumbList, BreadcrumbItem, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import { Button } from '@/components/ui/button'
import { Calendar } from '@/components/ui/calendar'
import { Card, CardHeader, CardContent, CardTitle, CardFooter, CardDescription } from '@/components/ui/card'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils'
import { createFileRoute, Link, useNavigate } from '@tanstack/react-router'
import { format } from 'date-fns'
import { CalendarIcon } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useCarIdQuery } from "@/api/cars";
import { useCreateBookingMutation } from "@/api/bookings";
import { Currency } from "@/openapi/models/Currency";
import MapComponent from '@/components/maps/MapComponent'
import { CurrencySelector } from '@/components/ui/currencySelector'
import { Car } from '@/openapi/models/Car'
import { useCurrency } from '@/components/currency/CurrencyWrapper'

export const Route = createFileRoute('/cars/$carId/')({
  component: RouteComponent,
})

function RouteComponent() {
  const { carId } = Route.useParams();
  const [dateRange, setDateRange] = useState<{ from?: Date; to?: Date }>({});
  const [pickupTime, setPickupTime] = useState<string>("12:00");
  const [isBooking, setIsBooking] = useState(false);
  const { selectedCurrency,setSelectedCurrency} = useCurrency();
  const { data: carDetail, isLoading} = useCarIdQuery(Number(carId), selectedCurrency); // Use selectedCurrency directly
  const navigate = useNavigate();

  const [cachedCarDetail, setCachedCarDetail] = useState<Car | undefined>(undefined);
  const [totalCost, setTotalCost] = useState<number>();

  useEffect(() => {
    if (carDetail) {
      setCachedCarDetail(carDetail);
    }

    if (activeCarDetail && dateRange.from && dateRange.to) {
      const days = getDateDifferenceInDays(dateRange.from, dateRange.to);
      const calculatedTotal = days * Number(activeCarDetail.pricePerDay);
      setTotalCost(calculatedTotal);
    } else {
      setTotalCost(undefined);
    }
  }, [carDetail,dateRange.from, dateRange.to]);
  const activeCarDetail = carDetail || cachedCarDetail;



  
  const addBooking = useCreateBookingMutation();

  const handleBooking = async () => {
    if (!dateRange.from || !dateRange.to) {
      alert("Please select a date range");
      return;
    }
    setIsBooking(true);

    addBooking.mutate({
      carId: Number(carId),
      startDate: formatDateForApi(dateRange.from!),
      endDate: formatDateForApi(dateRange.to!),
      plannedPickupTime: pickupTime,
      currencyCode: selectedCurrency as Currency,
    }, {
      onSuccess: () => {
        alert(
          `Car booked from ${format(dateRange.from!, "PPP")} to ${format(dateRange.to!, "PPP")}`
        );        
        setIsBooking(false);
        navigate({ to: "/mybookings" }); // Redirect to cars page after booking
      },
      onError: () => {
        alert("Booking failed. Please try again.");
        setIsBooking(false);
      },
    });
  };
  if (activeCarDetail== undefined && isLoading) {
    return (
      <div style={{margin:"auto"}} >
        <p>Loading car...</p>
      </div>
    );
  }

  if (activeCarDetail== undefined && !isLoading) {
    return (
      <div style={{margin:"auto"}}>
        <p>Error loading car details.</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <header className="mb-6">
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <Link to="/cars">Cars</Link>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>{activeCarDetail.name} {activeCarDetail.model}</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
        <h1 className="mt-4 text-3xl font-bold">{activeCarDetail.name} {activeCarDetail.model}</h1>
      </header>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Left side */}
        <div>
          <Card>
            <div className="overflow-hidden justify-center items-center flex rounded-lg">
              <div style={{ maxHeight: "400px", minHeight: "400px", width: "100%", backgroundColor: "white", borderRadius: "10px" }} className="flex items-center justify-center">
                <img
                  src={`/assets/car_images/car-${activeCarDetail.id}.jpg`}
                  alt={activeCarDetail.name}
                  className="h-full w-auto object-contain"
                  style={{ height: "100%", width: "100%", objectFit: "cover" }}
                />
              </div>
            </div>
          </Card>

          <div className="mt-6">
            <h2 className="text-2xl font-bold">Car Details</h2>
            <Separator className="my-4" />

            <dl className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-muted-foreground">Model</dt>
                <dd className="text-lg">{activeCarDetail.model}</dd>
              </div>

              <div>
                <dt className="text-sm font-medium text-muted-foreground">Price</dt>
                <dd className="text-lg font-bold flex items-center gap-2">
                  {activeCarDetail.pricePerDay}
                  <CurrencySelector
                    value={selectedCurrency}
                    onCurrencyChange={(value) => {
                      setSelectedCurrency(value);
                    }}
                  />
                </dd>
              </div>

              <div>
                <dt className="text-sm font-medium text-muted-foreground">Availability</dt>
                <dd className="text-lg">{activeCarDetail.isAvailable ? "Available" : "Not Available"}</dd>
              </div>

              {activeCarDetail.latitude != null && activeCarDetail.longitude != null && (
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Location</dt>
                  <dd className="text-lg">
                    {activeCarDetail.latitude.toFixed(4)}, {activeCarDetail.longitude.toFixed(4)}
                  </dd>
                </div>
              )}
            </dl>
          </div>
        </div>

        {/* Right side */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Total Cost {totalCost !== undefined ? `${totalCost} ${selectedCurrency}` : "-"}</CardTitle>
              <CardDescription>Select a date to book this car</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                <div className="grid gap-2">
                  <label className="text-sm font-medium">From Date</label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={cn("w-full justify-start text-left font-normal", !dateRange?.to && "text-muted-foreground")}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {dateRange?.from ? format(dateRange.from, "PPP") : "Select start date"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={dateRange?.from}
                        onSelect={(date) => setDateRange((prev) => ({ ...prev, from: date }))}
                        initialFocus
                        disabled={(date) => date < new Date()}
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                <div className="grid gap-2">
                  <label className="text-sm font-medium">To Date</label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={cn("w-full justify-start text-left font-normal", !dateRange?.to && "text-muted-foreground")}
                        disabled={!dateRange?.from}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {dateRange?.to ? format(dateRange.to, "PPP") : "Select end date"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={dateRange?.to}
                        onSelect={(date) => setDateRange((prev) => ({ ...prev, to: date }))}
                        initialFocus
                        disabled={(date) => date < new Date() || (dateRange?.from ? date < dateRange.from : false)}
                        
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                <div className="grid gap-2">
                  <label className="text-sm font-medium">Pickup Time</label>
                  <Select
                    defaultValue="12:00"
                    onValueChange={(value) => setPickupTime(value)}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select pickup time" />
                    </SelectTrigger>
                    <SelectContent>
                      {Array.from({ length: 13 }, (_, i) => 8 + i).map(hour => {
                        const formattedHour = hour.toString().padStart(2, '0');
                        return (
                          <SelectItem key={hour} value={`${formattedHour}:00`}>
                            {formattedHour}:00
                          </SelectItem>
                        );
                      })}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>

            <CardFooter>
              <Button
                className="w-full"
                onClick={handleBooking}
                disabled={!dateRange.from || !dateRange.to || isBooking}
              >
                {isBooking ? "Booking..." : "Book Now"}
              </Button>
            </CardFooter>
          </Card>

          <div className="mt-6">
            <h2 className="text-2xl font-bold">Location</h2>
            <Separator className="my-4" />
            {activeCarDetail.latitude != null && activeCarDetail.longitude != null && (
              <div style={{ width: "100%" }}>
                <MapComponent center={{ lat: activeCarDetail.latitude, lng: activeCarDetail.longitude }} car={activeCarDetail} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Helper
function formatDateForApi(date: Date): Date {
  const year = date.getFullYear();
  const month = date.getMonth();
  const day = date.getDate();
  return new Date(year, month, day, 12, 0, 0);
}

function getDateDifferenceInDays(startDate: Date, endDate: Date): number {
  const timeDiff = endDate.getTime() - startDate.getTime();
  return Math.ceil(timeDiff / (1000 * 3600 * 24));
}
