export interface Employee {
    id: number;
    employee_number: string;
    name: string;
    email?: string;
    phone: string;
    phone_alt?: string;
    date_of_birth?: string;
    address?: string;
    role_title?: string;
    employee_type: 'DRIVER' | 'MECHANIC' | 'ADMIN' | 'MANAGER' | 'CLERK';
    department?: string;
    branch?: string;
    secondary_department?: string;
    status: 'ACTIVE' | 'ON_LEAVE' | 'SUSPENDED' | 'TERMINATED';
    employment_date: string;
    termination_date?: string;
    supervisor_id?: number;
    contract_type?: string;
    contract_start?: string;
    contract_end?: string;
    probation_end?: string;
    license_number?: string;
    emergency_contact_name?: string;
    emergency_contact_phone?: string;
}

export interface EmployeeDocument {
    id: number;
    employee_id: number;
    document_type: string;
    document_name: string;
    file_path?: string;
    tag?: string;
    expiry_date?: string;
    status: 'VALID' | 'EXPIRED' | 'EXPIRING_SOON';
    is_sensitive?: boolean;
    verified?: boolean;
    approved_by?: string;
    notes?: string;
    created_at?: string;
    updated_at?: string;
}

export interface Certification {
    id: number;
    employee_id: number;
    certification_type: string;
    certification_name: string;
    issuing_authority?: string;
    issue_date: string;
    expiry_date?: string;
    status: 'VALID' | 'EXPIRED' | 'EXPIRING_SOON';
}

export interface EmployeeCountByType {
    employee_type: 'DRIVER' | 'MECHANIC' | 'ADMIN' | 'MANAGER' | 'CLERK';
    count: number;
}
