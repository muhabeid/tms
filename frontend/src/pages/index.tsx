import { useEffect, useState } from 'react';
import Link from 'next/link';
import Layout from '../components/Layout';

interface ModuleData {
  transport: any[];
  express: any[];
  fuel: any[];
  hr: any[];
  finance: any[];
  workshop: any[];
}

export default function Home() {
  const [data, setData] = useState<ModuleData>({
    transport: [],
    express: [],
    fuel: [],
    hr: [],
    finance: [],
    workshop: []
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [transport, express, fuel, hr, finance, workshop] = await Promise.allSettled([
          fetch('/api/v1/transport/trips').then(res => res.json()),
          fetch('/api/v1/express/buses').then(res => res.json()),
          fetch('/api/v1/fuel/logs').then(res => res.json()),
          fetch('/api/v1/hr/employees').then(res => res.json()),
          fetch('/api/v1/finance/transactions').then(res => res.json()),
          fetch('/api/v1/workshop/jobs').then(res => res.json())
        ]);

        setData({
          transport: transport.status === 'fulfilled' ? transport.value : [],
          express: express.status === 'fulfilled' ? express.value : [],
          fuel: fuel.status === 'fulfilled' ? fuel.value : [],
          hr: hr.status === 'fulfilled' ? hr.value : [],
          finance: finance.status === 'fulfilled' ? finance.value : [],
          workshop: workshop.status === 'fulfilled' ? workshop.value : []
        });
      } catch (err) {
        console.error('Failed to fetch data:', err);
      }
    };

    fetchData();
  }, []);

  return (
    <Layout>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '20px', marginTop: '30px' }}>

        {/* Transport Module */}
        <Link href="/transport">
          <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px', backgroundColor: '#f9f9f9', cursor: 'pointer' }}>
            <h2 style={{ color: '#0066cc', marginTop: 0 }}>🚛 Transport</h2>
          </div>
        </Link>

        {/* Express Module */}
        <Link href="/express">
          <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px', backgroundColor: '#f9f9f9', cursor: 'pointer' }}>
            <h2 style={{ color: '#00aa44', marginTop: 0 }}>🚌 Express</h2>
          </div>
        </Link>

        {/* Fuel Module */}
        <Link href="/fuel">
          <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px', backgroundColor: '#f9f9f9', cursor: 'pointer' }}>
            <h2 style={{ color: '#ff6600', marginTop: 0 }}>⛽ Fuel</h2>
          </div>
        </Link>

        {/* HR Module */}
        <Link href="/hr">
          <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px', backgroundColor: '#f9f9f9', cursor: 'pointer' }}>
            <h2 style={{ color: '#9933cc', marginTop: 0 }}>👥 HR</h2>
          </div>
        </Link>

        {/* Finance Module */}
        <Link href="/finance">
          <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px', backgroundColor: '#f9f9f9', cursor: 'pointer' }}>
            <h2 style={{ color: '#cc0000', marginTop: 0 }}>💰 Finance</h2>
          </div>
        </Link>

        {/* Workshop Module */}
        <Link href="/workshop">
          <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px', backgroundColor: '#f9f9f9', cursor: 'pointer' }}>
            <h2 style={{ color: '#006699', marginTop: 0 }}>🔧 Workshop</h2>
          </div>
        </Link>

      </div>
    </Layout>
  );
}