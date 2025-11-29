import api from './api';
import { Transaction, Invoice, FinancialSummary, DepartmentSummary } from '../types/finance';

export const financeService = {
    getTransactions: async () => {
        const response = await api.get<Transaction[]>('/finance/transactions');
        return response.data;
    },

    getInvoices: async () => {
        const response = await api.get<Invoice[]>('/finance/invoices');
        return response.data;
    },

    getSummary: async () => {
        const response = await api.get<FinancialSummary>('/finance/analytics/summary');
        return response.data;
    },

    getRevenueByCategory: async () => {
        const response = await api.get<{ category: string; total: number }[]>('/finance/analytics/revenue-by-category');
        return response.data;
    },

    getExpenseByCategory: async () => {
        const response = await api.get<{ category: string; total: number }[]>('/finance/analytics/expense-by-category');
        return response.data;
    },

    getByDepartment: async () => {
        const response = await api.get<DepartmentSummary[]>('/finance/analytics/by-department');
        return response.data;
    },

    createTransaction: async (data: Omit<Transaction, 'id'>) => {
        const response = await api.post<Transaction>('/finance/transactions', data);
        return response.data;
    },

    createInvoice: async (data: Omit<Invoice, 'id'>) => {
        const response = await api.post<Invoice>('/finance/invoices', data);
        return response.data;
    }
};
