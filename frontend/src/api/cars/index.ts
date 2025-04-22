// frontend/src/hooks/useCarsQuery.ts
import {useQuery} from '@tanstack/react-query';
import {carsApi} from "@/apiClient/client.ts";
import {Car} from "@/openapi";


// Create the fetch function for the GET /api/v1/cars/ endpoint


// Custom hook using useQuery for fetching cars
export const useCarsQuery = () => {
    return useQuery({
        queryKey: ['cars'],
        queryFn: async () =>
            await carsApi.getCarsApiV1CarsGet().then((response) => {
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