export interface Bus {
    id: number;
    plate_number: string;
    model: string;
    year?: number;
    capacity: number;
    mileage?: number;
    status: string;
    total_seats: number;
    seat_layout_json?: string;
}

export interface Route {
    id: number;
    name: string;
    origin: string;
    destination: string;
    distance?: number;
    duration?: number;
    schedule?: string;
    fare: number;
}

export interface Booking {
    id: number;
    route_id: number;
    bus_id: number;
    passenger_name: string;
    passenger_contact: string;
    seat_number: string;
    fare: number;
    travel_date: string;
    status: 'PENDING' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED';
    booking_date: string;
}
