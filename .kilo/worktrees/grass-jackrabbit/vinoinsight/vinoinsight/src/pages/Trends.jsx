import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { useAuth, API_BASE } from '../context/AuthContext';
import styles from './Trends.module.css';

const tooltipStyle = {
  contentStyle: {
    background: 'var(--bg-surface)',
    border: '1px solid var(--border)',
    borderRadius: 8,
    fontSize: '0.82rem',
    color: 'var(--text)',
  },
  labelStyle: { color: 'var(--text-muted)' },
};

export default function Trends() {
  const { token } = useAuth();
  const [activeMetric, setActiveMetric] = useState('quality');
  const [trendData, setTrendData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get(`${API_BASE}/predictions/trends`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!cancelled) {
          setTrendData(res.data.trends.map(t => ({
            date: t.date,
            avgQuality: t.avg_quality,
            avgAlcohol: t.avg_alcohol,
            samples: t.samples,
          })));
        }
      } catch (err) {
        console.error('Failed to load trends:', err);
        if (!cancelled) setError('Could not load trend data. Make sure the backend server is running.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    if (token) load();
    return () => { cancelled = true; };
  }, [token]);

  const hasData = trendData.length > 0;

  return (
    <div className={styles.page}>
      <div className={`${styles.header} fade-up`}>
        <div>
          <h1 className={styles.title}>Trend Analysis</h1>
          <p className={styles.subtitle}>
            Quality and chemical trends across your own prediction history
          </p>
        </div>
        <div className={styles.tabs}>
          {['quality', 'alcohol'].map(m => (
            <button
              key={m}
              className={`${styles.tab} ${activeMetric === m ? styles.tabActive : ''}`}
              onClick={() => setActiveMetric(m)}
            >
              {m.charAt(0).toUpperCase() + m.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <p style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginTop: -18 }}>
        These charts are built from the predictions you've actually run, grouped by the date each
        prediction was made — not by wine vintage year, since the underlying model has no vintage/year
        input to draw a true "year-based" trend from. Price range is a category (e.g. "Standard
        £10–£20"), not a number, so it isn't charted as a trend line here.
      </p>

      {loading ? (
        <div className={styles.chartCard}><p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Loading your trend data...</p></div>
      ) : error ? (
        <div className={styles.chartCard}><p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{error}</p></div>
      ) : !hasData ? (
        <div className={styles.chartCard}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            No predictions yet — run a few analyses on the Predict page, and trends across them will appear here.
          </p>
        </div>
      ) : (
        <>
          {/* Main trend chart */}
          <div className={`${styles.chartCard} fade-up fade-up-1`}>
            <h3 className={styles.chartTitle}>
              {activeMetric === 'quality' && 'Average Quality Score by Date'}
              {activeMetric === 'alcohol' && 'Average Alcohol Content (%) by Date'}
            </h3>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={trendData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(201,168,76,0.08)" />
                <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} axisLine={{ stroke: 'var(--border)' }} tickLine={false} />
                <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip {...tooltipStyle} />
                <Line
                  type="monotone"
                  dataKey={activeMetric === 'quality' ? 'avgQuality' : 'avgAlcohol'}
                  stroke="var(--gold)"
                  strokeWidth={2.5}
                  dot={{ fill: 'var(--gold)', r: 4, strokeWidth: 0 }}
                  activeDot={{ r: 6, fill: 'var(--gold-light)' }}
                  connectNulls
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Two smaller charts */}
          <div className={`${styles.chartRow} fade-up fade-up-2`}>
            <div className={styles.chartCard}>
              <h3 className={styles.chartTitle}>Samples Analysed per Day</h3>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={trendData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(201,168,76,0.08)" />
                  <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={{ stroke: 'var(--border)' }} tickLine={false} />
                  <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} allowDecimals={false} />
                  <Tooltip {...tooltipStyle} />
                  <Bar dataKey="samples" fill="var(--wine-light)" radius={[4, 4, 0, 0]} fillOpacity={0.85} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className={styles.chartCard}>
              <h3 className={styles.chartTitle}>Quality vs Alcohol Content</h3>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={trendData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(201,168,76,0.08)" />
                  <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={{ stroke: 'var(--border)' }} tickLine={false} />
                  <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip {...tooltipStyle} />
                  <Legend wrapperStyle={{ fontSize: '0.78rem', color: 'var(--text-muted)' }} />
                  <Line type="monotone" dataKey="avgQuality" name="Avg Quality" stroke="var(--gold)" strokeWidth={2} dot={false} connectNulls />
                  <Line type="monotone" dataKey="avgAlcohol" name="Avg Alcohol %" stroke="var(--wine-light)" strokeWidth={2} dot={false} strokeDasharray="4 4" connectNulls />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
