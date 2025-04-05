import { createFileRoute, Link } from '@tanstack/react-router'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card" // Adjust the import path based on your project structure
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb'

export const Route = createFileRoute('/cars/')({
  component: RouteComponent,
})

export const cars = [
  {
    id: "1",
    name: "Tesla Model S",
    price: "$80,000",
    model: "2025",
    // Thumbnail image (e.g. displayed in a list of cars)
    image: "https://i.pinimg.com/736x/5e/62/1b/5e621b67dac9b07531a63e815cf3f0cb.jpg",
    // Carousel images
    images: [
      "https://i.pinimg.com/736x/5e/62/1b/5e621b67dac9b07531a63e815cf3f0cb.jpg",
      "https://i.pinimg.com/736x/49/a8/a8/49a8a8a36efc16fd11638c544cda64e9.jpg",
      "https://i.pinimg.com/736x/e0/96/53/e096535ad6b68bc16ab4a7b0daaea548.jpg",
    ],
  },
  {
    id: "2",
    name: "Ford Mustang",
    price: "$55,000",
    model: "2024",
    image: "https://i.pinimg.com/736x/da/de/ff/dadeffa6c113e136a130ed1467e7bd2c.jpg",
    images: [
      "https://i.pinimg.com/736x/da/de/ff/dadeffa6c113e136a130ed1467e7bd2c.jpg",
      "https://i.pinimg.com/736x/e1/1a/f9/e11af996ab466cd65291d0946ec42939.jpg",
      "https://i.pinimg.com/736x/6d/2b/c0/6d2bc0f9e188046d8db773aabef85871.jpg",
    ],
  },
  {
    id: "3",
    name: "Chevrolet Camaro",
    price: "$50,000",
    model: "2023",
    image: "https://i.pinimg.com/736x/8f/9f/8b/8f9f8b9827a6c94456ff25ea331364de.jpg",
    images: [
      "https://i.pinimg.com/736x/8f/9f/8b/8f9f8b9827a6c94456ff25ea331364de.jpg",
      "https://i.pinimg.com/736x/be/23/5f/be235f5f30651b3a87f4154c539e5baa.jpg",
      "https://i.pinimg.com/736x/2d/e9/04/2de90468cf821fcc13beddf455f7d098.jpg",
    ],
  },
]


function RouteComponent() {
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

        {cars.map((car) => (
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
