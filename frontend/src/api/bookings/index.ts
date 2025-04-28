// frontend/src/api/bookings/index.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {Booking, BookingCreate, BookingStatus, BookingUpdate} from "@/openapi";
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
            bookingApi.getMyBookingsApiV1BookingsMyGet().then((response) => {
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
            void queryClient.invalidateQueries({ queryKey: ['bookings'] }); // Fixed: proper object syntax
        },
    });
};

// Optional: Add a hook for paginated access if you want to use pagination in the UI later
export const usePaginatedBookingsQuery = (page = 1, pageSize = 10) => {
    return useQuery({
        queryKey: ['bookings', 'paginated', page, pageSize],
        queryFn: async () =>
            await bookingApi.getMyBookingsApiV1BookingsMyGet().then((response) => {
                // Return the full response with pagination info
                return response as PaginatedResponse<Booking>;
            }),
    });
};

export function usePickUpBookingMutation(bookingId: number, carId: number) {
    const qc = useQueryClient();
    return useMutation<Booking, Error, void>({
        mutationFn: async () => {
            const { body } = await bookingApi.updateBookingApiV1BookingsBookingIdPut({
                bookingId,
                bookingUpdate: { status: BookingStatus.Active }
            });
            return body;
        },
        onSuccess: () => {
            void qc.invalidateQueries({ queryKey: ['booking', bookingId] });
            void qc.invalidateQueries({ queryKey: ['bookings'] });
            void qc.invalidateQueries({ queryKey: ['car', carId] });
            void qc.invalidateQueries({ queryKey: ['cars'] });
        },
    });
}

export function useCompleteBookingWithWindow(booking: Booking) {
    const qc = useQueryClient()

    return useMutation<Booking, Error, void>({
        mutationFn: () => {
            const ret    = new Date()
            const payload: BookingUpdate = {
                returnDate: ret,
                status:     BookingStatus.Completed,
            }
            return bookingApi.updateBookingApiV1BookingsBookingIdPut({
                bookingId:     booking.id,
                bookingUpdate: payload,
            })
        },
        onSuccess: () => {
            void qc.invalidateQueries({ queryKey: ['booking', booking.id] })
            void qc.invalidateQueries({ queryKey: ['bookings'] })
            void qc.invalidateQueries({ queryKey: ['car', booking.carId] })
            void qc.invalidateQueries({ queryKey: ['cars'] })
        },
    })
}


/**
 * Mark a booking as canceled (CANCELED)
 */
export const useCancelBookingMutation = (bookingId: number, carId: number) => {
    const qc = useQueryClient();

    return useMutation<Booking, Error, void>({
        mutationFn: async () => {
            const payload: BookingUpdate = {
                status: BookingStatus.Canceled,
            };
            return bookingApi.updateBookingApiV1BookingsBookingIdPut({
                bookingId,
                bookingUpdate: payload,
            });
        },
        onSuccess: () => {
            void qc.invalidateQueries({ queryKey: ['bookings'] });
            void qc.invalidateQueries({ queryKey: ['booking', bookingId] });
            void qc.invalidateQueries({ queryKey: ['cars'] });
            void qc.invalidateQueries({ queryKey: ['car', carId] });
        },
    });
};
