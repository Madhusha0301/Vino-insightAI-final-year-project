import React, { useState } from 'react';
import axios from 'axios';
import {
  Scale, FlaskConical, Loader, Trophy, Star, DollarSign,
  Wind, Users, Grape
} from 'lucide-react';
import { useAuth, API_BASE } from '../context/AuthContext';
import styles from './Compare.module.css';

const API_URL = `${API_BASE}/predict`;

const fields = [
  { key: 'fixed_acidity',    label: 'Fixed Acidity' },
  { key: 'volatile_acidity', label: 'Volatile Acidity' },
  { key: 'citric_acid',      label: 'Citric Acid' },
  { key: 'residual_sugar',   label: 'Residual Sugar' },
  { key: 'chlorides',        label: 'Chlorides' },
  { key: 'free_sulfur',      label: 'Free Sulfur Dioxide' },
  { key: 'total_sulfur',     label: 'Total Sulfur Dioxide' },
  { key: 'density',          label: 'Density' },
  { key: 'ph',               label: 'pH Level' },
  { key: 'sulphates',        label: 'Sulphates' },
  { key: 'alcohol',          label: 'Alcohol %' },
];

const wineADefault = {
  fixed_acidity:'7.4', volatile_acidity:'0.70', citric_acid:'0.00',
  residual_sugar:'1.9', chlorides:'0.076', free_sulfur:'11',
  total_sulfur:'34', density:'0.9978', ph:'3.51',
  sulphates:'0.56', alcohol:'9.4', is_red: 1,
};

const wineBDefault = {
  fixed_acidity:'6.3', volatile_acidity:'0.30', citric_acid:'0.34',
  residual_sugar:'6.5', chlorides:'0.044', free_sulfur:'42',
  total_sulfur:'160', density:'0.9949', ph:'3.20',
  sulphates:'0.49', alcohol:'11.5', is_red: 0,
};

function toPayload(form) {
  return {
    fixed_acidity: parseFloat(form.fixed_acidity),
    volatile_acidity: parseFloat(form.volatile_acidity),
    citric_acid: parseFloat(form.citric_acid),
    residual_sugar: parseFloat(form.residual_sugar),
    chlorides: parseFloat(form.chlorides),
    free_sulfur_dioxide: parseFloat(form.free_sulfur),
    total_sulfur_dioxide: parseFloat(form.total_sulfur),
    density: parseFloat(form.density),
    ph: parseFloat(form.ph),
    sulphates: parseFloat(form.sulphates),
    alcohol: parseFloat(form.alcohol),
    is_red: form.is_red ?? 1,
  };
}

function WineForm({ label, form, setForm, accent }) {
  return (
    <div className={styles.formCard} style={{ '--accent': accent }}>
      <div className={styles.formHeader}>
        <FlaskConical size={16} />
        <span>{label}</span>
      </div>
      <div className={styles.grid}>
        {fields.map(({ key, label: fLabel }) => (
          <div key={key} className={styles.field}>
            <label>{fLabel}</label>
            <input
              type="number"
              step="any"
              value={form[key]}
              onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
              required
            />
          </div>
        ))}
      </div>
    </div>
  );
}

const resultRows = [
  { key: 'quality_score', label: 'Quality Score', icon: Star, higherBetter: true },
  { key: 'quality_range', label: 'Quality Range', icon: Grape, higherBetter: null },
  { key: 'price_range', label: 'Price Range', icon: DollarSign, higherBetter: null },
  { key: 'aroma_profile', label: 'Aroma Profile', icon: Wind, higherBetter: null },
  { key: 'consumer_segment', label: 'Consumer Segment', icon: Users, higherBetter: null },
];

export default function Compare() {
  const { token } = useAuth();
  const [wineA, setWineA] = useState(wineADefault);
  const [wineB, setWineB] = useState(wineBDefault);
  const [resultA, setResultA] = useState(null);
  const [resultB, setResultB] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCompare = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};
      const [resA, resB] = await Promise.all([
        axios.post(API_URL, { ...toPayload(wineA), wine_style: 'Compare: Wine A' }, { headers: authHeaders }),
        axios.post(API_URL, { ...toPayload(wineB), wine_style: 'Compare: Wine B' }, { headers: authHeaders }),
      ]);
      setResultA(resA.data);
      setResultB(resB.data);
    } catch (err) {
      console.error(err);
      setError('Comparison failed. Make sure the backend server is running on port 5000.');
    } finally {
      setLoading(false);
    }
  };

  const winner = resultA && resultB
    ? (resultA.quality_score >= resultB.quality_score ? 'A' : 'B')
    : null;

  return (
    <div className={styles.page}>
      <div className={`${styles.header} fade-up`}>
        <div>
          <h1 className={styles.title}><Scale size={22} /> Compare Wines</h1>
          <p className={styles.subtitle}>
            Enter two wine samples side-by-side to decide which one offers better value —
            useful when choosing between two bottles or evaluating supplier batches.
          </p>
        </div>
      </div>

      <form onSubmit={handleCompare} className={`${styles.formsRow} fade-up fade-up-1`}>
        <WineForm label="Wine A" form={wineA} setForm={setWineA} accent="#C0394F" />
        <WineForm label="Wine B" form={wineB} setForm={setWineB} accent="#3ECF8E" />
      </form>

      <div className={`${styles.actions} fade-up fade-up-2`}>
        <button type="button" onClick={handleCompare} className={styles.compareBtn} disabled={loading}>
          {loading ? <><Loader size={16} className={styles.spin} /> Comparing...</> : <><Scale size={16} /> Compare Now</>}
        </button>
        {error && <p className={styles.error}>{error}</p>}
      </div>

      {resultA && resultB && (
        <div className={`${styles.resultsCard} fade-up fade-up-3`}>
          {winner && (
            <div className={styles.winnerBanner}>
              <Trophy size={18} />
              <span>
                Wine {winner} has the higher predicted quality score
                ({winner === 'A' ? resultA.quality_score : resultB.quality_score}/10)
              </span>
            </div>
          )}
          <div className={styles.resultsGrid}>
            <div className={styles.colHead} style={{ color: '#C0394F' }}>Wine A</div>
            <div className={styles.colHead}>Metric</div>
            <div className={styles.colHead} style={{ color: '#3ECF8E' }}>Wine B</div>

            {resultRows.map(({ key, label, icon: Icon }) => (
              <React.Fragment key={key}>
                <div className={`${styles.cell} ${winner === 'A' && key === 'quality_score' ? styles.cellWin : ''}`}>
                  {resultA[key]}
                </div>
                <div className={styles.cellLabel}><Icon size={14} /> {label}</div>
                <div className={`${styles.cell} ${winner === 'B' && key === 'quality_score' ? styles.cellWin : ''}`}>
                  {resultB[key]}
                </div>
              </React.Fragment>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
