import { useQuery } from '@tanstack/react-query';
import { carsApi } from "@/apiClient/client.ts";



// Custom hook using useQuery for fetching cars
export const useCarsQuery = (currency_code:string) => {
    return useQuery({
        queryKey: ['cars', currency_code],
        queryFn: async () =>
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            await carsApi.getCarsApiV1CarsGet({currency_code:currency_code}).then((response: any) => {
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
export const useCarIdQuery = (carId: number, currency_code: string) => {
    return useQuery({
      queryKey: ['car', carId, currency_code],
      queryFn: () =>
        carsApi.getCarApiV1CarsCarIdGet({ carId, currency_code }).then((result) => {
          return result;
        }),
      enabled: !!carId, // ✅ This keeps old car detail while fetching the new one
    });
  };