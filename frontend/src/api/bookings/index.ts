// frontend/src/api/bookings/index.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Booking, BookingCreate, BookingUpdate } from "@/openapi";
import {bookingApi} from "@/apiClient/client.ts";

// Define an interface for the paginated response
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// Fetch all bookings
export const useBookingsQuery = () => {
    return useQuery({
        queryKey: ['bookings'],
        queryFn: () =>
            bookingApi.getMyBookingsApiV1BookingsMyGet().then((response: any) => {
                // Check if the response has the new pagination structure
                if (response && response.items) {
                    // Return just the items array to maintain compatibility
                    return response.items;
                }
                alert("No bookings found or invalid response structure.");
            }),
    });
};

// Fetch a single booking by bookingId
export const useBookingIdQuery = (bookingId: number) => {
    return useQuery({
        queryKey: ['booking', bookingId],
        queryFn: () =>
            bookingApi.getBookingApiV1BookingsBookingIdGet({ bookingId }).then((result) => {
                return result;
            }),
        enabled: !!bookingId, // Ensures the query only runs if bookingId is provided
    });
};

// Create a new booking
export const useCreateBookingMutation = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (newBooking: BookingCreate) =>
            bookingApi.createBookingApiV1BookingsPost({ bookingCreate: newBooking }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['bookings'] }); // Fixed: proper object syntax
        },
    });
};

// Update an existing booking
export const useUpdateBookingMutation = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ bookingId, bookingUpdate }: { bookingId: number; bookingUpdate: BookingUpdate }) =>
            bookingApi.updateBookingApiV1BookingsBookingIdPut({ bookingId, bookingUpdate }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['bookings'] }); // Fixed: proper object syntax
        },
    });
};

// Optional: Add a hook for paginated access if you want to use pagination in the UI later
export const usePaginatedBookingsQuery = (page = 1, pageSize = 10) => {
    return useQuery({
        queryKey: ['bookings', 'paginated', page, pageSize],
        queryFn: async () =>
            await bookingApi.getMyBookingsApiV1BookingsMyGet().then((response: any) => {
                // Return the full response with pagination info
                return response as PaginatedResponse<Booking>;
            }),
    });
};