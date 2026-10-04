import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth, API_BASE } from '../context/AuthContext';
import { ShieldCheck, CheckCircle2, XCircle, Loader, Store } from 'lucide-react';
import styles from './Compare.module.css'; // reuse existing card/button styles

export default function AdminPanel() {
  const { token } = useAuth();
  const [pending, setPending] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actioning, setActioning] = useState(null);

  const fetchPending = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/admin/pending-sellers`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPending(res.data.pending);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPending(); }, []); // eslint-disable-line

  const handleAction = async (id, action) => {
    setActioning(id);
    try {
      await axios.post(`${API_BASE}/admin/${action}/${id}`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPending(p => p.filter(s => s.id !== id));
    } catch (err) {
      console.error(err);
      alert('Action failed.');
    } finally {
      setActioning(null);
    }
  };

  return (
    <div className={styles.page}>
      <div className={`${styles.header} fade-up`}>
        <div>
          <h1 className={styles.title}><ShieldCheck size={22} /> Seller Verification</h1>
          <p className={styles.subtitle}>
            Review and approve seller/producer sign-ups before they gain access to
            seller-only features. Buyer accounts don't require this step.
          </p>
        </div>
      </div>

      <div className={`${styles.resultsCard} fade-up fade-up-1`}>
        {loading ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-muted)' }}>
            <Loader size={16} className={styles.spin} /> Loading pending accounts...
          </div>
        ) : pending.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '20px 0' }}>
            No pending seller accounts right now.
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {pending.map(s => (
              <div key={s.id} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                gap: 16, padding: '16px 18px', background: 'var(--bg-surface)',
                border: '1px solid var(--border)', borderRadius: 12, flexWrap: 'wrap',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{
                    width: 40, height: 40, borderRadius: '50%', background: 'rgba(201,168,76,0.12)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--gold)',
                  }}>
                    <Store size={18} />
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, color: 'var(--text)', fontSize: '0.92rem' }}>{s.name}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{s.company_name || '—'} · {s.email}</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Applied: {s.created_at}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button
                    onClick={() => handleAction(s.id, 'approve')}
                    disabled={actioning === s.id}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 6, background: '#3ECF8E',
                      color: '#0F0A0C', border: 'none', padding: '8px 14px', borderRadius: 8,
                      fontWeight: 700, fontSize: '0.82rem', cursor: 'pointer',
                    }}
                  >
                    <CheckCircle2 size={15} /> Approve
                  </button>
                  <button
                    onClick={() => handleAction(s.id, 'reject')}
                    disabled={actioning === s.id}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 6, background: 'transparent',
                      color: '#E05C6A', border: '1px solid #E05C6A', padding: '8px 14px', borderRadius: 8,
                      fontWeight: 700, fontSize: '0.82rem', cursor: 'pointer',
                    }}
                  >
                    <XCircle size={15} /> Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
