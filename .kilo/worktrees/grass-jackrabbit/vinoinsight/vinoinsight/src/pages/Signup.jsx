import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Wine, Eye, EyeOff, ShoppingCart, Store, CheckCircle2 } from 'lucide-react';
import styles from './Login.module.css';

export default function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [role, setRole] = useState('buyer');
  const [form, setForm] = useState({ name: '', email: '', password: '', company_name: '' });
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    const result = await signup({ ...form, role });
    setLoading(false);
    if (result.success) {
      setSuccessMsg(result.message);
      setTimeout(() => navigate('/login'), 2200);
    } else {
      setError(result.error);
    }
  };

  if (successMsg) {
    return (
      <div className={styles.page}>
        <div className={styles.bgOrb1} />
        <div className={styles.bgOrb2} />
        <div className={styles.card} style={{ textAlign: 'center' }}>
          <CheckCircle2 size={44} color="#3ECF8E" style={{ margin: '0 auto 14px' }} />
          <h2 style={{ fontFamily: 'var(--font-display)', color: 'var(--cream)', marginBottom: 10 }}>
            Account Created
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.6 }}>{successMsg}</p>
          <p style={{ color: 'var(--text-dim)', fontSize: '0.8rem', marginTop: 14 }}>Redirecting to sign in...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.bgOrb1} />
      <div className={styles.bgOrb2} />

      <div className={styles.card}>
        <div className={styles.logoBlock}>
          <div className={styles.logoIcon}><Wine size={28} /></div>
          <h1 className={styles.logoText}>
            VinoInsight<span>AI</span>
          </h1>
          <p className={styles.tagline}>Create your account</p>
        </div>

        {/* Role selector */}
        <div style={{ display: 'flex', gap: 10, marginBottom: 18 }}>
          <button
            type="button"
            onClick={() => setRole('buyer')}
            style={{
              flex: 1, padding: '14px 10px', borderRadius: 12, cursor: 'pointer',
              border: `1.5px solid ${role === 'buyer' ? 'var(--gold)' : 'var(--border)'}`,
              background: role === 'buyer' ? 'rgba(201,168,76,0.1)' : 'transparent',
              color: role === 'buyer' ? 'var(--gold-light)' : 'var(--text-muted)',
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
            }}
          >
            <ShoppingCart size={20} />
            <span style={{ fontWeight: 700, fontSize: '0.85rem' }}>Buyer</span>
            <span style={{ fontSize: '0.68rem', textAlign: 'center', opacity: 0.8 }}>Instant access</span>
          </button>
          <button
            type="button"
            onClick={() => setRole('seller')}
            style={{
              flex: 1, padding: '14px 10px', borderRadius: 12, cursor: 'pointer',
              border: `1.5px solid ${role === 'seller' ? 'var(--gold)' : 'var(--border)'}`,
              background: role === 'seller' ? 'rgba(201,168,76,0.1)' : 'transparent',
              color: role === 'seller' ? 'var(--gold-light)' : 'var(--text-muted)',
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
            }}
          >
            <Store size={20} />
            <span style={{ fontWeight: 700, fontSize: '0.85rem' }}>Seller / Producer</span>
            <span style={{ fontSize: '0.68rem', textAlign: 'center', opacity: 0.8 }}>Requires verification</span>
          </button>
        </div>

        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.field}>
            <label className={styles.label}>Full Name</label>
            <input
              className={styles.input}
              type="text"
              placeholder="Your name"
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              required
            />
          </div>

          {role === 'seller' && (
            <div className={styles.field}>
              <label className={styles.label}>Company / Winery Name</label>
              <input
                className={styles.input}
                type="text"
                placeholder="e.g. Ravi Vineyards"
                value={form.company_name}
                onChange={e => setForm(f => ({ ...f, company_name: e.target.value }))}
                required
              />
            </div>
          )}

          <div className={styles.field}>
            <label className={styles.label}>Email address</label>
            <input
              className={styles.input}
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
              required
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Password</label>
            <div className={styles.inputWrap}>
              <input
                className={styles.input}
                type={showPw ? 'text' : 'password'}
                placeholder="At least 6 characters"
                value={form.password}
                onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                required
                minLength={6}
              />
              <button type="button" className={styles.eyeBtn} onClick={() => setShowPw(s => !s)}>
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {role === 'seller' && (
            <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', lineHeight: 1.5 }}>
              Seller accounts require admin verification before accessing seller
              features. You'll be notified once approved.
            </p>
          )}

          {error && <p className={styles.error}>{error}</p>}

          <button className={styles.submitBtn} type="submit" disabled={loading}>
            {loading ? <span className={styles.spinner} /> : 'Create Account'}
          </button>
        </form>

        <p className={styles.hint}>
          Already have an account? <Link to="/login" style={{ color: 'var(--gold)', fontWeight: 600 }}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}
