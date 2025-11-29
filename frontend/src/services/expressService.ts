import api from './api';
import { Bus, Route, Booking } from '../types/express';

export const expressService = {
    getBuses: async () => {
        const response = await api.get<Bus[]>('/express/buses');
        return response.data;
    },

    getRoutes: async () => {
        const response = await api.get<Route[]>('/express/routes');
        return response.data;
    },

    getBookings: async () => {
        const response = await api.get<Booking[]>('/express/bookings');
        return response.data;
    },

    createBus: async (data: Omit<Bus, 'id'>) => {
        const response = await api.post<Bus>('/express/buses', data);
        return response.data;
    },

    createRoute: async (data: Omit<Route, 'id'>) => {
        const response = await api.post<Route>('/express/routes', data);
        return response.data;
    },

    createBooking: async (data: Omit<Booking, 'id' | 'booking_date'>) => {
        const response = await api.post<Booking>('/express/bookings', data);
        return response.data;
    }
};
