import React, { useEffect, useState } from 'react';
 
import Layout from '../../components/Layout';
import { hrService } from '../../services/hrService';
import { Employee, EmployeeDocument, Certification, EmployeeCountByType } from '../../types/hr';

export default function HRDashboard() {
    const [activeTab, setActiveTab] = useState<'management' | 'operations' | 'analytics'>('management');
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [filters, setFilters] = useState<{ search?: string; branch?: string; department?: string; employee_type?: string; status?: string }>({});
    const [showCreate, setShowCreate] = useState(false);
    const [newEmp, setNewEmp] = useState<Partial<Employee>>({ employee_type: 'DRIVER', status: 'ACTIVE' as any });
    const [docs, setDocs] = useState<EmployeeDocument[]>([]);
    const [certs, setCerts] = useState<Certification[]>([]);
    const [counts, setCounts] = useState<EmployeeCountByType[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedEmp, setSelectedEmp] = useState<Employee | null>(null);
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [engagement, setEngagement] = useState<'FULL_TIME' | 'PROBATION' | 'CONTRACT'>('FULL_TIME');
    const [engagementMonths, setEngagementMonths] = useState<string>('');
    const [excludedWeekdays, setExcludedWeekdays] = useState<number[]>([0]);
    const [holidays, setHolidays] = useState<string[]>([]);
    const [docForm, setDocForm] = useState<{ document_type?: string; document_name?: string; sub_type?: string; tag?: string; issue_date?: string; expiry_date?: string; file?: File }>({});
    const [docQueue, setDocQueue] = useState<Array<{ document_type: string; document_name: string; tag?: string; issue_date?: string; expiry_date?: string; file: File }>>([]);
    const [uploadResetKey, setUploadResetKey] = useState(0);
    const [identity, setIdentity] = useState<{ id_or_passport?: string; kra_pin?: string; nhif?: string; nssf?: string; passport_photo?: File }>({});
    const [inlineEdits, setInlineEdits] = useState<Record<number, Partial<Employee>>>({});
    const [quickAdd, setQuickAdd] = useState(false);
    const [drafts, setDrafts] = useState<Array<{ id: string; name: string; department: string; role_title: string; branch: string }>>([]);
    const currentUser = { role: 'HR_OFFICER', branch: 'HQ' };
    const canManageEmployee = (emp?: Employee | null) => {
        if (!emp) return false;
        if (currentUser.role === 'HR_ADMIN') return true;
        return emp.branch ? emp.branch === currentUser.branch : false;
    };
    const canManageNew = () => {
        if (currentUser.role === 'HR_ADMIN') return true;
        return newEmp.branch ? newEmp.branch === currentUser.branch : false;
    };

    const departmentRoles: Record<string, string[]> = {
        Transport: ['Dispatcher','Operations Manager','Logistics Officer','Driver','Tracking','Invoicing'],
        Express: ['Operations Manager','Booking Clerk (Passengers & Parcel)','Conductor','Driver (Bus)','Route Supervisor','Parcel Officer','Revenue Clerk','Tracking'],
        Fuel: ['Fuel Manager','Fuel Clerk','Lubricant Officer','Fuel Pump Attendant'],
        Workshop: ['Workshop Manager','Foreman','Job Card Clerk','Mechanic','Electrician','Panel Beater','Welder','Tyre Technician','Store Manager','Store Clerk','Checklist Officer'],
        HR: ['HR Manager','HR Assistant'],
        Finance: ['Finance Manager','Accountant','Cashier'],
        'Support Services': ['Security Supervisor','Security','Watchman','Carwash','Loader','Machine Operator','Yard Controller','Safety Compliance Officer'],
        'System-wide': ['System Administrator','General Manager']
    };

    const roleToType = (role: string): Employee['employee_type'] => {
        const r = role.toLowerCase();
        if (r.includes('driver')) return 'DRIVER';
        if (['mechanic','electrician','welder','panel beater','tyre technician'].some(k => r.includes(k))) return 'MECHANIC';
        if (r.includes('manager')) return 'MANAGER';
        if (['clerk','officer','attendant','supervisor','controller','assistant'].some(k => r.includes(k))) return 'CLERK';
        return 'ADMIN';
    };
    const findDepartmentManagerId = (dept?: string) => {
        if (!dept) return undefined;
        const manager = employees.find(e => (e.department || '') === dept && (((e.role_title || '').toLowerCase().includes('manager')) || e.employee_type === 'MANAGER'));
        return manager?.id;
    };

    const deptCode = (dept?: string) => {
        if (!dept) return 'EMP';
        const map: Record<string,string> = {
            Transport: 'TPT',
            Express: 'EXP',
            Fuel: 'FUL',
            Workshop: 'WSH',
            HR: 'HR',
            Finance: 'FIN',
            'Support Services': 'SUP',
            'System-wide': 'SYS'
        };
        return map[dept] || 'EMP';
    };

    const addMonths = (start: string, m: number) => {
        const d = new Date(start);
        d.setMonth(d.getMonth() + m);
        const y = d.getFullYear();
        const mm = String(d.getMonth() + 1).padStart(2, '0');
        const dd = String(d.getDate()).padStart(2, '0');
        return `${y}-${mm}-${dd}`;
    };

    const businessDaysBetween = (start: string, end: string, excluded: number[] = [0, 6], holidayList: string[] = []) => {
        const s = new Date(start);
        const e = new Date(end);
        let total = 0;
        for (let d = new Date(s); d <= e; d.setDate(d.getDate() + 1)) {
            const day = d.getDay();
            const y = d.getFullYear();
            const mm = String(d.getMonth() + 1).padStart(2, '0');
            const dd = String(d.getDate()).padStart(2, '0');
            const iso = `${y}-${mm}-${dd}`;
            if (excluded.includes(day)) continue;
            if (holidayList.includes(iso)) continue;
            total += 1;
        }
        const today = new Date();
        const startForRemaining = new Date(Math.max(today.getTime(), s.getTime()));
        let remaining = 0;
        for (let d = new Date(startForRemaining); d <= e; d.setDate(d.getDate() + 1)) {
            const day = d.getDay();
            const y = d.getFullYear();
            const mm = String(d.getMonth() + 1).padStart(2, '0');
            const dd = String(d.getDate()).padStart(2, '0');
            const iso = `${y}-${mm}-${dd}`;
            if (excluded.includes(day)) continue;
            if (holidayList.includes(iso)) continue;
            remaining += 1;
        }
        return { total, remaining };
    };

    const generateEmployeeNumber = (dept?: string) => {
        const code = deptCode(dept);
        const deptEmployees = employees.filter(e => (e.department || '') === (dept || ''));
        let max = 0;
        deptEmployees.forEach(e => {
            const parts = e.employee_number.split('-');
            const numStr = parts[parts.length - 1];
            const n = parseInt(numStr, 10);
            if (!isNaN(n)) max = Math.max(max, n);
        });
        const next = max + 1;
        const pad = String(next).padStart(4, '0');
        return `${code}-${pad}`;
    };

    useEffect(() => {
        const loadManagement = async () => {
            const data = await hrService.getEmployees(filters);
            setEmployees(data);
        };
        const loadOperations = async () => {
            const [expDocs, expCerts] = await Promise.all([
                hrService.getExpiringDocuments(60),
                hrService.getExpiringCertifications(60)
            ]);
            setDocs(expDocs);
            setCerts(expCerts);
        };
        const loadAnalytics = async () => {
            const data = await hrService.getEmployeeCountByType();
            setCounts(data);
        };

        const init = async () => {
            try {
                await loadManagement();
                await loadOperations();
                await loadAnalytics();
                const yr = new Date().getFullYear();
                const holidayCfg = await hrService.getHolidays({ year: yr, branch: currentUser.branch, country: 'KE' });
                setHolidays(holidayCfg.dates || []);
            } catch (err) {
                console.error('Error loading HR dashboard', err);
                setError('Failed to load HR data. Ensure backend is running.');
            } finally {
                setLoading(false);
            }
        };
        init();
    }, [filters]);

    useEffect(() => {
        try {
            const raw = localStorage.getItem('hr_drafts');
            if (raw) {
                const list = JSON.parse(raw) as Array<{ id: string; name: string; department: string; role_title: string; branch: string }>;
                setDrafts(list);
            }
        } catch {}
    }, []);

    useEffect(() => {
        const dept = newEmp.department || '';
        const role = (newEmp.role_title || '').toLowerCase();
        const isTransportDriver = dept === 'Transport' && role.includes('driver');
        const isExpressDriver = dept === 'Express' && role.includes('driver');
        const transportReq = [
            "Valid Driver's License (BCE)",
            'Defensive Driving Certificate',
            'Medical Fitness Certificate',
            'Road Safety Training Certificate'
        ];
        const expressReq = [
            "Valid Driver's License (PSV)",
            'PSV Badge',
            'Medical Fitness Certificate',
            'Defensive Driving Certificate'
        ];
        const existing = new Set(docQueue.map(d => (d.document_name || '').split(' - ')[0]));
        const candidates = isTransportDriver ? transportReq : isExpressDriver ? expressReq : [];
        const next = candidates.find(n => !existing.has(n));
        if (next) {
            const map: Record<string, { type: string; tag?: string }> = {
                "Valid Driver's License (BCE)": { type: 'LICENSE', tag: 'transport' },
                'Defensive Driving Certificate': { type: 'CERTIFICATE', tag: 'legal' },
                'Medical Fitness Certificate': { type: 'CERTIFICATE', tag: 'medical' },
                'Road Safety Training Certificate': { type: 'CERTIFICATE', tag: 'legal' },
                "Valid Driver's License (PSV)": { type: 'LICENSE', tag: 'express' },
                'PSV Badge': { type: 'LICENSE', tag: 'express' }
            };
            const sel = map[next];
            if (!docForm.document_name || !candidates.includes(docForm.document_name)) {
                setDocForm({ ...docForm, document_name: next, document_type: sel ? sel.type : undefined, tag: sel ? sel.tag : undefined });
            }
        }
    }, [newEmp.department, newEmp.role_title, docQueue]);

    const TabButton = ({ id, label }: { id: 'management' | 'operations' | 'analytics'; label: string }) => (
        <button
            onClick={() => setActiveTab(id)}
            style={{
                padding: '10px 16px',
                border: '1px solid #ddd',
                borderBottom: activeTab === id ? '2px solid #722ed1' : '1px solid #ddd',
                borderRadius: '6px 6px 0 0',
                backgroundColor: activeTab === id ? '#f9f0ff' : '#fafafa',
                color: '#722ed1',
                marginRight: '8px',
                cursor: 'pointer'
            }}
        >
            {label}
        </button>
    );

    if (loading) return <Layout title="HR Dashboard"><p>Loading...</p></Layout>;
    if (error) return <Layout title="HR Dashboard"><p style={{ color: 'red' }}>{error}</p></Layout>;

    return (
        <Layout title="HR Dashboard">
            <div>
                <div style={{ display: 'flex', borderBottom: '1px solid #ddd', marginBottom: '16px' }}>
                    <TabButton id="management" label="Employee Management" />
                    <TabButton id="operations" label="Workforce Operations" />
                    <TabButton id="analytics" label="HR Analytics & Administration" />
                </div>

                {activeTab === 'management' && (
                    <div>
                        <div style={{ marginBottom: 12 }}>
                            <button onClick={() => setShowCreate(prev => !prev)} style={{ padding: '8px 12px', background: '#722ed1', color: '#fff', border: 0, borderRadius: 6, cursor: 'pointer' }}>
                                {showCreate ? 'Close' : 'Register Employee'}
                            </button>
                        </div>
                        
                        {showCreate && (
                            <div style={{ marginTop: 0, border: '1px solid #eee', padding: 16, borderRadius: 8, background: '#fafafa' }}>
                                <h4 style={{ marginTop: 0 }}>Register New Employee</h4>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                        <input type="checkbox" checked={quickAdd} onChange={e => setQuickAdd(e.target.checked)} />
                                        Quick Add Only
                                    </label>
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 12 }}>
                                    <input placeholder="First Name" value={firstName} onChange={e => setFirstName(e.target.value)} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                    <input placeholder="Last Name" value={lastName} onChange={e => setLastName(e.target.value)} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                    <input placeholder="Email" value={newEmp.email || ''} onChange={e => setNewEmp({ ...newEmp, email: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                    <input placeholder="+254 7xx xxx xxx" value={newEmp.phone || ''} onChange={e => setNewEmp({ ...newEmp, phone: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                    <input placeholder="Alt +254 7xx xxx xxx" value={newEmp.phone_alt || ''} onChange={e => setNewEmp({ ...newEmp, phone_alt: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                    <input placeholder="Address" value={newEmp.address || ''} onChange={e => setNewEmp({ ...newEmp, address: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                    <select value={newEmp.department || ''} onChange={e => setNewEmp({ ...newEmp, department: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }}>
                                        <option value="">Select Department</option>
                                        {Object.keys(departmentRoles).map(d => <option key={d} value={d}>{d}</option>)}
                                    </select>
                                    <select value={newEmp.role_title || ''} onChange={e => setNewEmp({ ...newEmp, role_title: e.target.value, employee_type: roleToType(e.target.value) })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }}>
                                        <option value="">Select Role</option>
                                        {(newEmp.department ? departmentRoles[newEmp.department] : []).map(r => <option key={r} value={r}>{r}</option>)}
                                    </select>
                                    {newEmp.department === 'Workshop' && newEmp.role_title ? (
                                        <select value={newEmp.secondary_department || ''} onChange={e => setNewEmp({ ...newEmp, secondary_department: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }}>
                                            <option value="">Reference Major Department</option>
                                            {['Transport','Express'].map(x => <option key={x} value={x}>{x}</option>)}
                                        </select>
                                    ) : null}
                                    
                                    <select value={newEmp.branch || ''} onChange={e => setNewEmp({ ...newEmp, branch: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }}>
                                        <option value="">Select Branch</option>
                                        {['Main Yard','Satelite yard','Nairobi Yard'].map(b => <option key={b} value={b}>{b}</option>)}
                                    </select>
                                    <select value={newEmp.status || 'ACTIVE'} onChange={e => setNewEmp({ ...newEmp, status: e.target.value as any })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }}>
                                        {['ACTIVE','ON_LEAVE','SUSPENDED','TERMINATED'].map(s => <option key={s} value={s}>{s}</option>)}
                                    </select>
                                    <select value={engagement} onChange={e => setEngagement(e.target.value as any)} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }}>
                                        {['PROBATION','CONTRACT','FULL_TIME'].map(x => <option key={x} value={x}>{x}</option>)}
                                    </select>
                                    <input type="date" value={newEmp.employment_date || ''} onChange={e => setNewEmp({ ...newEmp, employment_date: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                    {(engagement === 'PROBATION' || engagement === 'CONTRACT') && (
                                        <select value={engagementMonths} onChange={e => setEngagementMonths(e.target.value)} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }}>
                                            <option value="">Select months</option>
                                            {[3,6,9,12].map(m => <option key={m} value={String(m)}>{m}</option>)}
                                        </select>
                                    )}
                                    {(engagement === 'PROBATION' || engagement === 'CONTRACT') && newEmp.employment_date && engagementMonths && (
                                        <div style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }}>
                                            {(() => {
                                                const end = addMonths(newEmp.employment_date!, parseInt(engagementMonths, 10));
                                                const { total, remaining } = businessDaysBetween(newEmp.employment_date!, end, excludedWeekdays, holidays);
                                                return `Business days till completion: ${Math.max(remaining, 0)} (total ${total})`;
                                            })()}
                                            </div>
                                        )}
                                    
                                    <input placeholder="Emergency Contact Name" value={newEmp.emergency_contact_name || ''} onChange={e => setNewEmp({ ...newEmp, emergency_contact_name: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                    <input placeholder="Emergency Contact Phone" value={newEmp.emergency_contact_phone || ''} onChange={e => setNewEmp({ ...newEmp, emergency_contact_phone: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                </div>
                                <div style={{ marginTop: 12 }}>
                                    <h5 style={{ margin: '8px 0' }}>Identity & Personal</h5>
                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 8 }}>
                                        <input placeholder="National ID / Passport Number" value={identity.id_or_passport || ''} onChange={e => setIdentity({ ...identity, id_or_passport: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6, width: '100%' }} />
                                        <input placeholder="KRA PIN" value={identity.kra_pin || ''} onChange={e => setIdentity({ ...identity, kra_pin: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6, width: '100%' }} />
                                        <input placeholder="NHIF Number" value={identity.nhif || ''} onChange={e => setIdentity({ ...identity, nhif: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6, width: '100%' }} />
                                        <input placeholder="NSSF Number" value={identity.nssf || ''} onChange={e => setIdentity({ ...identity, nssf: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6, width: '100%' }} />
                                        <div style={{ display: 'grid', gap: 6 }}>
                                            <span style={{ fontSize: '0.9rem', color: '#666' }}>Passport-size Photo</span>
                                            <input type="file" onChange={e => setIdentity({ ...identity, passport_photo: e.target.files?.[0] })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                            <div style={{ border: '1px dashed #ddd', borderRadius: 6, height: 120, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fafafa' }}>
                                                {identity.passport_photo ? <span>{identity.passport_photo.name}</span> : <span style={{ color: '#999' }}>Photo preview will appear here</span>}
                                            </div>
                                        </div>
                                    </div>
                                    <h5 style={{ margin: '16px 0 8px' }}>Universal Documents</h5>
                                    <div key={uploadResetKey} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 8 }}>
                                        <select value={docForm.document_name || ''} onChange={e => {
                                            const name = e.target.value;
                                            const baseName = name.split(' - ')[0];
                                            const subtype = name.includes(' - ') ? name.split(' - ')[1] : undefined;
                                            const map: Record<string, { type: string; tag?: string }> = {
                                                "Signed Employment Contract": { type: 'CONTRACT', tag: 'legal' },
                                                "Job Offer Letter": { type: 'CONTRACT', tag: 'legal' },
                                                "Letter of Acceptance": { type: 'CONTRACT', tag: 'legal' },
                                                "Employee Personal Data Form": { type: 'OTHER', tag: 'personal' },
                                                "CV / Résumé": { type: 'OTHER', tag: 'personal' },
                                                "Academic Certificate": { type: 'CERTIFICATE', tag: 'legal' },
                                                "Good Conduct Certificate": { type: 'CERTIFICATE', tag: 'legal' },
                                                "Referee Letter": { type: 'OTHER', tag: 'personal' },
                                                "Signed Company Policies": { type: 'OTHER', tag: 'legal' }
                                            };
                                            const sel = map[baseName] || map[name];
                                            setDocForm({ ...docForm, document_name: baseName, sub_type: subtype, document_type: sel ? sel.type : undefined, tag: sel ? sel.tag : undefined });
                                        }} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }}>
                                            <option value="">Select Document</option>
                                            <option value="Signed Employment Contract">Signed Employment Contract</option>
                                            <option value="Job Offer Letter">Job Offer Letter</option>
                                            <option value="Letter of Acceptance">Letter of Acceptance</option>
                                            <option value="Employee Personal Data Form">Employee Personal Data Form</option>
                                            <option value="CV / Résumé">CV / Résumé</option>
                                            <option value="Academic Certificate">Academic Certificate</option>
                                            <option value="Good Conduct Certificate">Good Conduct Certificate</option>
                                            <option value="Referee Letter">Referee Letter</option>
                                            <option value="Signed Company Policies">Signed Company Policies</option>
                                        </select>
                                        <input placeholder="Tag (legal/personal/medical)" value={docForm.tag || ''} onChange={e => setDocForm({ ...docForm, tag: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                        <input type="date" placeholder="Issue date" value={docForm.issue_date || ''} onChange={e => setDocForm({ ...docForm, issue_date: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                        <input type="date" placeholder="Expiry date" value={docForm.expiry_date || ''} onChange={e => setDocForm({ ...docForm, expiry_date: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                        {docForm.document_name === 'Academic Certificate' && (
                                            <input placeholder="Sub-type (Diploma/Degree/etc)" value={docForm.sub_type || ''} onChange={e => setDocForm({ ...docForm, sub_type: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                        )}
                                        <input type="file" onChange={e => {
                                            const f = e.target.files?.[0];
                                            if (f) setDocForm({ ...docForm, file: f });
                                        }} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                        <button onClick={() => {
                                            if (!docForm.document_type || !docForm.document_name || !docForm.file) return alert('Fill type, name, and select file');
                                            const nameWithSubtype = docForm.sub_type ? `${docForm.document_name} - ${docForm.sub_type}` : docForm.document_name;
                                            const item = {
                                                document_type: docForm.document_type,
                                                document_name: nameWithSubtype,
                                                tag: docForm.tag,
                                                issue_date: docForm.issue_date,
                                                expiry_date: docForm.expiry_date,
                                                file: docForm.file
                                            };
                                            setDocQueue([item, ...docQueue]);
                                            setDocForm({});
                                            setUploadResetKey(k => k + 1);
                                        }} style={{ padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer', background: '#fff' }}>Add to Queue</button>
                                        <div style={{ fontSize: '0.85rem', color: '#666' }}>Add multiple documents by repeating “Add to Queue” before Save.</div>
                                    </div>
                                    {(newEmp.department && newEmp.role_title) ? (
                                        (() => {
                                            const dept = newEmp.department || '';
                                            const role = (newEmp.role_title || '').toLowerCase();
                                            const isTransportDriver = dept === 'Transport' && role.includes('driver');
        
                                            const isExpressDriver = dept === 'Express' && role.includes('driver');
                                            if (!isTransportDriver && !isExpressDriver) return null;
                                            return (
                                            <div style={{ marginTop: 12 }}>
                                            <h5 style={{ margin: '16px 0 8px' }}>Department-Specific Documents</h5>
                                            <div key={uploadResetKey} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 8 }}>
                                                <select value={docForm.document_name || ''} onChange={e => {
                                                    const name = e.target.value;
                                                    const map: Record<string, { type: string; tag?: string }> = {
                                                        "Valid Driver's License (BCE)": { type: 'LICENSE', tag: 'transport' },
                                                        "Defensive Driving Certificate": { type: 'CERTIFICATE', tag: 'legal' },
                                                        "Medical Fitness Certificate": { type: 'CERTIFICATE', tag: 'medical' },
                                                        "Road Safety Training Certificate": { type: 'CERTIFICATE', tag: 'legal' },
                                                        "Valid Driver's License (PSV)": { type: 'LICENSE', tag: 'express' },
                                                        "PSV Badge": { type: 'LICENSE', tag: 'express' }
                                                    };
                                                    const sel = map[name];
                                                    setDocForm({ ...docForm, document_name: name, document_type: sel ? sel.type : undefined, tag: sel ? sel.tag : undefined });
                                                }} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }}>
                                                    <option value="">Select Document</option>
                                                    {(() => {
                                                        const isTransportDriver = dept === 'Transport' && role.includes('driver');
                                                        const isExpressDriver = dept === 'Express' && role.includes('driver');
                                                        return (
                                                            <>
                                                                {isTransportDriver && (
                                                                    <>
                                                                        <option value="Valid Driver's License (BCE)">Valid Driver's License (BCE)</option>
                                                                        <option value="Defensive Driving Certificate">Defensive Driving Certificate</option>
                                                                        <option value="Medical Fitness Certificate">Medical Fitness Certificate</option>
                                                                        <option value="Road Safety Training Certificate">Road Safety Training Certificate</option>
                                                                    </>
                                                                )}
                                                                {isExpressDriver && (
                                                                    <>
                                                                        <option value="Valid Driver's License (PSV)">Valid Driver's License (PSV)</option>
                                                                        <option value="PSV Badge">PSV Badge</option>
                                                                        <option value="Medical Fitness Certificate">Medical Fitness Certificate</option>
                                                                        <option value="Defensive Driving Certificate">Defensive Driving Certificate</option>
                                                                    </>
                                                                )}
                                                            </>
                                                        );
                                                    })()}
                                                </select>
                                                <input placeholder="Tag (legal/personal/medical)" value={docForm.tag || ''} onChange={e => setDocForm({ ...docForm, tag: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                                <input type="file" onChange={e => {
                                                    const f = e.target.files?.[0];
                                                    if (f) setDocForm({ ...docForm, file: f });
                                                }} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                                <button onClick={() => {
                                                    if (!docForm.document_type || !docForm.document_name || !docForm.file) return alert('Fill type, name, and select file');
                                                    const nameWithSubtype = docForm.sub_type ? `${docForm.document_name} - ${docForm.sub_type}` : docForm.document_name;
                                                    const item = {
                                                        document_type: docForm.document_type,
                                                        document_name: nameWithSubtype,
                                                        tag: docForm.tag,
                                                        file: docForm.file
                                                    };
                                                    setDocQueue([item, ...docQueue]);
                                                    setDocForm({});
                                                    setUploadResetKey(k => k + 1);
                                                }} style={{ padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer', background: '#fff' }}>Add to Queue</button>
                                            </div>
                                        </div>
                                        );
                                        })()
                                    ) : (
                                        <div style={{ marginTop: 12, color: '#666' }}>Select Department and Role to show department-specific documents</div>
                                    )}
                                    {docQueue.length > 0 && (
                                        <div style={{ marginTop: 8 }}>
                                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                                <thead>
                                                    <tr style={{ backgroundColor: '#f5f5f5', textAlign: 'left' }}>
                                                        <th style={{ padding: 8, borderBottom: '1px solid #ddd' }}>Type</th>
                                                        <th style={{ padding: 8, borderBottom: '1px solid #ddd' }}>Name</th>
                                                        <th style={{ padding: 8, borderBottom: '1px solid #ddd' }}>Tag</th>
                                                        <th style={{ padding: 8, borderBottom: '1px solid #ddd' }}>Actions</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {docQueue.map((d, idx) => (
                                                        <tr key={idx} style={{ borderBottom: '1px solid #eee' }}>
                                                            <td style={{ padding: 8 }}>{d.document_type}</td>
                                                            <td style={{ padding: 8 }}>{d.document_name}</td>
                                                            <td style={{ padding: 8 }}>{d.tag || '-'}</td>
                                                            <td style={{ padding: 8 }}>
                                                                <button onClick={() => setDocQueue(docQueue.filter((_, i) => i !== idx))} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer' }}>Remove</button>
                                                            </td>
                                                    </tr>
                                                ))}
                                                </tbody>
                                            </table>
                                        {(() => {
                                            const legalNames = [
                                                'Signed Employment Contract',
                                                'Job Offer Letter',
                                                'Letter of Acceptance',
                                                'Employee Personal Data Form',
                                                'CV / Résumé',
                                                'Academic Certificate',
                                                'Good Conduct Certificate',
                                                'Referee Letter',
                                                'Signed Company Policies'
                                            ];
                                            const legalCount = docQueue.filter(d => legalNames.includes((d.document_name || '').split(' - ')[0])).length;
                                            const color = legalCount >= 4 ? '#135200' : '#a8071a';
                                            const dept = newEmp.department || '';
                                            const role = (newEmp.role_title || '').toLowerCase();
                                            const transportReq = ["Valid Driver's License (BCE)", 'Defensive Driving Certificate', 'Medical Fitness Certificate', 'Road Safety Training Certificate'];
                                            const expressReq = ["Valid Driver's License (PSV)", 'PSV Badge', 'Medical Fitness Certificate', 'Defensive Driving Certificate'];
                                            const missingTransport = transportReq.filter(r => !docQueue.some(d => (d.document_name || '').startsWith(r)));
                                            const missingExpress = expressReq.filter(r => !docQueue.some(d => (d.document_name || '').startsWith(r)));
                                            return (
                                                <div style={{ marginTop: 12, display: 'grid', gap: 8 }}>
                                                    <div>
                                                        <strong>Legal documents added:</strong> <span style={{ color }}>{legalCount}/4</span>
                                                    </div>
                                                    {dept === 'Transport' && role.includes('driver') && (
                                                        <div>
                                                            <strong>Transport driver requirements missing:</strong> {missingTransport.length === 0 ? 'None' : missingTransport.join(', ')}
                                                        </div>
                                                    )}
                                                    {dept === 'Express' && role.includes('driver') && (
                                                        <div>
                                                            <strong>Express driver requirements missing:</strong> {missingExpress.length === 0 ? 'None' : missingExpress.join(', ')}
                                                        </div>
                                                    )}
                                                </div>
                                            );
                                        })()}
                                        </div>
                                    )}
                                </div>
                                <div style={{ marginTop: 12 }}>
                                    <button onClick={async () => {
                                        if (quickAdd) {
                                            const autoNumber = generateEmployeeNumber(newEmp.department);
                                            const draftId = `${autoNumber}-${Date.now()}`;
                                            const draft = {
                                                id: draftId,
                                                name: `${firstName} ${lastName}`.trim(),
                                                department: newEmp.department || '',
                                                role_title: newEmp.role_title || '',
                                                branch: newEmp.branch || ''
                                            };
                                            const list = [draft, ...drafts];
                                            setDrafts(list);
                                            localStorage.setItem('hr_drafts', JSON.stringify(list));
                                            setShowCreate(false);
                                            setQuickAdd(false);
                                            return;
                                        }
                                        if (!identity.id_or_passport || !identity.kra_pin || !identity.nhif || !identity.nssf || !identity.passport_photo) {
                                            alert('Enter National ID/Passport, KRA PIN, NHIF, NSSF and upload passport photo');
                                            return;
                                        }
                                        const legalNames = [
                                            'Signed Employment Contract',
                                            'Job Offer Letter',
                                            'Letter of Acceptance',
                                            'Employee Personal Data Form',
                                            'CV / Résumé',
                                            'Academic Certificate',
                                            'Good Conduct Certificate',
                                            'Referee Letter',
                                            'Signed Company Policies'
                                        ];
                                        const legalCount = docQueue.filter(d => legalNames.includes((d.document_name || '').split(' - ')[0])).length;
                                        if (legalCount < 4) {
                                            alert('Upload at least 4 Employment & Legal documents');
                                            return;
                                        }
                                        const dept = newEmp.department || '';
                                        const role = (newEmp.role_title || '').toLowerCase();
                                        if (dept === 'Transport' && role.includes('driver')) {
                                            const required = [
                                                "Valid Driver's License (BCE)",
                                                'Defensive Driving Certificate',
                                                'Medical Fitness Certificate',
                                                'Road Safety Training Certificate'
                                            ];
                                            const hasAll = required.every(r => docQueue.some(d => (d.document_name || '').startsWith(r)));
                                            if (!hasAll) {
                                                alert('Transport drivers must upload BCE license, Defensive Driving, Medical Fitness, and Road Safety Training');
                                                return;
                                            }
                                        }
                                        if (dept === 'Express' && role.includes('driver')) {
                                            const required = [
                                                "Valid Driver's License (PSV)",
                                                'PSV Badge',
                                                'Medical Fitness Certificate',
                                                'Defensive Driving Certificate'
                                            ];
                                            const hasAll = required.every(r => docQueue.some(d => (d.document_name || '').startsWith(r)));
                                            if (!hasAll) {
                                                alert('Express bus drivers must upload PSV license, PSV badge, Medical Fitness, and Defensive Driving');
                                                return;
                                            }
                                        }
                                        const autoNumber = generateEmployeeNumber(newEmp.department);
                                        const payload = {
                                            employee_number: autoNumber,
                                            name: `${firstName} ${lastName}`.trim(),
                                            email: newEmp.email || undefined,
                                            phone: newEmp.phone!,
                                            phone_alt: newEmp.phone_alt || undefined,
                                            date_of_birth: undefined,
                                            address: newEmp.address || undefined,
                                            role_title: newEmp.role_title || undefined,
                                            employee_type: newEmp.employee_type!,
                                            department: newEmp.department || undefined,
                                            branch: newEmp.branch || undefined,
                                            secondary_department: newEmp.secondary_department || undefined,
                                            supervisor_id: findDepartmentManagerId(newEmp.department) || undefined,
                                            status: newEmp.status || 'ACTIVE',
                                            employment_date: newEmp.employment_date!,
                                            termination_date: undefined,
                                            contract_type: engagement === 'FULL_TIME' ? 'FULL_TIME' : engagement,
                                            contract_start: engagement === 'CONTRACT' ? newEmp.employment_date! : undefined,
                                            contract_end: engagement === 'CONTRACT' && engagementMonths ? (() => { const d = new Date(newEmp.employment_date!); d.setMonth(d.getMonth() + parseInt(engagementMonths, 10)); const y = d.getFullYear(); const mm = String(d.getMonth() + 1).padStart(2, '0'); const dd = String(d.getDate()).padStart(2, '0'); return `${y}-${mm}-${dd}`; })() : undefined,
                                            probation_end: engagement === 'PROBATION' && engagementMonths ? (() => { const d = new Date(newEmp.employment_date!); d.setMonth(d.getMonth() + parseInt(engagementMonths, 10)); const y = d.getFullYear(); const mm = String(d.getMonth() + 1).padStart(2, '0'); const dd = String(d.getDate()).padStart(2, '0'); return `${y}-${mm}-${dd}`; })() : undefined,
                                            emergency_contact_name: newEmp.emergency_contact_name || undefined,
                                            emergency_contact_phone: newEmp.emergency_contact_phone || undefined
                                        } as Omit<Employee,'id'>;
                                        const created = await hrService.createEmployee(payload);
                                        await hrService.uploadDocument({ employee_id: created.id, document_type: 'ID', document_name: 'National ID / Passport Number', tag: 'identity', notes: identity.id_or_passport });
                                        await hrService.uploadDocument({ employee_id: created.id, document_type: 'ID', document_name: 'KRA PIN', tag: 'identity', notes: identity.kra_pin });
                                        await hrService.uploadDocument({ employee_id: created.id, document_type: 'ID', document_name: 'NHIF Number', tag: 'identity', notes: identity.nhif });
                                        await hrService.uploadDocument({ employee_id: created.id, document_type: 'ID', document_name: 'NSSF Number', tag: 'identity', notes: identity.nssf });
                                        if (identity.passport_photo) {
                                            await hrService.uploadDocument({ employee_id: created.id, document_type: 'ID', document_name: 'Passport-size photo', tag: 'identity', file: identity.passport_photo });
                                        }
                                        if (docQueue.length > 0) {
                                            const uploads = await Promise.all(docQueue.map(async dq => {
                                                const createdDoc = await hrService.uploadDocument({
                                                    employee_id: created.id,
                                                    document_type: dq.document_type,
                                                    document_name: dq.document_name,
                                                    file: dq.file,
                                                    tag: dq.tag,
                                                    issue_date: dq.issue_date,
                                                    expiry_date: dq.expiry_date
                                                });
                                                return createdDoc;
                                            }));
                                            console.log('Uploaded documents:', uploads.length);
                                        }
                                        setDocQueue([]);
                                        setEmployees([created, ...employees]);
                                        setShowCreate(false);
                                        setNewEmp({ employee_type: 'DRIVER', status: 'ACTIVE' as any });
                                        setFirstName('');
                                        setLastName('');
                                        setEngagement('FULL_TIME');
                                        setEngagementMonths('');
                                    }} style={{ padding: '8px 12px', background: '#1890ff', color: '#fff', border: 0, borderRadius: 6, cursor: 'pointer' }}>Save</button>
                                    <button onClick={() => setShowCreate(false)} style={{ padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6, marginLeft: 8, cursor: 'pointer' }}>Cancel</button>
                                </div>
                            </div>
                        )}

                        {drafts.length > 0 && (
                            <div style={{ marginTop: 16, border: '1px solid #eee', borderRadius: 8, padding: 12, background: '#fff' }}>
                                <h4 style={{ marginTop: 0 }}>Draft Registrations</h4>
                                <div style={{ display: 'grid', gap: 8 }}>
                                    {drafts.map(d => (
                                        <div key={d.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid #f0f0f0', borderRadius: 6, padding: 10 }}>
                                            <div>
                                                <div style={{ fontWeight: 'bold' }}>{d.name}</div>
                                                <div style={{ fontSize: '0.9rem', color: '#666' }}>{d.department} • {d.role_title} • {d.branch}</div>
                                            </div>
                                            <div style={{ display: 'flex', gap: 8 }}>
                                                <button onClick={() => {
                                                    setShowCreate(true);
                                                    const parts = d.name.split(' ');
                                                    setFirstName(parts[0] || '');
                                                    setLastName(parts.slice(1).join(' ') || '');
                                                    setNewEmp({ ...newEmp, department: d.department, role_title: d.role_title, employee_type: roleToType(d.role_title), branch: d.branch });
                                                    const list = drafts.filter(x => x.id !== d.id);
                                                    setDrafts(list);
                                                    localStorage.setItem('hr_drafts', JSON.stringify(list));
                                                }} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer' }}>Continue registration</button>
                                                <button onClick={() => {
                                                    const list = drafts.filter(x => x.id !== d.id);
                                                    setDrafts(list);
                                                    localStorage.setItem('hr_drafts', JSON.stringify(list));
                                                }} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer' }}>Delete</button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                        
                        <h3 style={{ borderBottom: '2px solid #722ed1', paddingBottom: '10px', color: '#722ed1', marginTop: showCreate ? 16 : 0 }}>Employees</h3>
                        
                        
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
                                <thead>
                                    <tr style={{ backgroundColor: '#f9f0ff', textAlign: 'left' }}>
                                        <th style={{ padding: '12px', borderBottom: '1px solid #ddd' }}>ID</th>
                                        <th style={{ padding: '12px', borderBottom: '1px solid #ddd' }}>Name</th>
                                        <th style={{ padding: '12px', borderBottom: '1px solid #ddd' }}>Role</th>
                                        <th style={{ padding: '12px', borderBottom: '1px solid #ddd' }}>Department</th>
                                        <th style={{ padding: '12px', borderBottom: '1px solid #ddd' }}>Status</th>
                                        <th style={{ padding: '12px', borderBottom: '1px solid #ddd' }}>Contact</th>
                                        <th style={{ padding: '12px', borderBottom: '1px solid #ddd' }}>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {employees.map(emp => (
                                        <React.Fragment key={emp.id}>
                                        <tr style={{ borderBottom: '1px solid #eee' }}>
                                            <td style={{ padding: '12px' }}>{emp.employee_number}</td>
                                            <td style={{ padding: '12px', fontWeight: 'bold' }}>{emp.name}</td>
                                            <td style={{ padding: '12px' }}>{emp.role_title || emp.employee_type}</td>
                                            <td style={{ padding: '12px' }}>{emp.department || '-'}</td>
                                            <td style={{ padding: '12px' }}>
                                                <span style={{
                                                    padding: '2px 8px',
                                                    borderRadius: '12px',
                                                    fontSize: '0.8rem',
                                                    backgroundColor: emp.status === 'ACTIVE' ? '#b7eb8f' : '#f5f5f5',
                                                    color: emp.status === 'ACTIVE' ? '#135200' : '#666'
                                                }}>
                                                    {emp.status}
                                                </span>
                                            </td>
                                            <td style={{ padding: '12px' }}>{emp.phone}</td>
                                            <td style={{ padding: '12px' }}>
                                                <button onClick={() => setSelectedEmp(sel => sel?.id === emp.id ? null : emp)} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer' }}>View</button>
                                                <button onClick={() => window.print()} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer' }}>Print</button>
                                                <button onClick={() => {
                                                    const blob = new Blob([JSON.stringify(emp, null, 2)], { type: 'application/json' });
                                                    const url = URL.createObjectURL(blob);
                                                    const a = document.createElement('a');
                                                    a.href = url;
                                                    a.download = `employee_${emp.employee_number}.json`;
                                                    a.click();
                                                    URL.revokeObjectURL(url);
                                                }} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, marginLeft: 6, cursor: 'pointer' }}>Download</button>
                                            </td>
                                        </tr>
                                        {selectedEmp?.id === emp.id && (
                                            <tr>
                                                <td colSpan={7} style={{ padding: 0 }}>
                                                    <EmployeeProfilePanel emp={selectedEmp} canManage={canManageEmployee(selectedEmp)} onClose={() => setSelectedEmp(null)} />
                                                </td>
                                            </tr>
                                        )}
                                        </React.Fragment>
                                    ))}
                                    {employees.length === 0 && (
                                        <tr>
                                            <td colSpan={6} style={{ padding: '20px', textAlign: 'center', color: '#999' }}>No employees found.</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                        {/* removed global panel; now panel renders inline below selected row */}
                    </div>
                )}

                {activeTab === 'operations' && (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
                        <div>
                            <h3 style={{ borderBottom: '2px solid #faad14', paddingBottom: '10px', color: '#faad14' }}>Expiring Documents (60 days)</h3>
                            <ul style={{ listStyle: 'none', padding: 0 }}>
                                {docs.map(doc => (
                                    <li key={doc.id} style={{ padding: '12px', border: '1px solid #eee', marginBottom: '10px', borderRadius: '8px', backgroundColor: '#fffbe6' }}>
                                        <div style={{ fontWeight: 'bold' }}>{doc.document_name}</div>
                                        <div style={{ fontSize: '0.9rem', color: '#666' }}>Employee #{doc.employee_id}</div>
                                        <div style={{ fontSize: '0.85rem' }}>Expiry: {doc.expiry_date ? new Date(doc.expiry_date).toLocaleDateString() : '-'}</div>
                                    </li>
                                ))}
                                {docs.length === 0 && <p style={{ color: '#999' }}>No expiring documents.</p>}
                            </ul>
                        </div>
                        <div>
                            <h3 style={{ borderBottom: '2px solid #eb2f96', paddingBottom: '10px', color: '#eb2f96' }}>Expiring Certifications (60 days)</h3>
                            <ul style={{ listStyle: 'none', padding: 0 }}>
                                {certs.map(cert => (
                                    <li key={cert.id} style={{ padding: '12px', border: '1px solid #eee', marginBottom: '10px', borderRadius: '8px', backgroundColor: '#fff0f6' }}>
                                        <div style={{ fontWeight: 'bold' }}>{cert.certification_name}</div>
                                        <div style={{ fontSize: '0.9rem', color: '#666' }}>{cert.certification_type}</div>
                                        <div style={{ fontSize: '0.85rem' }}>Expiry: {cert.expiry_date ? new Date(cert.expiry_date).toLocaleDateString() : '-'}</div>
                                    </li>
                                ))}
                                {certs.length === 0 && <p style={{ color: '#999' }}>No expiring certifications.</p>}
                            </ul>
                        </div>
                        <div>
                            <h3 style={{ borderBottom: '2px solid #13c2c2', paddingBottom: '10px', color: '#13c2c2' }}>Alerts</h3>
                            <div style={{ display: 'grid', gap: 12 }}>
                                <AlertWidget />
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'analytics' && (
                    <div>
                        <h3 style={{ borderBottom: '2px solid #1890ff', paddingBottom: '10px', color: '#1890ff' }}>Employee Count by Type</h3>
                        <div>
                            {counts.map(c => (
                                <div key={c.employee_type} style={{ marginBottom: '12px' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <span>{c.employee_type}</span>
                                        <span style={{ fontWeight: 'bold' }}>{c.count}</span>
                                    </div>
                                    <div style={{ height: '10px', backgroundColor: '#e6f7ff', borderRadius: '6px' }}>
                                        <div style={{ width: `${Math.min(100, c.count * 5)}%`, height: '10px', backgroundColor: '#1890ff', borderRadius: '6px' }} />
                                    </div>
                                </div>
                            ))}
                            {counts.length === 0 && <p style={{ color: '#999' }}>No analytics data available.</p>}
                        </div>
                    </div>
                )}
            </div>
        </Layout>
    );
}

function AlertWidget() {
    const [contracts, setContracts] = useState<Employee[]>([]);
    const [probations, setProbations] = useState<Employee[]>([]);
    useEffect(() => {
        const load = async () => {
            const [ec, up] = await Promise.all([
                hrService.getExpiringContracts(60),
                hrService.getUpcomingProbationCompletions(30)
            ]);
            setContracts(ec);
            setProbations(up);
        };
        load();
    }, []);
    return (
        <div>
            <div style={{ marginBottom: 12 }}>
                <strong>Expiring Contracts (60 days)</strong>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                    {contracts.map(e => <li key={e.id}>{e.name} ({e.employee_number}) {e.contract_end ? new Date(e.contract_end).toLocaleDateString() : ''}</li>)}
                    {contracts.length === 0 && <li style={{ color: '#999' }}>None</li>}
                </ul>
            </div>
            <div>
                <strong>Upcoming Probation Completions (30 days)</strong>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                    {probations.map(e => <li key={e.id}>{e.name} ({e.employee_number}) {e.probation_end ? new Date(e.probation_end).toLocaleDateString() : ''}</li>)}
                    {probations.length === 0 && <li style={{ color: '#999' }}>None</li>}
                </ul>
            </div>
        </div>
    );
}

function EmployeeProfilePanel({ emp, canManage, onClose }: { emp: Employee; canManage: boolean; onClose: () => void }) {
    const [empState, setEmpState] = useState<Employee>(emp);
    const [editing, setEditing] = useState(false);
    const [editForm, setEditForm] = useState<Partial<Employee>>({
        name: emp.name,
        email: emp.email,
        phone: emp.phone,
        phone_alt: emp.phone_alt,
        address: emp.address,
        role_title: emp.role_title,
        employee_type: emp.employee_type,
        department: emp.department,
        branch: emp.branch,
        status: emp.status
    });
    const [docs, setDocs] = useState<EmployeeDocument[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [identityEdit, setIdentityEdit] = useState<{ id_or_passport?: string; kra_pin?: string; nhif?: string; nssf?: string; passport_photo?: File }>({});
    const [identityDocIds, setIdentityDocIds] = useState<{ id_or_passport?: number; kra_pin?: number; nhif?: number; nssf?: number }>({});
    const [profileDocForm, setProfileDocForm] = useState<{ document_type?: string; document_name?: string; sub_type?: string; tag?: string; issue_date?: string; expiry_date?: string; file?: File }>({});
    const [profileDocQueue, setProfileDocQueue] = useState<Array<{ document_type: string; document_name: string; tag?: string; issue_date?: string; expiry_date?: string; file: File }>>([]);
    const [docExpiryEdits, setDocExpiryEdits] = useState<Record<number, string>>({});
    const [profileResetKey, setProfileResetKey] = useState(0);
    const computeExpiryStatus = (expiry?: string, server?: 'VALID' | 'EXPIRED' | 'EXPIRING_SOON') => {
        if (!expiry) return server || 'VALID';
        const today = new Date();
        const exp = new Date(expiry);
        const diff = Math.floor((exp.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
        if (diff < 0) return 'EXPIRED';
        if (diff <= 30) return 'EXPIRING_SOON';
        return 'VALID';
    };
    useEffect(() => {
        const load = async () => {
            try {
                const data = await hrService.getDocuments(emp.id);
                setDocs(data);
                const idDoc = data.find(d => d.document_name === 'National ID / Passport Number');
                const kraDoc = data.find(d => d.document_name === 'KRA PIN');
                const nhifDoc = data.find(d => d.document_name === 'NHIF Number');
                const nssfDoc = data.find(d => d.document_name === 'NSSF Number');
                setIdentityEdit({
                    id_or_passport: idDoc?.notes || '',
                    kra_pin: kraDoc?.notes || '',
                    nhif: nhifDoc?.notes || '',
                    nssf: nssfDoc?.notes || ''
                });
                setIdentityDocIds({
                    id_or_passport: idDoc?.id,
                    kra_pin: kraDoc?.id,
                    nhif: nhifDoc?.id,
                    nssf: nssfDoc?.id
                });
            } catch (e) {
                setError('Failed to load documents');
            } finally {
                setLoading(false);
            }
        };
        load();
        setEmpState(emp);
        setEditForm({
            name: emp.name,
            email: emp.email,
            phone: emp.phone,
            phone_alt: emp.phone_alt,
            address: emp.address,
            role_title: emp.role_title,
            employee_type: emp.employee_type,
            department: emp.department,
            branch: emp.branch,
            status: emp.status
        });
    }, [emp.id, emp]);

    useEffect(() => {
        const dept = empState.department || '';
        const role = (empState.role_title || '').toLowerCase();
        const isTransportDriver = dept === 'Transport' && role.includes('driver');
        const isExpressDriver = dept === 'Express' && role.includes('driver');
        const transportReq = [
            "Valid Driver's License (BCE)",
            'Defensive Driving Certificate',
            'Medical Fitness Certificate',
            'Road Safety Training Certificate'
        ];
        const expressReq = [
            "Valid Driver's License (PSV)",
            'PSV Badge',
            'Medical Fitness Certificate',
            'Defensive Driving Certificate'
        ];
        const existing = new Set([
            ...docs.map(d => (d.document_name || '').split(' - ')[0]),
            ...profileDocQueue.map(d => (d.document_name || '').split(' - ')[0])
        ]);
        const candidates = isTransportDriver ? transportReq : isExpressDriver ? expressReq : [];
        const next = candidates.find(n => !existing.has(n));
        if (next) {
            const map: Record<string, { type: string; tag?: string }> = {
                "Valid Driver's License (BCE)": { type: 'LICENSE', tag: 'transport' },
                'Defensive Driving Certificate': { type: 'CERTIFICATE', tag: 'legal' },
                'Medical Fitness Certificate': { type: 'CERTIFICATE', tag: 'medical' },
                'Road Safety Training Certificate': { type: 'CERTIFICATE', tag: 'legal' },
                "Valid Driver's License (PSV)": { type: 'LICENSE', tag: 'express' },
                'PSV Badge': { type: 'LICENSE', tag: 'express' }
            };
            const sel = map[next];
            if (!profileDocForm.document_name || !candidates.includes(profileDocForm.document_name)) {
                setProfileDocForm({ ...profileDocForm, document_name: next, document_type: sel ? sel.type : undefined, tag: sel ? sel.tag : undefined });
            }
        }
    }, [empState.department, empState.role_title, docs, profileDocQueue]);
    return (
        <div style={{ marginTop: 16, border: '1px solid #ddd', borderRadius: 8, padding: 16, background: '#fff' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h4 style={{ margin: 0 }}>Employee Profile</h4>

                <div style={{ display: 'flex', gap: 8 }}>
                    {editing ? (
                        <>
                            <button onClick={async () => {
                                    const updated = await hrService.updateEmployee(empState.id, {
                                        name: editForm.name,
                                        email: editForm.email,
                                        phone: editForm.phone,
                                        phone_alt: editForm.phone_alt,
                                        address: editForm.address,
                                        role_title: editForm.role_title,
                                        employee_type: editForm.employee_type,
                                        department: editForm.department,
                                        branch: editForm.branch,
                                        status: editForm.status
                                    });
                                    setEmpState(updated as Employee);
                                    setEditing(false);
                                }} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer', background: '#1890ff', color: '#fff' }}>Save Details</button>
                            <button onClick={() => { setEditing(false); setEditForm({
                                    name: empState.name,
                                    email: empState.email,
                                    phone: empState.phone,
                                    phone_alt: empState.phone_alt,
                                    address: empState.address,
                                    role_title: empState.role_title,
                                    employee_type: empState.employee_type,
                                    department: empState.department,
                                    branch: empState.branch,
                                    status: empState.status
                                }); }} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer' }}>Cancel</button>
                        </>
                    ) : (
                        <button onClick={() => setEditing(true)} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer' }}>Edit Details</button>
                    )}
                    <button onClick={onClose} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer' }}>Close</button>
                </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 12, marginTop: 12 }}>
                <div><strong>Number:</strong> {empState.employee_number}</div>
                {!editing ? (
                    <>
                        <div><strong>Name:</strong> {empState.name}</div>
                        <div><strong>Role:</strong> {empState.role_title || empState.employee_type}</div>
                        <div><strong>Branch:</strong> {empState.branch || '-'}</div>
                        <div><strong>Department:</strong> {empState.department || '-'}</div>
                        <div><strong>Status:</strong> {empState.status}</div>
                        <div><strong>Employment Date:</strong> {empState.employment_date}</div>
                    </>
                ) : (
                    <>
                        <input placeholder="Name" value={editForm.name || ''} onChange={e => setEditForm({ ...editForm, name: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                        <input placeholder="Email" value={editForm.email || ''} onChange={e => setEditForm({ ...editForm, email: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                        <input placeholder="Phone" value={editForm.phone || ''} onChange={e => setEditForm({ ...editForm, phone: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                        <input placeholder="Alt Phone" value={editForm.phone_alt || ''} onChange={e => setEditForm({ ...editForm, phone_alt: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                        <input placeholder="Address" value={editForm.address || ''} onChange={e => setEditForm({ ...editForm, address: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                        <input placeholder="Role Title" value={editForm.role_title || ''} onChange={e => setEditForm({ ...editForm, role_title: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                        <input placeholder="Department" value={editForm.department || ''} onChange={e => setEditForm({ ...editForm, department: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                        <input placeholder="Branch" value={editForm.branch || ''} onChange={e => setEditForm({ ...editForm, branch: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                        <select value={editForm.status || empState.status} onChange={e => setEditForm({ ...editForm, status: e.target.value as any })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }}>
                            {['ACTIVE','ON_LEAVE','SUSPENDED','TERMINATED'].map(s => <option key={s} value={s}>{s}</option>)}
                        </select>
                    </>
                )}
            </div>
            <div style={{ marginTop: 16 }}>
                <h5 style={{ margin: '8px 0' }}>Identity & Personal</h5>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 8 }}>
                    <input placeholder="National ID / Passport Number" value={identityEdit.id_or_passport || ''} onChange={e => setIdentityEdit({ ...identityEdit, id_or_passport: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                    <input placeholder="KRA PIN" value={identityEdit.kra_pin || ''} onChange={e => setIdentityEdit({ ...identityEdit, kra_pin: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                    <input placeholder="NHIF Number" value={identityEdit.nhif || ''} onChange={e => setIdentityEdit({ ...identityEdit, nhif: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                    <input placeholder="NSSF Number" value={identityEdit.nssf || ''} onChange={e => setIdentityEdit({ ...identityEdit, nssf: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                    <div style={{ display: 'grid', gap: 6 }}>
                        <span style={{ fontSize: '0.9rem', color: '#666' }}>Passport-size Photo</span>
                        <input type="file" onChange={e => setIdentityEdit({ ...identityEdit, passport_photo: e.target.files?.[0] })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                        {(() => {
                            const photos = docs.filter(d => d.document_name === 'Passport-size photo');
                            const latest = photos
                                .filter(p => !!p.created_at)
                                .sort((a, b) => new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime())[0];
                            const label = latest?.created_at ? new Date(latest.created_at).toLocaleString() : '-';
                            return <span style={{ fontSize: '0.85rem', color: '#888' }}>Latest upload: {label}</span>;
                        })()}
                    </div>
                </div>
                <div style={{ marginTop: 12 }}>
                    <button onClick={async () => {
                        const ops: Promise<any>[] = [];
                        if (identityEdit.id_or_passport !== undefined) {
                            const id = identityDocIds.id_or_passport;
                            if (id) ops.push(hrService.updateDocument(id, { notes: identityEdit.id_or_passport }));
                            else ops.push(hrService.uploadDocument({ employee_id: empState.id, document_type: 'ID', document_name: 'National ID / Passport Number', tag: 'identity', notes: identityEdit.id_or_passport }));
                        }
                        if (identityEdit.kra_pin !== undefined) {
                            const id = identityDocIds.kra_pin;
                            if (id) ops.push(hrService.updateDocument(id, { notes: identityEdit.kra_pin }));
                            else ops.push(hrService.uploadDocument({ employee_id: empState.id, document_type: 'ID', document_name: 'KRA PIN', tag: 'identity', notes: identityEdit.kra_pin }));
                        }
                        if (identityEdit.nhif !== undefined) {
                            const id = identityDocIds.nhif;
                            if (id) ops.push(hrService.updateDocument(id, { notes: identityEdit.nhif }));
                            else ops.push(hrService.uploadDocument({ employee_id: empState.id, document_type: 'ID', document_name: 'NHIF Number', tag: 'identity', notes: identityEdit.nhif }));
                        }
                        if (identityEdit.nssf !== undefined) {
                            const id = identityDocIds.nssf;
                            if (id) ops.push(hrService.updateDocument(id, { notes: identityEdit.nssf }));
                            else ops.push(hrService.uploadDocument({ employee_id: empState.id, document_type: 'ID', document_name: 'NSSF Number', tag: 'identity', notes: identityEdit.nssf }));
                        }
                        if (identityEdit.passport_photo) {
                            const existingPhoto = docs.find(d => d.document_name === 'Passport-size photo');
                            if (existingPhoto) {
                                ops.push(hrService.deleteDocument(existingPhoto.id));
                            }
                            ops.push(hrService.uploadDocument({ employee_id: empState.id, document_type: 'ID', document_name: 'Passport-size photo', tag: 'identity', file: identityEdit.passport_photo }));
                        }
                        const results = await Promise.all(ops);
                        const refreshed = await hrService.getDocuments(empState.id);
                        setDocs(refreshed);
                    }} style={{ padding: '8px 12px', background: '#1890ff', color: '#fff', border: 0, borderRadius: 6, cursor: 'pointer' }}>Save Identity</button>
                </div>
            </div>
            <div style={{ marginTop: 16 }}>
                <h5 style={{ margin: '8px 0' }}>Documents</h5>
                {loading ? <p>Loading documents...</p> : error ? <p style={{ color: 'red' }}>{error}</p> : (
                    <div style={{ display: 'grid', gap: 8 }}>
                        {docs.map(d => (
                            <div key={d.id} style={{ border: '1px solid #eee', borderRadius: 6, padding: 10, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div>
                                    <div style={{ fontWeight: 'bold' }}>{d.document_name}</div>
                                    <div style={{ fontSize: '0.9rem', color: '#666' }}>{d.document_type} {d.tag ? `• ${d.tag}` : ''}</div>
                                    <div style={{ fontSize: '0.85rem', color: '#666' }}>Expiry {d.expiry_date ? d.expiry_date : '-'}</div>
                                    <div style={{ marginTop: 4 }}>
                                        {(() => {
                                            const s = computeExpiryStatus(d.expiry_date, d.status);
                                            const bg = s === 'EXPIRED' ? '#ffccc7' : s === 'EXPIRING_SOON' ? '#ffe58f' : '#b7eb8f';
                                            const fg = s === 'EXPIRED' ? '#a8071a' : s === 'EXPIRING_SOON' ? '#614700' : '#135200';
                                            return <span style={{ padding: '2px 8px', borderRadius: 12, fontSize: '0.75rem', backgroundColor: bg, color: fg }}>{s}</span>;
                                        })()}
                                    </div>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                        <input type="checkbox" disabled={!canManage} checked={!!d.verified} onChange={async (e) => {
                                            const updated = await hrService.updateDocument(d.id, { verified: e.target.checked });
                                            setDocs(documents => documents.map(x => x.id === d.id ? { ...x, verified: updated.verified } : x));
                                        }} />
                                        Verified
                                    </label>
                                    <input type="date" disabled={!canManage} value={docExpiryEdits[d.id] ?? (d.expiry_date || '')} onChange={e => setDocExpiryEdits({ ...docExpiryEdits, [d.id]: e.target.value })} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6 }} />
                                    <button disabled={!canManage} onClick={async () => {
                                        const val = docExpiryEdits[d.id];
                                        if (!val) return;
                                        const updated = await hrService.updateDocument(d.id, { expiry_date: val });
                                        const refreshed = await hrService.getDocuments(empState.id);
                                        setDocs(refreshed);
                                    }} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer' }}>Save Expiry</button>
                                    <button disabled={!canManage} onClick={async () => {
                                        const approver = prompt('Enter approver name');
                                        if (!approver) return;
                                        const updated = await hrService.updateDocument(d.id, { approved_by: approver });
                                        setDocs(documents => documents.map(x => x.id === d.id ? { ...x, approved_by: updated.approved_by } : x));
                                    }} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer' }}>Approve</button>
                                    <button disabled={!canManage} onClick={async () => {
                                        const confirmDelete = window.confirm('Delete this document?');
                                        if (!confirmDelete) return;
                                        await hrService.deleteDocument(d.id);
                                        const refreshed = await hrService.getDocuments(empState.id);
                                        setDocs(refreshed);
                                    }} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer' }}>Delete</button>
                                </div>
                            </div>
                        ))}
                        {docs.length === 0 && <p style={{ color: '#999' }}>No documents.</p>}
                    </div>
                )}
            </div>
            <div style={{ marginTop: 16 }}>
                <h5 style={{ margin: '8px 0' }}>Upload Documents</h5>
                <h6 style={{ margin: '8px 0' }}>Universal</h6>
                <div key={profileResetKey} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 8 }}>
                    <select value={profileDocForm.document_name || ''} onChange={e => {
                        const name = e.target.value;
                        const baseName = name.split(' - ')[0];
                        const subtype = name.includes(' - ') ? name.split(' - ')[1] : undefined;
                        const map: Record<string, { type: string; tag?: string }> = {
                            "Signed Employment Contract": { type: 'CONTRACT', tag: 'legal' },
                            "Job Offer Letter": { type: 'CONTRACT', tag: 'legal' },
                            "Letter of Acceptance": { type: 'CONTRACT', tag: 'legal' },
                            "Employee Personal Data Form": { type: 'OTHER', tag: 'personal' },
                            "CV / Résumé": { type: 'OTHER', tag: 'personal' },
                            "Academic Certificate": { type: 'CERTIFICATE', tag: 'legal' },
                            "Good Conduct Certificate": { type: 'CERTIFICATE', tag: 'legal' },
                            "Referee Letter": { type: 'OTHER', tag: 'personal' },
                            "Signed Company Policies": { type: 'OTHER', tag: 'legal' }
                        };
                        const sel = map[baseName] || map[name];
                        setProfileDocForm({ ...profileDocForm, document_name: baseName, sub_type: subtype, document_type: sel ? sel.type : undefined, tag: sel ? sel.tag : undefined });
                    }} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }}>
                        <option value="">Select Document</option>
                        {(() => {
                            const universal = [
                                "Signed Employment Contract",
                                "Job Offer Letter",
                                "Letter of Acceptance",
                                "Employee Personal Data Form",
                                "CV / Résumé",
                                "Academic Certificate",
                                "Academic Certificate - Degree",
                                "Academic Certificate - Diploma",
                                "Academic Certificate - KCSE",
                                "Good Conduct Certificate",
                                "Referee Letter",
                                "Signed Company Policies"
                            ];
                            return universal.map(n => <option key={n} value={n}>{n}</option>);
                        })()}
                    </select>
                    <input placeholder="Tag (legal/personal/medical)" value={profileDocForm.tag || ''} onChange={e => setProfileDocForm({ ...profileDocForm, tag: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                    <input type="date" placeholder="Issue date" value={profileDocForm.issue_date || ''} onChange={e => setProfileDocForm({ ...profileDocForm, issue_date: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                    <input type="date" placeholder="Expiry date" value={profileDocForm.expiry_date || ''} onChange={e => setProfileDocForm({ ...profileDocForm, expiry_date: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                    {profileDocForm.document_name === 'Academic Certificate' && (
                        <input placeholder="Sub-type (Diploma/Degree/etc)" value={profileDocForm.sub_type || ''} onChange={e => setProfileDocForm({ ...profileDocForm, sub_type: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                    )}
                    <input type="file" onChange={e => {
                        const f = e.target.files?.[0];
                        if (f) setProfileDocForm({ ...profileDocForm, file: f });
                    }} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                    <button onClick={() => {
                        if (!profileDocForm.document_type || !profileDocForm.document_name || !profileDocForm.file) return alert('Fill type, name, and select file');
                        const nameWithSubtype = profileDocForm.sub_type ? `${profileDocForm.document_name} - ${profileDocForm.sub_type}` : profileDocForm.document_name;
                        const item = {
                            document_type: profileDocForm.document_type,
                            document_name: nameWithSubtype,
                            tag: profileDocForm.tag,
                            issue_date: profileDocForm.issue_date,
                            expiry_date: profileDocForm.expiry_date,
                            file: profileDocForm.file!
                        };
                        setProfileDocQueue([item, ...profileDocQueue]);
                        setProfileDocForm({});
                        setProfileResetKey(k => k + 1);
                    }} style={{ padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer', background: '#fff' }}>Add to Queue</button>
                    <div style={{ fontSize: '0.85rem', color: '#666' }}>Add multiple documents by repeating “Add to Queue”.</div>
                </div>
                {(() => {
                    const dept = empState.department || '';
                    const role = (empState.role_title || '').toLowerCase();
                    const isTransportDriver = dept === 'Transport' && role.includes('driver');
                    const isExpressDriver = dept === 'Express' && role.includes('driver');
                    if (!isTransportDriver && !isExpressDriver) return null;
                    return (
                        <div style={{ marginTop: 12 }}>
                            <h6 style={{ margin: '8px 0' }}>Department-Specific</h6>
                            <div key={profileResetKey} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 8 }}>
                                <select value={profileDocForm.document_name || ''} onChange={e => {
                                    const name = e.target.value;
                                    const map: Record<string, { type: string; tag?: string }> = {
                                        "Valid Driver's License (BCE)": { type: 'LICENSE', tag: 'transport' },
                                        "Defensive Driving Certificate": { type: 'CERTIFICATE', tag: 'legal' },
                                        "Medical Fitness Certificate": { type: 'CERTIFICATE', tag: 'medical' },
                                        "Road Safety Training Certificate": { type: 'CERTIFICATE', tag: 'legal' },
                                        "Valid Driver's License (PSV)": { type: 'LICENSE', tag: 'express' },
                                        "PSV Badge": { type: 'LICENSE', tag: 'express' }
                                    };
                                    const sel = map[name];
                                    setProfileDocForm({ ...profileDocForm, document_name: name, document_type: sel ? sel.type : undefined, tag: sel ? sel.tag : undefined });
                                }} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }}>
                                    <option value="">Select Document</option>
                                    {(() => {
                                        const taken = new Set([
                                            ...docs.map(d => d.document_name),
                                            ...profileDocQueue.map(d => d.document_name)
                                        ]);
                                        const base = isTransportDriver ? [
                                            "Valid Driver's License (BCE)",
                                            "Defensive Driving Certificate",
                                            "Medical Fitness Certificate",
                                            "Road Safety Training Certificate"
                                        ] : isExpressDriver ? [
                                            "Valid Driver's License (PSV)",
                                            "PSV Badge",
                                            "Medical Fitness Certificate",
                                            "Defensive Driving Certificate"
                                        ] : [];
                                        const options = base.filter(n => !taken.has(n));
                                        return options.map(n => <option key={n} value={n}>{n}</option>);
                                    })()}
                                </select>
                                <input placeholder="Tag (legal/personal/medical)" value={profileDocForm.tag || ''} onChange={e => setProfileDocForm({ ...profileDocForm, tag: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                <input type="date" placeholder="Issue date" value={profileDocForm.issue_date || ''} onChange={e => setProfileDocForm({ ...profileDocForm, issue_date: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                <input type="date" placeholder="Expiry date" value={profileDocForm.expiry_date || ''} onChange={e => setProfileDocForm({ ...profileDocForm, expiry_date: e.target.value })} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                <input type="file" onChange={e => {
                                    const f = e.target.files?.[0];
                                    if (f) setProfileDocForm({ ...profileDocForm, file: f });
                                }} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 6 }} />
                                <button onClick={() => {
                                    if (!profileDocForm.document_type || !profileDocForm.document_name || !profileDocForm.file) return alert('Fill type, name, and select file');
                                    const item = {
                                        document_type: profileDocForm.document_type,
                                        document_name: profileDocForm.document_name,
                                        tag: profileDocForm.tag,
                                        issue_date: profileDocForm.issue_date,
                                        expiry_date: profileDocForm.expiry_date,
                                        file: profileDocForm.file!
                                    };
                                    setProfileDocQueue([item, ...profileDocQueue]);
                                    setProfileDocForm({});
                                    setProfileResetKey(k => k + 1);
                                }} style={{ padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer', background: '#fff' }}>Add to Queue</button>
                            </div>
                        </div>
                    );
                })()}
                {profileDocQueue.length > 0 && (
                    <div style={{ marginTop: 8 }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ backgroundColor: '#f5f5f5', textAlign: 'left' }}>
                                    <th style={{ padding: 8, borderBottom: '1px solid #ddd' }}>Type</th>
                                    <th style={{ padding: 8, borderBottom: '1px solid #ddd' }}>Name</th>
                                    <th style={{ padding: 8, borderBottom: '1px solid #ddd' }}>Tag</th>
                                    <th style={{ padding: 8, borderBottom: '1px solid #ddd' }}>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {profileDocQueue.map((d, idx) => (
                                    <tr key={idx} style={{ borderBottom: '1px solid #eee' }}>
                                        <td style={{ padding: 8 }}>{d.document_type}</td>
                                        <td style={{ padding: 8 }}>{d.document_name}</td>
                                        <td style={{ padding: 8 }}>{d.tag || '-'}</td>
                                        <td style={{ padding: 8 }}>
                                            <button onClick={() => setProfileDocQueue(profileDocQueue.filter((_, i) => i !== idx))} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer' }}>Remove</button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {(() => {
                            const legalNames = [
                                'Signed Employment Contract',
                                'Job Offer Letter',
                                'Letter of Acceptance',
                                'Employee Personal Data Form',
                                'CV / Résumé',
                                'Academic Certificate',
                                'Good Conduct Certificate',
                                'Referee Letter',
                                'Signed Company Policies'
                            ];
                            const legalCount = profileDocQueue.filter(d => legalNames.includes((d.document_name || '').split(' - ')[0])).length;
                            const color = legalCount >= 4 ? '#135200' : '#a8071a';
                            const dept = empState.department || '';
                            const role = (empState.role_title || '').toLowerCase();
                            const transportReq = ["Valid Driver's License (BCE)", 'Defensive Driving Certificate', 'Medical Fitness Certificate', 'Road Safety Training Certificate'];
                            const expressReq = ["Valid Driver's License (PSV)", 'PSV Badge', 'Medical Fitness Certificate', 'Defensive Driving Certificate'];
                            const missingTransport = transportReq.filter(r => !profileDocQueue.some(d => (d.document_name || '').startsWith(r)));
                            const missingExpress = expressReq.filter(r => !profileDocQueue.some(d => (d.document_name || '').startsWith(r)));
                            return (
                                <div style={{ marginTop: 12, display: 'grid', gap: 8 }}>
                                    <div>
                                        <strong>Legal documents queued:</strong> <span style={{ color }}>{legalCount}/4</span>
                                    </div>
                                    {dept === 'Transport' && role.includes('driver') && (
                                        <div>
                                            <strong>Transport driver requirements missing:</strong> {missingTransport.length === 0 ? 'None' : missingTransport.join(', ')}
                                        </div>
                                    )}
                                    {dept === 'Express' && role.includes('driver') && (
                                        <div>
                                            <strong>Express driver requirements missing:</strong> {missingExpress.length === 0 ? 'None' : missingExpress.join(', ')}
                                        </div>
                                    )}
                                </div>
                            );
                        })()}
                    </div>
                )}
                <div style={{ marginTop: 12 }}>
                    <button disabled={!canManage} onClick={async () => {
                        if (profileDocQueue.length === 0) return alert('Add documents to queue first');
                        const uploads = await Promise.all(profileDocQueue.map(async dq => {
                            const base = (dq.document_name || '').split(' - ')[0];
                            if (base && base !== 'Academic Certificate') {
                                const existing = docs.find(x => (x.document_name || '').split(' - ')[0] === base);
                                if (existing) {
                                    await hrService.deleteDocument(existing.id);
                                }
                            }
                            const createdDoc = await hrService.uploadDocument({
                                employee_id: empState.id,
                                document_type: dq.document_type,
                                document_name: dq.document_name,
                                file: dq.file,
                                tag: dq.tag,
                                issue_date: dq.issue_date,
                                expiry_date: dq.expiry_date
                            });
                            return createdDoc;
                        }));
                        const refreshed = await hrService.getDocuments(empState.id);
                        setDocs(refreshed);
                        setProfileDocQueue([]);
                    }} style={{ padding: '8px 12px', background: '#722ed1', color: '#fff', border: 0, borderRadius: 6, cursor: 'pointer' }}>Upload</button>
                </div>
            </div>
        </div>
    );
}
