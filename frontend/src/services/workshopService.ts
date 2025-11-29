import api from './api';
import { MaintenanceJob, StoreItem, Supplier } from '../types/workshop';

export const workshopService = {
    getJobs: async () => {
        const response = await api.get<MaintenanceJob[]>('/workshop/jobs');
        return response.data;
    },

    getStoreItems: async () => {
        const response = await api.get<StoreItem[]>('/workshop/store-items');
        return response.data;
    },

    getSuppliers: async () => {
        const response = await api.get<Supplier[]>('/workshop/suppliers');
        return response.data;
    },

    createJob: async (data: Omit<MaintenanceJob, 'id'>) => {
        const response = await api.post<MaintenanceJob>('/workshop/jobs', data);
        return response.data;
    }
};
