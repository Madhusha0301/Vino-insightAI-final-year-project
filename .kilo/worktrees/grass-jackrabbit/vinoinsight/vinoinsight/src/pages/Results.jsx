import React, { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ResponsiveContainer, Cell
} from 'recharts';
import {
  Star, DollarSign, Grape, Users, Wind,
  Lightbulb, ArrowLeft, Download, UtensilsCrossed, Loader, Lock
} from 'lucide-react';
import { generateLabReportPDF } from '../utils/pdfReport';
import { useAuth } from '../context/AuthContext';
import styles from './Results.module.css';
import WineBottle3D from '../components/WineBottle3D';

// Mock fallback result
const MOCK = {
  quality_score: 7.2,
  quality_range: 'Medium-High',
  price_range: '£18–£25',
  aroma_profile: 'Fruity & Floral',
  consumer_segment: 'Wine Enthusiasts',
  shap_values: {
    alcohol: 0.42, sulphates: 0.28, volatile_acidity: -0.35,
    citric_acid: 0.18, fixed_acidity: 0.12, residual_sugar: -0.08,
    ph: -0.06, chlorides: -0.05, density: -0.04,
    free_sulfur: 0.03, total_sulfur: -0.02
  },
  // Mirrors the real /api/predict response's shap_values_by_output field
  // (project audit, Task 5) so this mock fallback still exercises the
  // per-output SHAP tab selector when no real backend result is available.
  shap_values_by_output: {
    quality_score: {
      alcohol: 0.42, sulphates: 0.28, volatile_acidity: -0.35,
      citric_acid: 0.18, fixed_acidity: 0.12, residual_sugar: -0.08,
      ph: -0.06, chlorides: -0.05, density: -0.04,
      free_sulfur: 0.03, total_sulfur: -0.02
    },
    quality_range: {
      alcohol: 0.31, sulphates: 0.19, volatile_acidity: -0.22,
      citric_acid: 0.09, fixed_acidity: 0.05, residual_sugar: -0.03,
    },
    price_range: {
      alcohol: 0.55, sulphates: 0.33, volatile_acidity: -0.11,
      citric_acid: 0.04, fixed_acidity: 0.02,
    },
    aroma_profile: {
      citric_acid: 0.61, residual_sugar: 0.48, volatile_acidity: -0.39, alcohol: 0.35,
    },
    consumer_segment: {
      alcohol: 0.14, sulphates: 0.10, density: 0.06, fixed_acidity: 0.03,
    },
  },
  recommendations: [
    'Reduce volatile acidity below 0.60 g/dm³ to improve overall taste quality.',
    'Increase sulphates to 0.65–0.75 g/dm³ to enhance preservation and flavour.',
    'Consider increasing alcohol content slightly to 10.0–10.5% for better body.',
  ]
};

const SHAP_OUTPUT_LABELS = {
  quality_score: 'Quality Score',
  quality_range: 'Quality Range',
  price_range: 'Price Range',
  aroma_profile: 'Aroma Profile',
  consumer_segment: 'Consumer Segment',
};

const outputCards = (r) => [
  { label: 'Quality Score',    value: r.quality_score,    icon: Star,        color: '#C9A84C', sub: 'out of 10' },
  { label: 'Quality Range',    value: r.quality_range,    icon: Grape,       color: '#C0394F', sub: 'classification' },
  { label: 'Price Range',      value: r.price_range,      icon: DollarSign,  color: '#3ECF8E', sub: 'estimated' },
  { label: 'Aroma Profile',    value: r.aroma_profile,    icon: Wind,        color: '#A78BFA', sub: 'descriptor' },
  { label: 'Consumer Segment', value: r.consumer_segment, icon: Users,       color: '#7B9EFF', sub: 'target audience' },
];

const inputLabels = {
  fixed_acidity: 'Fixed Acidity', volatile_acidity: 'Volatile Acidity',
  citric_acid: 'Citric Acid', residual_sugar: 'Residual Sugar',
  chlorides: 'Chlorides', free_sulfur_dioxide: 'Free Sulfur Dioxide',
  total_sulfur_dioxide: 'Total Sulfur Dioxide', density: 'Density',
  ph: 'pH', sulphates: 'Sulphates', alcohol: 'Alcohol',
};

