import React, { useEffect, useState } from 'react';
import Layout from '../../components/Layout';
import { financeService } from '../../services/financeService';
import { Transaction, Invoice, FinancialSummary, CategoryTotal } from '../../types/finance';

export default function FinanceDashboard() {
    const [summary, setSummary] = useState<FinancialSummary | null>(null);
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [invoices, setInvoices] = useState<Invoice[]>([]);
    const [revenueByCategory, setRevenueByCategory] = useState<CategoryTotal[]>([]);
    const [expenseByCategory, setExpenseByCategory] = useState<CategoryTotal[]>([]);
    const [departmentSummary, setDepartmentSummary] = useState<{ department: string; revenue: number; expense: number; net: number }[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [summaryData, transactionsData, invoicesData, revenueData, expenseData, byDept] = await Promise.all([
                    financeService.getSummary(),
                    financeService.getTransactions(),
                    financeService.getInvoices(),
                    financeService.getRevenueByCategory(),
                    financeService.getExpenseByCategory(),
                    financeService.getByDepartment()
                ]);
                setSummary(summaryData);
                setTransactions(transactionsData);
                setInvoices(invoicesData);
                setRevenueByCategory(revenueData);
                setExpenseByCategory(expenseData);
                setDepartmentSummary(byDept);
            } catch (err) {
                console.error("Error fetching finance data:", err);
                setError("Failed to load finance data. Please ensure the backend is running.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) return <Layout title="Finance Dashboard"><p>Loading...</p></Layout>;
    if (error) return <Layout title="Finance Dashboard"><p style={{ color: 'red' }}>{error}</p></Layout>;

    return (
        <Layout title="Finance Dashboard">
            {/* Summary Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
                <div style={{ padding: '20px', backgroundColor: '#e6f7ff', borderRadius: '8px', border: '1px solid #91d5ff' }}>
                    <h3 style={{ margin: '0 0 10px 0', color: '#0050b3' }}>Total Revenue</h3>
                    <p style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>${summary?.total_revenue.toLocaleString()}</p>
                </div>
                <div style={{ padding: '20px', backgroundColor: '#fff1f0', borderRadius: '8px', border: '1px solid #ffa39e' }}>
                    <h3 style={{ margin: '0 0 10px 0', color: '#cf1322' }}>Total Expenses</h3>
                    <p style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>${summary?.total_expense.toLocaleString()}</p>
                </div>
                <div style={{ padding: '20px', backgroundColor: '#f6ffed', borderRadius: '8px', border: '1px solid #b7eb8f' }}>
                    <h3 style={{ margin: '0 0 10px 0', color: '#389e0d' }}>Net Profit</h3>
                    <p style={{ fontSize: '24px', fontWeight: 'bold', margin: 0, color: (summary?.net_profit || 0) >= 0 ? '#389e0d' : '#cf1322' }}>
                        ${summary?.net_profit.toLocaleString()}
                    </p>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
                {/* Recent Transactions */}
                <div>
                    <h3 style={{ borderBottom: '1px solid #ddd', paddingBottom: '10px' }}>Recent Transactions</h3>
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                        {transactions.slice(0, 5).map(t => (
                            <li key={t.id} style={{ padding: '10px', borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between' }}>
                                <div>
                                    <div style={{ fontWeight: 'bold' }}>{t.description || 'No description'}</div>
                                    <div style={{ fontSize: '0.85rem', color: '#666' }}>{new Date(t.date).toLocaleDateString()} - {t.category}</div>
                                </div>
                                <div style={{ fontWeight: 'bold', color: t.transaction_type === 'REVENUE' ? 'green' : 'red' }}>
                                    {t.transaction_type === 'REVENUE' ? '+' : '-'}${t.amount.toLocaleString()}
                                </div>
                            </li>
                        ))}
                        {transactions.length === 0 && <p style={{ color: '#999' }}>No transactions found.</p>}
                    </ul>
                </div>

                {/* Recent Invoices */}
                <div>
                    <h3 style={{ borderBottom: '1px solid #ddd', paddingBottom: '10px' }}>Recent Invoices</h3>
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                        {invoices.slice(0, 5).map(inv => (
                            <li key={inv.id} style={{ padding: '10px', borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between' }}>
                                <div>
                                    <div style={{ fontWeight: 'bold' }}>#{inv.invoice_number} - {inv.client_name}</div>
                                    <div style={{ fontSize: '0.85rem', color: '#666' }}>Due: {new Date(inv.due_date).toLocaleDateString()}</div>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <div style={{ fontWeight: 'bold' }}>${inv.total_amount.toLocaleString()}</div>
                                    <span style={{
                                        fontSize: '0.8rem',
                                        padding: '2px 6px',
                                        borderRadius: '4px',
                                        backgroundColor: inv.status === 'PAID' ? '#f6ffed' : inv.status === 'OVERDUE' ? '#fff1f0' : '#e6f7ff',
                                        color: inv.status === 'PAID' ? '#389e0d' : inv.status === 'OVERDUE' ? '#cf1322' : '#096dd9',
                                        border: '1px solid',
                                        borderColor: inv.status === 'PAID' ? '#b7eb8f' : inv.status === 'OVERDUE' ? '#ffa39e' : '#91d5ff'
                                    }}>
                                        {inv.status}
                                    </span>
                                </div>
                            </li>
                        ))}
                        {invoices.length === 0 && <p style={{ color: '#999' }}>No invoices found.</p>}
                    </ul>
                </div>
            </div>

            <div style={{ marginTop: '30px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
                <div>
                    <h3 style={{ borderBottom: '1px solid #ddd', paddingBottom: '10px' }}>Revenue by Category</h3>
                    {revenueByCategory.length === 0 && <p style={{ color: '#999' }}>No revenue data.</p>}
                    {revenueByCategory.length > 0 && (
                        <div>
                            {(() => {
                                const max = Math.max(...revenueByCategory.map(r => r.total));
                                return revenueByCategory.map(r => (
                                    <div key={r.category} style={{ marginBottom: '10px' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                            <span style={{ fontSize: '0.9rem', color: '#555' }}>{r.category}</span>
                                            <span style={{ fontWeight: 'bold' }}>${r.total.toLocaleString()}</span>
                                        </div>
                                        <div style={{ height: '10px', backgroundColor: '#e6f7ff', borderRadius: '6px' }}>
                                            <div style={{ width: `${(r.total / max) * 100}%`, height: '10px', backgroundColor: '#1890ff', borderRadius: '6px' }} />
                                        </div>
                                    </div>
                                ));
                            })()}
                        </div>
                    )}
                </div>
                <div>
                    <h3 style={{ borderBottom: '1px solid #ddd', paddingBottom: '10px' }}>Expenses by Category</h3>
                    {expenseByCategory.length === 0 && <p style={{ color: '#999' }}>No expense data.</p>}
                    {expenseByCategory.length > 0 && (
                        <div>
                            {(() => {
                                const max = Math.max(...expenseByCategory.map(r => r.total));
                                return expenseByCategory.map(r => (
                                    <div key={r.category} style={{ marginBottom: '10px' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                            <span style={{ fontSize: '0.9rem', color: '#555' }}>{r.category}</span>
                                            <span style={{ fontWeight: 'bold' }}>${r.total.toLocaleString()}</span>
                                        </div>
                                        <div style={{ height: '10px', backgroundColor: '#fff1f0', borderRadius: '6px' }}>
                                            <div style={{ width: `${(r.total / max) * 100}%`, height: '10px', backgroundColor: '#cf1322', borderRadius: '6px' }} />
                                        </div>
                                    </div>
                                ));
                            })()}
                        </div>
                    )}
                </div>
            </div>

            <div style={{ marginTop: '30px' }}>
                <h3 style={{ borderBottom: '1px solid #ddd', paddingBottom: '10px' }}>Department Breakdown</h3>
                {departmentSummary.length === 0 && <p style={{ color: '#999' }}>No department data.</p>}
                {departmentSummary.length > 0 && (
                    <div>
                        {(() => {
                            const max = Math.max(...departmentSummary.map(d => Math.max(d.revenue, d.expense)));
                            return departmentSummary.map(d => (
                                <div key={d.department} style={{ marginBottom: '14px' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                                        <span style={{ fontSize: '0.95rem', color: '#333' }}>{d.department}</span>
                                        <span style={{ fontSize: '0.9rem', color: '#666' }}>Net: ${d.net.toLocaleString()}</span>
                                    </div>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                                        <div>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                                                <span style={{ color: '#0050b3' }}>Revenue</span>
                                                <span style={{ fontWeight: 'bold' }}>${d.revenue.toLocaleString()}</span>
                                            </div>
                                            <div style={{ height: '10px', backgroundColor: '#e6f7ff', borderRadius: '6px' }}>
                                                <div style={{ width: `${(d.revenue / max) * 100}%`, height: '10px', backgroundColor: '#1890ff', borderRadius: '6px' }} />
                                            </div>
                                        </div>
                                        <div>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                                                <span style={{ color: '#cf1322' }}>Expense</span>
                                                <span style={{ fontWeight: 'bold' }}>${d.expense.toLocaleString()}</span>
                                            </div>
                                            <div style={{ height: '10px', backgroundColor: '#fff1f0', borderRadius: '6px' }}>
                                                <div style={{ width: `${(d.expense / max) * 100}%`, height: '10px', backgroundColor: '#cf1322', borderRadius: '6px' }} />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ));
                        })()}
                    </div>
                )}
            </div>
        </Layout>
    );
}
