// History.jsx
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Search, Grape, Loader } from 'lucide-react';
import { useAuth, API_BASE } from '../context/AuthContext';
import styles from './History.module.css';

// Maps a quality_range string to the CSS badge class. Falls back to
// "rMedium" styling for any value not in the known set (defensive —
// real model output should only ever be Low/Medium/High, but this keeps
// the UI from silently breaking if that ever changes).
function rangeClass(range) {
  if (range === 'High') return styles.rHigh;
  if (range === 'Low') return styles.rLow;
  return styles.rMedium;
}

export default function History() {
  const { token } = useAuth();
  const [search, setSearch] = useState('');
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API_BASE}/predictions`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setRecords(res.data.predictions);
    } catch (err) {
      console.error('Failed to load prediction history:', err);
      setError('Could not load your prediction history. Make sure the backend server is running.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  const filtered = records.filter(r =>
    (r.wine_style || '').toLowerCase().includes(search.toLowerCase()) ||
    (r.aroma_profile || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className={styles.page}>
      <div className={`${styles.header} fade-up`}>
        <div>
          <h1 className={styles.title}>Prediction History</h1>
          <p className={styles.subtitle}>Your previous wine analysis records</p>
        </div>
        <div className={styles.searchWrap}>
          <Search size={15} className={styles.searchIcon} />
          <input
            className={styles.searchInput}
            placeholder="Search samples..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className={`${styles.tableWrap} fade-up fade-up-1`}>
        {loading ? (
          <p className={styles.empty}><Loader size={14} className="spin" style={{ marginRight: 8 }} /> Loading your prediction history...</p>
        ) : error ? (
          <p className={styles.empty}>{error}</p>
        ) : (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Sample</th>
                <th>Date</th>
                <th>Quality Score</th>
                <th>Range</th>
                <th>Price Range</th>
                <th>Aroma</th>
                <th>Segment</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(row => (
                <tr key={row.id}>
                  <td className={styles.sampleCell}>
                    <Grape size={13} color="var(--wine-light)" style={{ marginRight: 8, flexShrink: 0 }} />
                    {row.wine_style || 'Wine Sample'}
                  </td>
                  <td className={styles.dim}>{new Date(row.created_at).toLocaleDateString()}</td>
                  <td>
                    <span className={styles.score}>{row.quality_score}</span>
                  </td>
                  <td>
                    <span className={`${styles.badge} ${rangeClass(row.quality_range)}`}>{row.quality_range}</span>
                  </td>
                  <td className={styles.price}>{row.price_range}</td>
                  <td className={styles.dim}>{row.aroma_profile}</td>
                  <td className={styles.dim}>{row.consumer_segment}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {!loading && !error && filtered.length === 0 && (
          <p className={styles.empty}>
            {records.length === 0
              ? 'No predictions yet — run your first analysis on the Predict page to see it here.'
              : 'No records match your search.'}
          </p>
        )}
      </div>
    </div>
  );
}
