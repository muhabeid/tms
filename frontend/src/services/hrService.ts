import api from './api';
import { Employee, EmployeeDocument, Certification, EmployeeCountByType } from '../types/hr';

export const hrService = {
    getEmployees: async (params?: { employee_type?: string; status?: string; branch?: string; department?: string; search?: string }) => {
        const response = await api.get<Employee[]>('/hr/employees', { params });
        return response.data;
    },

    getEmployee: async (id: number) => {
        const response = await api.get<Employee>(`/hr/employees/${id}`);
        return response.data;
    },

    createEmployee: async (data: Omit<Employee, 'id'>) => {
        const response = await api.post<Employee>('/hr/employees', data);
        return response.data;
    },

    updateEmployee: async (id: number, data: Partial<Omit<Employee, 'id'>>) => {
        const response = await api.put<Employee>(`/hr/employees/${id}`, data);
        return response.data;
    },

    getDocuments: async (employeeId?: number) => {
        const response = await api.get<EmployeeDocument[]>('/hr/documents', {
            params: employeeId ? { employee_id: employeeId } : undefined
        });
        return response.data;
    },

    updateDocument: async (id: number, data: Partial<EmployeeDocument>) => {
        const response = await api.put<EmployeeDocument>(`/hr/documents/${id}`, data);
        return response.data;
    },

    deleteDocument: async (id: number) => {
        const response = await api.delete(`/hr/documents/${id}`);
        return response.data;
    },

    getCertifications: async (employeeId?: number) => {
        const response = await api.get<Certification[]>('/hr/certifications', {
            params: employeeId ? { employee_id: employeeId } : undefined
        });
        return response.data;
    },

    uploadDocument: async (payload: { employee_id: number; document_type: string; document_name: string; file?: File; issue_date?: string; expiry_date?: string; tag?: string; is_sensitive?: boolean; notes?: string }) => {
        if (payload.file) {
            const form = new FormData();
            Object.entries(payload).forEach(([k, v]) => {
                if (v !== undefined && k !== 'file') form.append(k, String(v));
            });
            form.append('file', payload.file);
            const response = await api.post<EmployeeDocument>('/hr/documents/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } });
            return response.data;
        } else {
            const { file, ...data } = payload;
            const response = await api.post<EmployeeDocument>('/hr/documents', data);
            return response.data;
        }
    },

    getExpiringDocuments: async (days = 30) => {
        const response = await api.get<EmployeeDocument[]>('/hr/analytics/expiring-documents', {
            params: { days }
        });
        return response.data;
    },

    getExpiringCertifications: async (days = 30) => {
        const response = await api.get<Certification[]>('/hr/analytics/expiring-certifications', {
            params: { days }
        });
        return response.data;
    },

    getEmployeeCountByType: async () => {
        const response = await api.get<EmployeeCountByType[]>('/hr/analytics/employee-count-by-type');
        return response.data;
    },

    getExpiringContracts: async (days = 60) => {
        const response = await api.get<Employee[]>('/hr/analytics/expiring-contracts', { params: { days } });
        return response.data;
    },

    getUpcomingProbationCompletions: async (days = 30) => {
        const response = await api.get<Employee[]>('/hr/analytics/upcoming-probation-completions', { params: { days } });
        return response.data;
    },

    getEmployeeHistory: async (employeeId: number) => {
        const response = await api.get(`/hr/employees/${employeeId}/history`);
        return response.data;
    },

    getHolidays: async (params?: { year?: number; branch?: string; country?: string }) => {
        const response = await api.get<{ year: number; country: string; branch?: string; dates: string[] }>(
            '/hr/calendar/holidays',
            { params }
        );
        return response.data;
    }
};
