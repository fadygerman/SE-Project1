// frontend/src/api/bookings/index.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Booking, BookingCreate, BookingUpdate } from "@/openapi";
import {bookingApi} from "@/apiClient/client.ts";

// Fetch all bookings
export const useBookingsQuery = () => {
    return useQuery({
        queryKey: ['bookings'],
        queryFn: () =>
            bookingApi.getBookingsApiV1BookingsGet().then((response) => {
                return response;
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
            queryClient.invalidateQueries(['bookings']); // Refetch bookings after creation
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
            queryClient.invalidateQueries(['bookings']); // Refetch bookings after update
        },
    });
};