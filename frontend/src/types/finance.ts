export interface Transaction {
    id: number;
    amount: number;
    transaction_type: 'REVENUE' | 'EXPENSE';
    description?: string;
    date: string;
    category?: string;
}

export interface Invoice {
    id: number;
    invoice_number: string;
    total_amount: number;
    status: 'DRAFT' | 'SENT' | 'PAID' | 'OVERDUE' | 'CANCELLED';
    due_date: string;
    client_name: string;
}

export interface FinancialSummary {
    total_revenue: number;
    total_expense: number;
    net_profit: number;
}

export interface CategoryTotal {
    category: string;
    total: number;
}

export interface DepartmentSummary {
    department: string;
    revenue: number;
    expense: number;
    net: number;
}
