import React, { ReactNode } from 'react';
import Link from 'next/link';

interface LayoutProps {
    children: ReactNode;
    title?: string;
}

const Layout: React.FC<LayoutProps> = ({ children, title = 'TMS' }) => {
    return (
        <div style={{ fontFamily: 'sans-serif', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <header style={{ backgroundColor: '#0066cc', color: 'white', padding: '1rem' }}>
                <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h1 style={{ margin: 0, fontSize: '1.5rem' }}>
                        <Link href="/" style={{ color: 'white', textDecoration: 'none' }}>TMS Full Stack</Link>
                    </h1>
                    <div />
                </div>
            </header>
            <main style={{ flex: 1, padding: '2rem', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
                {title && <h2 style={{ borderBottom: '2px solid #eee', paddingBottom: '10px', marginBottom: '20px' }}>{title}</h2>}
                {children}
            </main>
            <footer style={{ backgroundColor: '#f5f5f5', padding: '1rem', textAlign: 'center', borderTop: '1px solid #ddd' }}>
                <p style={{ margin: 0, color: '#666' }}>&copy; 2025 TMS System</p>
            </footer>
        </div>
    );
};

export default Layout;
