export interface Truck {
    id: number;
    plate_number: string;
    model: string;
    year?: number;
    mileage?: number;
    status: string;
    current_location?: string;
}

export interface DeliveryNote {
    id: number;
    delivery_number: string;
    truck_id: number;
    driver_id: number;
    cargo_description: string;
    cargo_category: 'LOCAL' | 'IMPORT' | 'EXPORT';
    tonnage: number;
    client_name: string;
    client_contact: string;
    consignee_name: string;
    consignee_contact: string;
    origin: string;
    destination: string;
    distance?: number;
    status: 'ACTIVE' | 'COMPLETED' | 'CANCELLED';
    created_date: string;
    start_date?: string;
    completion_date?: string;
}

export interface Trip {
    id: number;
    delivery_id: number;
    vehicle_id: number;
    fuel_consumed?: number;
    estimated_cost?: number;
    actual_cost?: number;
    start_odometer?: number;
    end_odometer?: number;
}
