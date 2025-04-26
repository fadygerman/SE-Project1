import { createFileRoute, Link } from '@tanstack/react-router'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card" // Removed unused CardHeader
import { Breadcrumb, BreadcrumbItem, BreadcrumbList, BreadcrumbPage } from '@/components/ui/breadcrumb' // Removed unused imports
import { useCarsQuery } from "@/api/cars";
import { Car } from "@/openapi";

export const Route = createFileRoute('/cars/')({
  component: RouteComponent,
})

function RouteComponent() {
  const { data: cars, isLoading, error } = useCarsQuery();
  console.log(cars); // For debugging
  
  if (isLoading) {
    return <div>Loading cars...</div>;
  }

  if (error) {
      return <div>Error loading cars: {(error as Error).message}</div>;
  }

  if (!cars || !cars.length) {
      return <div>No cars available</div>;
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
        <h1 className="mt-4 text-3xl font-bold">Available Cars</h1>
      </header>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
        {cars.filter((car: Car) => car.isAvailable) // Filter cars based on availability
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
              <p className="mt-1">Price: {car.pricePerDay} per day</p>
              <p className="mt-1">Status: {car.isAvailable ? "Available" : "Not Available"}</p>
            </CardContent>
            <CardFooter>
              <Link to={`/cars/$carId`} params={{ carId: car.id.toString() }} className="text-blue-500 hover:underline">
                View Details
              </Link>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}