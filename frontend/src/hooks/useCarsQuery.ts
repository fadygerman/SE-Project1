import {useQuery} from '@tanstack/react-query';
import {carsApi} from "@/apiClient/client.ts";
import {Car} from "@/openapi";

// Define an interface for the paginated response
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// Custom hook using useQuery for fetching cars
export const useCarsQuery = () => {
    return useQuery({
        queryKey: ['cars'],
        queryFn: async () =>
            await carsApi.getCarsApiV1CarsGet().then((response: any) => {
                // Check if the response has the new pagination structure
                if (response && response.items) {
                    // Return just the items array to maintain compatibility
                    return response.items;
                }
                // Fall back to the original response format if needed
                return response;
            }),
    });
};

// Custom hook using useQuery for fetching a single car by carId
export const useCarIdQuery = (carId: number) => {
    return useQuery({
        queryKey: ['car', carId],
        queryFn: () =>
            carsApi.getCarApiV1CarsCarIdGet({ carId }).then((result) => {
                return result;
            }),
        enabled: !!carId, // Ensures the query only runs if carId is provided
    }).data as Car;
};

// Optional: Add a hook for paginated access if you want to use pagination in the UI later
export const usePaginatedCarsQuery = (page = 1, pageSize = 10) => {
    return useQuery({
        queryKey: ['cars', 'paginated', page, pageSize],
        queryFn: async () =>
            await carsApi.getCarsApiV1CarsGet().then((response: any) => {
                // Return the full response with pagination info
                return response as PaginatedResponse<Car>;
            }),
    });
};

export * from '@/api/cars/index';