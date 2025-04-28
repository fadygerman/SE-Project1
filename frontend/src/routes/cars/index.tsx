import { createFileRoute, Link } from '@tanstack/react-router'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card" // Removed unused CardHeader
import { Breadcrumb, BreadcrumbItem, BreadcrumbList, BreadcrumbPage } from '@/components/ui/breadcrumb' // Removed unused imports
import { useCarsQuery } from "@/api/cars";
import { Car } from "@/openapi";
import { CurrencySelector } from '@/components/ui/currencySelector';
import { useEffect, useState } from 'react';
import { useCurrency } from '@/components/currency/CurrencyWrapper';

export const Route = createFileRoute('/cars/')({
  component: RouteComponent,
})

function RouteComponent() {
  
  const { selectedCurrency,setSelectedCurrency} = useCurrency();
  const [shownCurrency, setShownCurrency] = useState<string>(selectedCurrency);
  const [cachedCarDetails, setCachedCarDetails] = useState<[Car] | undefined>(undefined);
  const { data: cars,  isLoading, } = useCarsQuery(selectedCurrency);
  useEffect(() => {
     if (cars) {
      setCachedCarDetails(cars);
      setShownCurrency(selectedCurrency);
    }
 
   }, [cars]);
  const activeCars = cars || cachedCarDetails;
  
  if (activeCars == undefined) {
    return <div style={{margin:"auto"}}>Loading Cars </div>;
  }

  if (activeCars == undefined && !isLoading) {
    return <div  style={{margin:"auto"}}>Error loading cars. </div>;
  }

  if (!activeCars ||!activeCars.length) {
      return <div  style={{margin:"auto"}}>No cars available</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <header className="mb-6">
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbPage>Cars</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
        <div className="mt-4 flex items-center justify-between mr-4">
          <div>
            <h2 className="text-2xl font-bold">Available Cars</h2>
          </div>
          <div>
          <dt className="text-sm font-medium text-muted-foreground">Currency</dt>
          <CurrencySelector
            value={selectedCurrency}
            onCurrencyChange={(value) => {
              setSelectedCurrency(value);
            }}
          />
          </div>

        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
        {activeCars.filter((car: Car) => car.isAvailable) // Filter cars based on availability
        .map((car: Car) => (
          <Card key={car.id} className="shadow-md">
            <CardContent className="pt-6">
              <CardHeader>
                <div style={{ height: '200px', width: '100%', backgroundColor:"white", borderRadius:"10px"}} className="flex items-center justify-center">
                  <img 
                  src={`/assets/car_images/car-${car.id}.jpg`} 
                  alt={car.name} 
                  className="h-full w-auto object-contain"
                />
                </div>
                
            </CardHeader>
              <CardTitle>{car.name}</CardTitle>
              <p className="mt-2">Model: {car.model}</p>
              <p className="mt-1">Price: {car.pricePerDay} {shownCurrency} per day</p>
              <p className="mt-1">Status: {car.isAvailable ? "Available" : "Not Available"}</p>
            </CardContent>
            <CardFooter>
              <Link to={`/cars/$carId`} params={{ carId: car.id.toString() }} className="text-blue-500 hover:underline">
                Book Now
              </Link>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}