// Food pairing suggestions derived from the predicted aroma profile —
// a rule-based, literature-informed addition (classic pairing principles:
// acidity cuts richness, tannin/body pairs with protein, sweetness balances spice).
const FOOD_PAIRINGS = {
  'Sweet & Fruity':     ['Spicy Asian cuisine', 'Soft cheeses (brie, camembert)', 'Fruit-based desserts'],
  'Sharp & Earthy':     ['Grilled red meats', 'Mushroom dishes', 'Aged hard cheeses'],
  'Full-Bodied & Warm': ['Roasted lamb or beef', 'Rich pasta (bolognese)', 'Dark chocolate'],
  'Crisp & Fresh':      ['Seafood & shellfish', 'Light salads', 'Goat cheese'],
  'Balanced & Floral':  ['Roast chicken', 'Creamy pasta', 'Mild curries'],
};

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const v = payload[0].value;
  return (
    <div style={{ background:'var(--bg-surface)', border:'1px solid var(--border)',
                  borderRadius:8, padding:'8px 12px', fontSize:'0.82rem' }}>
      <p style={{ color: v >= 0 ? '#3ECF8E' : '#E05C6A', fontWeight:600 }}>
        {v >= 0 ? '+' : ''}{v.toFixed(3)}
      </p>
      <p style={{ color:'var(--text-muted)', marginTop:2 }}>
        {v >= 0 ? 'Positive influence' : 'Negative influence'}
      </p>
    </div>
  );
};

