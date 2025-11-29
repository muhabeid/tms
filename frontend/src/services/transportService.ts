import api from './api';
import { Truck, DeliveryNote, Trip } from '../types/transport';

export const transportService = {
    getTrucks: async () => {
        const response = await api.get<Truck[]>('/transport/trucks');
        return response.data;
    },

    getDeliveries: async () => {
        const response = await api.get<DeliveryNote[]>('/transport/deliveries');
        return response.data;
    },

    getTrips: async () => {
        const response = await api.get<Trip[]>('/transport/trips');
        return response.data;
    },

    createTruck: async (data: Omit<Truck, 'id'>) => {
        const response = await api.post<Truck>('/transport/trucks', data);
        return response.data;
    },

    createDelivery: async (data: Omit<DeliveryNote, 'id' | 'delivery_number' | 'created_date' | 'status'>) => {
        const response = await api.post<DeliveryNote>('/transport/deliveries', data);
        return response.data;
    }
};
