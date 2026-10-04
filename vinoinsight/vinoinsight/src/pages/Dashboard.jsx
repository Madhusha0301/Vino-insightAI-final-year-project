import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth, API_BASE } from '../context/AuthContext';
import {
  FlaskConical, BarChart3, TrendingUp, Lightbulb,
  ArrowRight, Star, DollarSign, Grape, Users, Scale
} from 'lucide-react';
import styles from './Dashboard.module.css';

// Builds the 4 stat cards from real, saved-prediction aggregates
// (GET /api/predictions/stats) instead of the fixed placeholder numbers
// this page used to show unconditionally.
function buildStatCards(apiStats) {
  return [
    { label: 'Total Predictions', value: String(apiStats.total_predictions ?? 0), icon: BarChart3, color: '#C9A84C' },
    { label: 'Avg Quality Score', value: apiStats.avg_quality_score != null ? String(apiStats.avg_quality_score) : '—', icon: Star, color: '#C0394F' },
    { label: 'Price Ranges Seen', value: String(apiStats.distinct_price_ranges ?? 0), icon: DollarSign, color: '#3ECF8E' },
    { label: 'Consumer Segments Seen', value: String(apiStats.distinct_consumer_segments ?? 0), icon: Users, color: '#7B9EFF' },
  ];
}

const quickActionsBuyer = [
  {
    icon: FlaskConical,
    title: 'Check a Wine',
    desc: 'Analyse a wine sample before you buy',
    to: '/dashboard/predict',
    accent: 'var(--wine-light)',
  },
  {
    icon: Scale,
    title: 'Compare Wines',
    desc: 'See two wines side by side to decide which to buy',
    to: '/dashboard/compare',
    accent: '#3ECF8E',
  },
  {
    icon: BarChart3,
    title: 'View Results',
    desc: 'See your latest prediction and food pairing suggestions',
    to: '/dashboard/results',
    accent: 'var(--gold)',
  },
  {
    icon: TrendingUp,
    title: 'Trend Analysis',
    desc: 'Explore quality trends across production years',
    to: '/dashboard/trends',
    accent: '#7B9EFF',
  },
];

const quickActionsSeller = [
  {
    icon: FlaskConical,
    title: 'New Prediction',
    desc: 'Analyse a batch using physicochemical properties',
    to: '/dashboard/predict',
    accent: 'var(--wine-light)',
  },
  {
    icon: Lightbulb,
    title: 'Quality Recommendations',
    desc: 'Get chemical adjustments to raise predicted quality',
    to: '/dashboard/results',
    accent: '#7B9EFF',
  },
  {
    icon: BarChart3,
    title: 'Price Positioning',
    desc: 'See predicted price range and consumer segment fit',
    to: '/dashboard/results',
    accent: 'var(--gold)',
  },
  {
    icon: TrendingUp,
    title: 'Trend Analysis',
    desc: 'Explore quality trends across production years',
    to: '/dashboard/trends',
    accent: '#3ECF8E',
  },
];

export default function Dashboard() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const isSeller = user?.role === 'seller' || user?.role === 'admin';
  const quickActions = isSeller ? quickActionsSeller : quickActionsBuyer;

  const [statCards, setStatCards] = useState(buildStatCards({}));
  const [recentPredictions, setRecentPredictions] = useState([]);
  const [loadingRecent, setLoadingRecent] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [statsRes, recentRes] = await Promise.all([
          axios.get(`${API_BASE}/predictions/stats`, { headers: { Authorization: `Bearer ${token}` } }),
          axios.get(`${API_BASE}/predictions?limit=4`, { headers: { Authorization: `Bearer ${token}` } }),
        ]);
        if (cancelled) return;
        setStatCards(buildStatCards(statsRes.data));
        setRecentPredictions(recentRes.data.predictions.map(p => ({
          id: p.id,
          name: p.wine_style || 'Wine Sample',
          quality: p.quality_score,
          range: p.quality_range,
          price: p.price_range,
          date: new Date(p.created_at).toLocaleDateString(),
        })));
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        if (!cancelled) setLoadingRecent(false);
      }
    }
    if (token) load();
    return () => { cancelled = true; };
  }, [token]);

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={`${styles.header} fade-up`}>
        <div>
          <h1 className={styles.title}>
            Welcome back, <span className="gold">{user?.name}</span>
          </h1>
          <p className={styles.subtitle}>
            {isSeller
              ? 'Here is an overview of your production quality and pricing insights'
              : 'Here is an overview of the wines you\'ve checked before buying'}
          </p>
        </div>
        <button
          className={styles.ctaBtn}
          onClick={() => navigate('/dashboard/predict')}
        >
          <FlaskConical size={16} />
          New Prediction
        </button>
      </div>

      {/* Stats row */}
      <div className={`${styles.statsGrid} fade-up fade-up-1`}>
        {statCards.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className={styles.statCard}>
            <div className={styles.statIcon} style={{ background: `${color}18`, color }}>
              <Icon size={20} />
            </div>
            <div>
              <p className={styles.statValue}>{value}</p>
              <p className={styles.statLabel}>{label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Quick actions */}
      <div className={`${styles.section} fade-up fade-up-2`}>
        <h2 className={styles.sectionTitle}>Quick Actions</h2>
        <div className={styles.actionsGrid}>
          {quickActions.map(({ icon: Icon, title, desc, to, accent }) => (
            <button
              key={title}
              className={styles.actionCard}
              onClick={() => navigate(to)}
              style={{ '--accent': accent }}
            >
              <div className={styles.actionIcon}>
                <Icon size={22} />
              </div>
              <div className={styles.actionText}>
                <p className={styles.actionTitle}>{title}</p>
                <p className={styles.actionDesc}>{desc}</p>
              </div>
              <ArrowRight size={16} className={styles.actionArrow} />
            </button>
          ))}
        </div>
      </div>

      {/* Recent predictions table */}
      <div className={`${styles.section} fade-up fade-up-3`}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Recent Predictions</h2>
          <button className={styles.viewAll} onClick={() => navigate('/dashboard/history')}>
            View all <ArrowRight size={14} />
          </button>
        </div>
        <div className={styles.tableWrap}>
          {loadingRecent ? (
            <p style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Loading your recent predictions...
            </p>
          ) : recentPredictions.length === 0 ? (
            <p style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              No predictions yet — run your first analysis to see it here.
            </p>
          ) : (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Sample</th>
                  <th>Quality Score</th>
                  <th>Quality Range</th>
                  <th>Price Range</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {recentPredictions.map(row => (
                  <tr key={row.id}>
                    <td className={styles.sampleName}>
                      <Grape size={14} className={styles.grapeIcon} />
                      {row.name}
                    </td>
                    <td>
                      <span className={styles.scoreChip}>{row.quality}</span>
                    </td>
                    <td>
                      <span className={`${styles.rangeBadge} ${styles[`range${row.range}`]}`}>
                        {row.range}
                      </span>
                    </td>
                    <td className={styles.price}>{row.price}</td>
                    <td className={styles.date}>{row.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
