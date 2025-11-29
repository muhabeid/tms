import React, { useEffect, useState } from 'react';
import Layout from '../../components/Layout';
import { workshopService } from '../../services/workshopService';
import { MaintenanceJob, StoreItem } from '../../types/workshop';

export default function WorkshopDashboard() {
    const [jobs, setJobs] = useState<MaintenanceJob[]>([]);
    const [items, setItems] = useState<StoreItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [jobsData, itemsData] = await Promise.all([
                    workshopService.getJobs(),
                    workshopService.getStoreItems()
                ]);
                setJobs(jobsData);
                setItems(itemsData);
            } catch (err) {
                console.error("Error fetching workshop data:", err);
                setError("Failed to load workshop data. Please ensure the backend is running.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) return <Layout title="Workshop Dashboard"><p>Loading...</p></Layout>;
    if (error) return <Layout title="Workshop Dashboard"><p style={{ color: 'red' }}>{error}</p></Layout>;

    return (
        <Layout title="Workshop Dashboard">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px' }}>

                {/* Jobs Section */}
                <div>
                    <h3 style={{ borderBottom: '2px solid #006699', paddingBottom: '10px', color: '#006699' }}>Maintenance Jobs</h3>
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                        {jobs.map(job => (
                            <li key={job.id} style={{ padding: '15px', border: '1px solid #eee', marginBottom: '10px', borderRadius: '8px', backgroundColor: '#e6f7ff' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <span style={{ fontWeight: 'bold' }}>{job.job_card_number}</span>
                                    <span style={{
                                        padding: '2px 6px',
                                        borderRadius: '4px',
                                        fontSize: '0.8rem',
                                        backgroundColor: job.priority === 'URGENT' ? '#ffccc7' : job.priority === 'HIGH' ? '#ffe7ba' : '#f0f5ff',
                                        color: job.priority === 'URGENT' ? '#cf1322' : job.priority === 'HIGH' ? '#d46b08' : '#2f54eb'
                                    }}>
                                        {job.priority}
                                    </span>
                                </div>
                                <div style={{ margin: '5px 0' }}>{job.description}</div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '5px' }}>
                                    <span style={{ fontSize: '0.85rem', color: '#666' }}>{job.job_type}</span>
                                    <span style={{
                                        fontSize: '0.8rem',
                                        color: job.status === 'COMPLETED' ? '#389e0d' : '#096dd9'
                                    }}>
                                        {job.status}
                                    </span>
                                </div>
                            </li>
                        ))}
                        {jobs.length === 0 && <p style={{ color: '#999' }}>No jobs found.</p>}
                    </ul>
                </div>

                {/* Store Items Section */}
                <div>
                    <h3 style={{ borderBottom: '2px solid #13c2c2', paddingBottom: '10px', color: '#13c2c2' }}>Store Inventory</h3>
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                        {items.map(item => (
                            <li key={item.id} style={{ padding: '15px', border: '1px solid #eee', marginBottom: '10px', borderRadius: '8px', backgroundColor: '#e6fffb' }}>
                                <div style={{ fontWeight: 'bold' }}>{item.name}</div>
                                <div style={{ fontSize: '0.9rem', color: '#666' }}>PN: {item.part_number}</div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '5px' }}>
                                    <span>Stock: {item.quantity_in_stock}</span>
                                    <span style={{ fontWeight: 'bold' }}>${item.unit_cost}</span>
                                </div>
                            </li>
                        ))}
                        {items.length === 0 && <p style={{ color: '#999' }}>No items in store.</p>}
                    </ul>
                </div>

            </div>
        </Layout>
    );
}
