import React, { useEffect, useState } from 'react';
import Layout from '../../components/Layout';
import api from '../../services/api';

interface FuelLog {
  id: number;
  litres: number;
  vehicle_id?: number;
  fuel_station_id?: number;
  date_time?: string;
}

export default function FuelPage() {
  const [logs, setLogs] = useState<FuelLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await api.get<FuelLog[]>('/fuel/logs');
        setLogs(res.data);
      } catch (err) {
        console.error('Error fetching fuel logs', err);
        setError('Failed to load fuel logs. Ensure backend is running.');
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  return (
    <Layout title="Fuel">
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {!loading && !error && (
        <div>
          <h3 style={{ borderBottom: '1px solid #ddd', paddingBottom: '10px' }}>Recent Fuel Logs</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {logs.slice(0, 10).map((log) => (
              <li key={log.id} style={{ padding: '10px', borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontWeight: 'bold' }}>Log #{log.id}</div>
                  <div style={{ fontSize: '0.85rem', color: '#666' }}>{log.date_time ? new Date(log.date_time).toLocaleString() : ''}</div>
                </div>
                <div style={{ fontWeight: 'bold' }}>{log.litres} litres</div>
              </li>
            ))}
            {logs.length === 0 && <p style={{ color: '#999' }}>No fuel logs found.</p>}
          </ul>
        </div>
      )}
    </Layout>
  );
}