export default function Results() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const raw = sessionStorage.getItem('vino_result');
  const result = raw ? JSON.parse(raw) : MOCK;
  const reportRef = useRef(null);
  const [exporting, setExporting] = useState(false);

  // Seller-specific insights (recommendations, consumer segment) are locked
  // until an admin approves the seller account. Buyers and approved sellers
  // are unaffected.
  const isPendingSeller = user?.role === 'seller' && user?.status === 'pending';

  // shap_values_by_output (project audit, Task 5) gives a local SHAP
  // explanation for all 5 outputs, not just Quality Score. Older cached
  // results (or the MOCK fallback) may only have the original flat
  // `shap_values` field for Quality Score — fall back to that so this page
  // still works with either shape of response.
  const shapByOutput = result.shap_values_by_output || { quality_score: result.shap_values };
  const availableShapOutputs = Object.keys(shapByOutput).filter(k => SHAP_OUTPUT_LABELS[k]);
  const [activeShapOutput, setActiveShapOutput] = useState(
    availableShapOutputs.includes('quality_score') ? 'quality_score' : availableShapOutputs[0]
  );

  const shapData = Object.entries(shapByOutput[activeShapOutput] || result.shap_values)
    .filter(([key]) => key !== 'is_red')
    .map(([key, value]) => ({
      feature: key.replace(/_/g, ' '),
      value: parseFloat(value.toFixed(3)),
    }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value));

  const foodPairings = FOOD_PAIRINGS[result.aroma_profile] || FOOD_PAIRINGS['Balanced & Floral'];

  const handleExportPDF = async () => {
    setExporting(true);
    try {
      generateLabReportPDF(result);
    } catch (err) {
      console.error('PDF export failed:', err);
      alert('Could not generate PDF. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className={styles.page} ref={reportRef}>
      {/* Header */}
      <div className={`${styles.header} fade-up`}>
        <div>
          <button className={styles.backBtn} onClick={() => navigate('/dashboard/predict')}>
            <ArrowLeft size={15} /> Back to Predict
          </button>
          <h1 className={styles.title}>Prediction Results</h1>
          <p className={styles.subtitle}>AI analysis complete — 5 outputs generated</p>
        </div>
        <button className={styles.downloadBtn} onClick={handleExportPDF} disabled={exporting}>
          {exporting ? <><Loader size={15} className={styles.spin} /> Generating...</> : <><Download size={15} /> Export Report (PDF)</>}
        </button>
      </div>

      {/* Wine Profile Hero */}
      <div className={`${styles.section} fade-up`} style={{
        display: 'flex', gap: 28, alignItems: 'center', flexWrap: 'wrap',
        background: 'var(--bg-card)', border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)', padding: '28px',
      }}>
        <div style={{ width: 220, flexShrink: 0 }}>
          <WineBottle3D aroma={result.aroma_profile} height={260} />
          <p style={{ textAlign: 'center', fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: 4 }}>
            Drag to rotate 360°
          </p>
        </div>
        <div style={{ flex: 1, minWidth: 240 }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.4rem', color: 'var(--cream)', marginBottom: 6 }}>
            {result.aroma_profile || 'Wine Profile'}
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: 16 }}>
            Predicted quality {result.quality_score}/10 · {result.quality_range} · {result.price_range}
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: '8px 20px' }}>
            {result.inputs && Object.entries(result.inputs).map(([key, val]) => (
              inputLabels[key] ? (
                <div key={key} style={{ fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border)', padding: '4px 0' }}>
                  <span style={{ color: 'var(--text-dim)' }}>{inputLabels[key]}</span>
                  <span style={{ color: 'var(--text)', fontWeight: 600 }}>{val}</span>
                </div>
              ) : null
            ))}
          </div>
        </div>
      </div>

      {/* Output cards */}
      <div className={`${styles.cardsGrid} fade-up fade-up-1`}>
        {outputCards(result).map(({ label, value, icon: Icon, color, sub }) => {
          const locked = isPendingSeller && label === 'Consumer Segment';
          return (
            <div key={label} className={styles.outputCard} style={{ '--c': color, position: 'relative' }}>
              {locked ? (
                <>
                  <div className={styles.cardIcon}><Lock size={20} /></div>
                  <p className={styles.cardValue} style={{ filter: 'blur(5px)', userSelect: 'none' }}>{value}</p>
                  <p className={styles.cardLabel}>{label}</p>
                  <p className={styles.cardSub} style={{ color: 'var(--gold)' }}>Unlocks after verification</p>
                </>
              ) : (
                <>
                  <div className={styles.cardIcon}><Icon size={20} /></div>
                  <p className={styles.cardValue}>{value}</p>
                  <p className={styles.cardLabel}>{label}</p>
                  <p className={styles.cardSub}>{sub}</p>
                </>
              )}
            </div>
          );
        })}
      </div>

      {isPendingSeller && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: 10,
          background: 'rgba(201,168,76,0.1)', border: '1px solid var(--border-hover)',
          borderRadius: 12, padding: '12px 16px', color: 'var(--gold-light)', fontSize: '0.84rem',
        }}>
          <Lock size={16} />
          Consumer Segment insights and Quality Improvement Recommendations are
          locked until your seller account is verified by an admin.
        </div>
      )}

      {/* SHAP chart */}
      <div className={`${styles.section} fade-up fade-up-2`}>
        <div className={styles.sectionHead}>
          <h2 className={styles.sectionTitle}>SHAP Feature Importance</h2>
          <p className={styles.sectionSub}>
            Which chemical properties most influenced the {SHAP_OUTPUT_LABELS[activeShapOutput] || 'quality score'} prediction
          </p>
        </div>
        {availableShapOutputs.length > 1 && (
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 14 }}>
            {availableShapOutputs.map(key => (
              <button
                key={key}
                onClick={() => setActiveShapOutput(key)}
                style={{
                  padding: '6px 14px', borderRadius: 20, fontSize: '0.78rem', cursor: 'pointer',
                  border: '1px solid var(--border)',
                  background: activeShapOutput === key ? 'var(--gold)' : 'transparent',
                  color: activeShapOutput === key ? '#1a1410' : 'var(--text-muted)',
                  fontWeight: activeShapOutput === key ? 700 : 500,
                  transition: 'all 0.15s',
                }}
              >
                {SHAP_OUTPUT_LABELS[key]}
              </button>
            ))}
          </div>
        )}
        <div className={styles.chartCard}>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={shapData}
              layout="vertical"
              margin={{ top: 8, right: 24, left: 110, bottom: 8 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(201,168,76,0.08)" horizontal={false} />
              <XAxis
                type="number"
                tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                axisLine={{ stroke: 'var(--border)' }}
                tickLine={false}
              />
              <YAxis
                type="category"
                dataKey="feature"
                tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                width={105}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(201,168,76,0.05)' }} />
              <ReferenceLine x={0} stroke="var(--border)" />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {shapData.map((entry) => (
                  <Cell
                    key={entry.feature}
                    fill={entry.value >= 0 ? '#3ECF8E' : '#E05C6A'}
                    fillOpacity={0.85}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className={styles.shapLegend}>
            <span className={styles.legendPos}>■ Positive influence</span>
            <span className={styles.legendNeg}>■ Negative influence</span>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className={`${styles.section} fade-up fade-up-3`}>
        <div className={styles.sectionHead}>
          <h2 className={styles.sectionTitle}>Quality Improvement Recommendations</h2>
          <p className={styles.sectionSub}>
            Actionable suggestions to optimise wine composition
          </p>
        </div>
        <div style={{ position: 'relative' }}>
          <div
            className={styles.recoList}
            style={isPendingSeller ? { filter: 'blur(6px)', pointerEvents: 'none', userSelect: 'none' } : undefined}
          >
            {result.recommendations.map((rec, i) => (
              <div key={i} className={styles.recoCard}>
                <div className={styles.recoIcon}>
                  <Lightbulb size={16} />
                </div>
                <p className={styles.recoText}>{rec}</p>
              </div>
            ))}
          </div>
          {isPendingSeller && (
            <div style={{
              position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center', gap: 8, textAlign: 'center',
            }}>
              <Lock size={22} color="var(--gold)" />
              <p style={{ color: 'var(--gold-light)', fontSize: '0.85rem', fontWeight: 600 }}>
                Available after seller verification
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Food Pairing Suggestions */}
      <div className={`${styles.section} fade-up fade-up-3`}>
        <div className={styles.sectionHead}>
          <h2 className={styles.sectionTitle}>Food Pairing Suggestions</h2>
          <p className={styles.sectionSub}>
            Based on the predicted "{result.aroma_profile}" aroma profile
          </p>
        </div>
        <div className={styles.recoList}>
          {foodPairings.map((pair, i) => (
            <div key={i} className={styles.recoCard}>
              <div className={styles.recoIcon}>
                <UtensilsCrossed size={16} />
              </div>
              <p className={styles.recoText}>{pair}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
