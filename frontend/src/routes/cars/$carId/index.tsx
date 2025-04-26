import { Breadcrumb, BreadcrumbList, BreadcrumbItem, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import { Button } from '@/components/ui/button'
import { Calendar } from '@/components/ui/calendar'
import { Card, CardHeader, CardContent, CardTitle, CardFooter, CardDescription } from '@/components/ui/card'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils'
import { createFileRoute, Link } from '@tanstack/react-router'
import { format } from 'date-fns'
import { CalendarIcon } from 'lucide-react'
import { useState } from 'react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {useCarIdQuery} from "@/api/cars";
import {useCreateBookingMutation} from "@/api/bookings";
import { Currency } from "@/openapi/models/Currency";
import MapComponent from '@/components/maps/MapComponent'

export const Route = createFileRoute('/cars/$carId/')({
  component: RouteComponent,
})

function RouteComponent() {
  const { carId } = Route.useParams()
  const [dateRange, setDateRange] = useState<{
    from?: Date
    to?: Date
  }>({})
  const [pickupTime, setPickupTime] = useState<string>("12:00");
  const [selectedCurrency, setSelectedCurrency] = useState<string>("USD")
  const [isBooking, setIsBooking] = useState(false)
  
  const handleBooking = async () => {
    if (!dateRange.from || !dateRange.to) {
      alert("Please select a date range")
      return
    }
    setIsBooking(true)
    setTimeout(() => {
      alert(`Car booked from ${dateRange.from ? format(dateRange.from, "PPP") : "N/A"} to ${dateRange.to ? format(dateRange.to, "PPP") : "N/A"}`)
      setIsBooking(false)
    }, 2000)
    addBooking.mutate({
        carId: Number(carId),
        startDate: formatDateForApi(dateRange.from!),
        endDate: formatDateForApi(dateRange.to!),
        plannedPickupTime: pickupTime,
        currencyCode: selectedCurrency as Currency,
        })
  }
  console.log(carId)
  const carDetail = useCarIdQuery(Number(carId));
  const addBooking = useCreateBookingMutation();

  if (!carDetail) {
    return <div className="container mx-auto p-4">Loading car details...</div>;
  }

  const currencyCodes = Object.values(Currency);

  return (
    <div className="container mx-auto p-4">
      <header className="mb-6">
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <Link to='/cars'>Cars</Link>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>{carDetail.name} {carDetail.model}</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
        <h1 className="mt-4 text-3xl font-bold">{carDetail.name} {carDetail.model}</h1>
      </header>
      <div className="grid gap-6 md:grid-cols-2">
        <div>
          <div className="overflow-hidden justify-center items-center flex rounded-lg">
            <div style={{ maxHeight: "400px"}}>
            <img
              src={`/assets/car_images/car-${carDetail.id}.jpg`}
              alt={carDetail.name}
              className="h-full w-auto object-contain"
            />
            </div>
          </div>
            <div className="mt-6">
              <h2 className="text-2xl font-bold">Car Details</h2>
              <Separator className="my-4" />
              <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Model</dt>
                  <dd className="text-lg">{carDetail.model}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Price</dt>
                  <dd className="text-lg font-bold flex items-center gap-2">
                    {carDetail.pricePerDay}
                    <Select 
                      defaultValue="USD" 
                      onValueChange={(value) => setSelectedCurrency(value)}
                    >
                      <SelectTrigger className="w-32">
                        <SelectValue placeholder="Currency" />
                      </SelectTrigger>
                      <SelectContent>
                        {/* Dynamically generate SelectItems from the Currency enum */}
                        {currencyCodes.map(code => (
                          <SelectItem key={code} value={code}>
                            {code} - {getCurrencyDisplayName(code)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </dd>
                </div>
                <div>
                <dt className="text-sm font-medium text-muted-foreground">Availability</dt>
                <dd className="text-lg">{carDetail.isAvailable ? "Available" : "Not Available"}</dd>
                </div>
                {carDetail.latitude && carDetail.longitude && (
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">Location</dt>
                    <dd className="text-lg">
                      {carDetail.latitude.toFixed(4)}, {carDetail.longitude.toFixed(4)}
                    </dd>
                  </div>
                )}
              </dl>
            </div>
          </div>

        <div>
          <Card>
            <CardHeader>
              <CardTitle>Book this car</CardTitle>
              <CardDescription>Select a date to book this car</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                <div className="grid gap-4">
                  <div className="grid gap-2">
                    <label className="text-sm font-medium">From Date</label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className={cn(
                            "w-full justify-start text-left font-normal",
                            !dateRange?.to && "text-muted-foreground",
                          )}
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
                          className={cn(
                            "w-full justify-start text-left font-normal",
                            !dateRange?.to && "text-muted-foreground",
                          )}
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
                          )
                        })}
                      </SelectContent>
                    </Select>
                  </div>
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
            {carDetail.latitude != null && carDetail.longitude != null && (
              <div style={{width:"100%"}}><MapComponent center={{ lat: carDetail.latitude, lng: carDetail.longitude }}></MapComponent></div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// Helper function to get a nice display name for each currency
function getCurrencyDisplayName(currency: string): string {
  const displayNames: Record<string, string> = {
    'USD': 'US Dollar',
    'EUR': 'Euro',
    'GBP': 'British Pound',
    'JPY': 'Japanese Yen',
    'CAD': 'Canadian Dollar',
    'AUD': 'Australian Dollar',
    'CHF': 'Swiss Franc',
    'CNY': 'Chinese Yuan',
    'MXN': 'Mexican Peso',
    'INR': 'Indian Rupee',
    'BRL': 'Brazilian Real',
    'ZAR': 'South African Rand',
  };
  
  return displayNames[currency] || currency;
}

function formatDateForApi(date: Date): Date {
  // Create a new Date object set to midnight in local timezone, which will maintain
  // the correct date when serialized to ISO format
  const year = date.getFullYear();
  const month = date.getMonth(); // Keep 0-indexed for Date constructor
  const day = date.getDate();
  
  // Create a new date at 12:00 noon to avoid any timezone boundary issues
  return new Date(year, month, day, 12, 0, 0);
}
