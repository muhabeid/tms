export interface MaintenanceJob {
    id: number;
    job_card_number: string;
    vehicle_id: number;
    job_type: 'SCHEDULED' | 'BREAKDOWN' | 'INSPECTION' | 'ACCIDENT_REPAIR' | 'UPGRADE';
    description: string;
    scheduled_date?: string;
    start_date?: string;
    completion_date?: string;
    priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
    status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
    total_cost?: number;
}

export interface StoreItem {
    id: number;
    part_number: string;
    name: string;
    description?: string;
    quantity_in_stock: number;
    unit_cost: number;
    shelf_location?: string;
}

export interface Supplier {
    id: number;
    name: string;
    contact_person?: string;
    phone: string;
    email?: string;
    status: 'ACTIVE' | 'INACTIVE';
}
