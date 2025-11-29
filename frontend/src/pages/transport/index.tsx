import React, { useEffect, useState } from 'react';
import Layout from '../../components/Layout';
import { transportService } from '../../services/transportService';
import { Truck, DeliveryNote } from '../../types/transport';

export default function TransportDashboard() {
    const [trucks, setTrucks] = useState<Truck[]>([]);
    const [deliveries, setDeliveries] = useState<DeliveryNote[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [trucksData, deliveriesData] = await Promise.all([
                    transportService.getTrucks(),
                    transportService.getDeliveries()
                ]);
                setTrucks(trucksData);
                setDeliveries(deliveriesData);
            } catch (err) {
                console.error("Error fetching transport data:", err);
                setError("Failed to load transport data. Please ensure the backend is running.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) return <Layout title="Transport Dashboard"><p>Loading...</p></Layout>;
    if (error) return <Layout title="Transport Dashboard"><p style={{ color: 'red' }}>{error}</p></Layout>;

    return (
        <Layout title="Transport Dashboard">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px' }}>

                {/* Trucks Section */}
                <div>
                    <h3 style={{ borderBottom: '2px solid #0066cc', paddingBottom: '10px', color: '#0066cc' }}>Trucks</h3>
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                        {trucks.map(truck => (
                            <li key={truck.id} style={{ padding: '15px', border: '1px solid #eee', marginBottom: '10px', borderRadius: '8px', backgroundColor: '#e6f7ff' }}>
                                <div style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{truck.plate_number}</div>
                                <div style={{ color: '#666' }}>{truck.model} ({truck.year})</div>
                                <div style={{ marginTop: '5px' }}>
                                    <span style={{
                                        padding: '2px 8px',
                                        borderRadius: '12px',
                                        fontSize: '0.8rem',
                                        backgroundColor: truck.status === 'AVAILABLE' ? '#b7eb8f' : '#ffa39e',
                                        color: truck.status === 'AVAILABLE' ? '#135200' : '#820014'
                                    }}>
                                        {truck.status}
                                    </span>
                                    {truck.current_location && <span style={{ marginLeft: '10px', fontSize: '0.9rem', color: '#666' }}>📍 {truck.current_location}</span>}
                                </div>
                            </li>
                        ))}
                        {trucks.length === 0 && <p style={{ color: '#999' }}>No trucks found.</p>}
                    </ul>
                </div>

                {/* Deliveries Section */}
                <div>
                    <h3 style={{ borderBottom: '2px solid #fa8c16', paddingBottom: '10px', color: '#fa8c16' }}>Active Deliveries</h3>
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                        {deliveries.filter(d => d.status === 'ACTIVE').map(delivery => (
                            <li key={delivery.id} style={{ padding: '15px', border: '1px solid #eee', marginBottom: '10px', borderRadius: '8px', backgroundColor: '#fff7e6' }}>
                                <div style={{ fontWeight: 'bold' }}>{delivery.delivery_number}</div>
                                <div style={{ fontSize: '0.9rem', color: '#666', margin: '5px 0' }}>
                                    {delivery.origin} → {delivery.destination}
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ fontSize: '0.85rem', color: '#888' }}>{delivery.cargo_category}</span>
                                    <span style={{
                                        padding: '2px 6px',
                                        borderRadius: '4px',
                                        fontSize: '0.8rem',
                                        backgroundColor: '#ffd591',
                                        color: '#d46b08'
                                    }}>
                                        {delivery.status}
                                    </span>
                                </div>
                            </li>
                        ))}
                        {deliveries.filter(d => d.status === 'ACTIVE').length === 0 && <p style={{ color: '#999' }}>No active deliveries.</p>}
                    </ul>
                </div>

            </div>
        </Layout>
    );
}
