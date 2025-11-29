import React, { useEffect, useState } from 'react';
import Layout from '../../components/Layout';
import { expressService } from '../../services/expressService';
import { Bus, Route, Booking } from '../../types/express';

export default function ExpressDashboard() {
    const [buses, setBuses] = useState<Bus[]>([]);
    const [routes, setRoutes] = useState<Route[]>([]);
    const [bookings, setBookings] = useState<Booking[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [busesData, routesData, bookingsData] = await Promise.all([
                    expressService.getBuses(),
                    expressService.getRoutes(),
                    expressService.getBookings()
                ]);
                setBuses(busesData);
                setRoutes(routesData);
                setBookings(bookingsData);
            } catch (err) {
                console.error("Error fetching express data:", err);
                setError("Failed to load express data. Please ensure the backend is running.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) return <Layout title="Express Dashboard"><p>Loading...</p></Layout>;
    if (error) return <Layout title="Express Dashboard"><p style={{ color: 'red' }}>{error}</p></Layout>;

    return (
        <Layout title="Express Dashboard">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px' }}>

                {/* Buses Section */}
                <div>
                    <h3 style={{ borderBottom: '2px solid #00aa44', paddingBottom: '10px', color: '#00aa44' }}>Buses</h3>
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                        {buses.map(bus => (
                            <li key={bus.id} style={{ padding: '15px', border: '1px solid #eee', marginBottom: '10px', borderRadius: '8px', backgroundColor: '#f6ffed' }}>
                                <div style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{bus.plate_number}</div>
                                <div style={{ color: '#666' }}>{bus.model} ({bus.year})</div>
                                <div style={{ marginTop: '5px' }}>
                                    <span style={{
                                        padding: '2px 8px',
                                        borderRadius: '12px',
                                        fontSize: '0.8rem',
                                        backgroundColor: bus.status === 'AVAILABLE' ? '#b7eb8f' : '#ffa39e',
                                        color: bus.status === 'AVAILABLE' ? '#135200' : '#820014'
                                    }}>
                                        {bus.status}
                                    </span>
                                    <span style={{ marginLeft: '10px', fontSize: '0.9rem' }}>{bus.capacity} seats</span>
                                </div>
                            </li>
                        ))}
                        {buses.length === 0 && <p style={{ color: '#999' }}>No buses found.</p>}
                    </ul>
                </div>

                {/* Routes Section */}
                <div>
                    <h3 style={{ borderBottom: '2px solid #1890ff', paddingBottom: '10px', color: '#1890ff' }}>Routes</h3>
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                        {routes.map(route => (
                            <li key={route.id} style={{ padding: '15px', border: '1px solid #eee', marginBottom: '10px', borderRadius: '8px', backgroundColor: '#e6f7ff' }}>
                                <div style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{route.name}</div>
                                <div style={{ display: 'flex', alignItems: 'center', margin: '5px 0' }}>
                                    <span>{route.origin}</span>
                                    <span style={{ margin: '0 10px' }}>→</span>
                                    <span>{route.destination}</span>
                                </div>
                                <div style={{ fontWeight: 'bold', color: '#096dd9' }}>${route.fare}</div>
                            </li>
                        ))}
                        {routes.length === 0 && <p style={{ color: '#999' }}>No routes found.</p>}
                    </ul>
                </div>

                {/* Bookings Section */}
                <div>
                    <h3 style={{ borderBottom: '2px solid #722ed1', paddingBottom: '10px', color: '#722ed1' }}>Recent Bookings</h3>
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                        {bookings.slice(0, 5).map(booking => (
                            <li key={booking.id} style={{ padding: '15px', border: '1px solid #eee', marginBottom: '10px', borderRadius: '8px', backgroundColor: '#f9f0ff' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <span style={{ fontWeight: 'bold' }}>{booking.passenger_name}</span>
                                    <span style={{
                                        fontSize: '0.8rem',
                                        padding: '2px 6px',
                                        borderRadius: '4px',
                                        backgroundColor: booking.status === 'CONFIRMED' ? '#d3adf7' : '#f5f5f5'
                                    }}>{booking.status}</span>
                                </div>
                                <div style={{ fontSize: '0.9rem', marginTop: '5px' }}>Seat: {booking.seat_number}</div>
                                <div style={{ fontSize: '0.85rem', color: '#666' }}>{new Date(booking.travel_date).toLocaleDateString()}</div>
                            </li>
                        ))}
                        {bookings.length === 0 && <p style={{ color: '#999' }}>No bookings found.</p>}
                    </ul>
                </div>

            </div>
        </Layout>
    );
}
