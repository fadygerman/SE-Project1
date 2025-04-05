import { Breadcrumb, BreadcrumbList, BreadcrumbItem, BreadcrumbPage, BreadcrumbLink, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import { Button } from '@/components/ui/button'
import { Calendar } from '@/components/ui/calendar'
import { Card, CardHeader, CardContent, CardTitle, CardFooter, CardDescription } from '@/components/ui/card'
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from '@/components/ui/carousel'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils'
import { createFileRoute, Link } from '@tanstack/react-router'
import { format } from 'date-fns'
import { CalendarIcon, Car, IdCardIcon } from 'lucide-react'
import { useState } from 'react'
import { cars } from '..'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

export const Route = createFileRoute('/cars/$carId/')({
  component: RouteComponent,
})

function RouteComponent() {
  const { carId } = Route.useParams()
  const [dateRange, setDateRange] = useState<{
    from?: Date
    to?: Date
  }>({})
  const [isBooking, setIsBooking] = useState(false)
  const handleBooking = async () => {
    if (!dateRange.from || !dateRange.to) {
      alert("Please select a date range")
      return
    }
    setIsBooking(true)
    // Simulate booking process
    setTimeout(() => {
      alert(`Car booked from ${dateRange.from ? format(dateRange.from, "PPP") : "N/A"} to ${dateRange.to ? format(dateRange.to, "PPP") : "N/A"}`)
      setIsBooking(false)
    }, 2000)

  }
  const car = cars.find((car) => car.id === carId)

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
              <BreadcrumbPage>{carId}</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
        <h1 className="mt-4 text-3xl font-bold">cars</h1>
      </header>
      <div className="grid gap-6 md:grid-cols-2">
        <div>
          <div className="overflow-hidden justify-center items-center flex rounded-lg ">
            {/* {car.image ? (
              <img src={car.image || "/placeholder.svg"} alt={car.name} className="h-64 w-full object-cover md:h-96" />
            ) : (
              <div className="flex h-64 items-center justify-center md:h-96">
                <Car className="h-24 w-24 text-muted-foreground" />
              </div>
            )} */}
            <Carousel className="w-full w-2/3 ">
              <CarouselContent>
                {car?.images.map((img, index) => (
                  <CarouselItem key={index}>
                    <div className="p-1">
                      <Card>
                        <CardContent className="flex aspect-square items-center justify-center p-6">
                          <img src={img} alt="" />
                        </CardContent>
                      </Card>
                    </div>
                  </CarouselItem>
                ))}
              </CarouselContent>
              <CarouselPrevious />
              <CarouselNext />
            </Carousel>

          </div>

          <div className="mt-6">
            <h2 className="text-2xl font-bold">Car Details</h2>
            <Separator className="my-4" />
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-muted-foreground">Model</dt>
                <dd className="text-lg">carmodel</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-muted-foreground">Price</dt>
                <dd className="text-lg font-bold flex items-center gap-2">
                  carprice
                  <Select defaultValue='USD' onValueChange={(value) => console.log(value)}>
                    <SelectTrigger className="w-32">
                      <SelectValue placeholder="Currency" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="USD">USD</SelectItem>
                      <SelectItem value="EUR">EUR</SelectItem>
                      <SelectItem value="ALL">Lek</SelectItem>
                      <SelectItem value="JPY">Yen</SelectItem>
                      <SelectItem value="MXN">Pesos</SelectItem>
                    </SelectContent>
                  </Select>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-muted-foreground">Year</dt>
                <dd className="text-lg">{"caryear"}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-muted-foreground">Color</dt>
                <dd className="text-lg">{"carcolor"}</dd>
              </div>
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
            <h2 className="text-2xl font-bold">Description</h2>
            <Separator className="my-4" />
            {/* <p className="text-muted-foreground">{car.description || "No description available for this vehicle."}</p> */}
          </div>
        </div>
      </div>
    </div>
  )
}
