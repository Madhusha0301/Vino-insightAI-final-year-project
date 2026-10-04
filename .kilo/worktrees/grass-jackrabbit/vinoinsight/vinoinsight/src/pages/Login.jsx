import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Wine, Eye, EyeOff } from 'lucide-react';
import styles from './Login.module.css';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    const result = await login(form.email, form.password);
    setLoading(false);
    if (result.success) {
      if (result.user.role === 'seller' && result.user.status === 'pending') {
        navigate('/dashboard'); // Dashboard shows a pending-verification banner
      } else {
        navigate('/dashboard');
      }
    } else {
      setError(result.error);
    }
  };

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
          <p className={styles.tagline}>Explainable Wine Quality Intelligence</p>
        </div>

        <form className={styles.form} onSubmit={handleSubmit}>
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
                placeholder="••••••••"
                value={form.password}
                onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                required
              />
              <button
                type="button"
                className={styles.eyeBtn}
                onClick={() => setShowPw(s => !s)}
              >
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {error && <p className={styles.error}>{error}</p>}

          <button
            className={styles.submitBtn}
            type="submit"
            disabled={loading}
          >
            {loading ? <span className={styles.spinner} /> : 'Sign In'}
          </button>
        </form>

        <p className={styles.hint}>
          Don't have an account? <Link to="/signup" style={{ color: 'var(--gold)', fontWeight: 600 }}>Sign up</Link>
        </p>
        <p className={styles.hint} style={{ marginTop: 6, fontSize: '0.72rem' }}>
          Admin demo: admin@vinoinsight.ai / Admin@123
        </p>
      </div>
    </div>
  );
}
