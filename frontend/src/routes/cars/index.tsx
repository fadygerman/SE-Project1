import { createFileRoute, Link } from '@tanstack/react-router'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card" // Adjust the import path based on your project structure
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import {useCarsQuery} from "@/api/cars";
import {carsApi} from "@/apiClient/client.ts";

export const Route = createFileRoute('/cars/')({
  component: RouteComponent,
})

function RouteComponent() {
    const {data: cars, isLoading, error} = useCarsQuery();
    console.log(cars)
    if (!cars)  {
        return <div>No Cars</div>
    }
    if (isLoading)  {
        return <div>Loading ...</div>
    }

    return (
    <div className="container mx-auto p-4">
      <header className="mb-6">
        <Breadcrumb>
          <BreadcrumbList>
            {/* <BreadcrumbItem>
              <BreadcrumbLink href="/dashboard/cars">Cars</BreadcrumbLink>
            </BreadcrumbItem> */}
            {/* <BreadcrumbSeparator /> */}
            <BreadcrumbItem>
              <BreadcrumbPage>Cars</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
        <h1 className="mt-4 text-3xl font-bold">cars</h1>
      </header>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">

        {cars?.map((car) => (
          <Card key={car.id} className="shadow-md">
            <CardHeader>
              <img src={car.image} alt={car.name} className="w-full h-40 object-cover rounded-t-md" />
            </CardHeader>
            <CardContent>
              <CardTitle>{car.name}</CardTitle>
              <p>Model: {car.model}</p>
              <p>Price: {car.price}</p>
            </CardContent>
            <CardFooter>
              <Link to={`/cars/$carId`} params={{ carId: car.id }} className="text-blue-500 hover:underline">
                View Details
              </Link>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  )
}
