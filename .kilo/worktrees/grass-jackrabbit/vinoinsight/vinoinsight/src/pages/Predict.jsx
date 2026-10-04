import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FlaskConical, Info, Loader } from 'lucide-react';
import axios from 'axios';
import { useAuth, API_BASE } from '../context/AuthContext';
import styles from './Predict.module.css';

const API_URL = `${API_BASE}/predict`;

// Wine style presets. The underlying model is chemistry-based (it reads
// physicochemical measurements, not a "grape variety" label), so it can
// process any wine style. These presets simply load typical starting
// chemistry for each market category — replace the values with your own
// lab measurements for an accurate prediction of that specific sample.
const WINE_STYLES = [
  {
    id: 'red', label: 'Still Red', is_red: 1,
    defaults: { fixed_acidity:'7.4', volatile_acidity:'0.70', citric_acid:'0.00', residual_sugar:'1.9', chlorides:'0.076', free_sulfur:'11', total_sulfur:'34', density:'0.9978', ph:'3.51', sulphates:'0.56', alcohol:'9.4' },
  },
  {
    id: 'white', label: 'Still White', is_red: 0,
    defaults: { fixed_acidity:'6.3', volatile_acidity:'0.30', citric_acid:'0.34', residual_sugar:'6.5', chlorides:'0.044', free_sulfur:'42', total_sulfur:'160', density:'0.9949', ph:'3.20', sulphates:'0.49', alcohol:'11.5' },
  },
  {
    id: 'rose', label: 'Rosé', is_red: 0,
    defaults: { fixed_acidity:'6.8', volatile_acidity:'0.35', citric_acid:'0.28', residual_sugar:'3.2', chlorides:'0.05', free_sulfur:'25', total_sulfur:'110', density:'0.9935', ph:'3.30', sulphates:'0.52', alcohol:'12.0' },
  },
  {
    id: 'sparkling', label: 'Sparkling', is_red: 0,
    defaults: { fixed_acidity:'7.0', volatile_acidity:'0.25', citric_acid:'0.36', residual_sugar:'8.5', chlorides:'0.04', free_sulfur:'35', total_sulfur:'130', density:'0.9940', ph:'3.15', sulphates:'0.45', alcohol:'11.0' },
  },
  {
    id: 'dessert', label: 'Dessert / Fortified', is_red: 0,
    defaults: { fixed_acidity:'6.5', volatile_acidity:'0.32', citric_acid:'0.40', residual_sugar:'22.0', chlorides:'0.05', free_sulfur:'40', total_sulfur:'170', density:'1.0010', ph:'3.35', sulphates:'0.55', alcohol:'13.5' },
  },
];

const fields = [
  { key: 'fixed_acidity',    label: 'Fixed Acidity',       unit: 'g/dm³', min: 3.8,  max: 15.9, step: 0.1, tip: 'Tartaric acid content' },
  { key: 'volatile_acidity', label: 'Volatile Acidity',    unit: 'g/dm³', min: 0.08, max: 1.58, step: 0.01, tip: 'Acetic acid — too high causes vinegar taste' },
  { key: 'citric_acid',      label: 'Citric Acid',         unit: 'g/dm³', min: 0,    max: 1.66, step: 0.01, tip: 'Adds freshness and flavour' },
  { key: 'residual_sugar',   label: 'Residual Sugar',      unit: 'g/dm³', min: 0.6,  max: 65.8, step: 0.1, tip: 'Sugar remaining after fermentation' },
  { key: 'chlorides',        label: 'Chlorides',           unit: 'g/dm³', min: 0.009,max: 0.346,step: 0.001,tip: 'Salt content of the wine' },
  { key: 'free_sulfur',      label: 'Free Sulfur Dioxide', unit: 'mg/dm³',min: 1,    max: 289,  step: 1,   tip: 'Prevents oxidation and microbial growth' },
  { key: 'total_sulfur',     label: 'Total Sulfur Dioxide',unit: 'mg/dm³',min: 6,    max: 440,  step: 1,   tip: 'Total SO₂ concentration' },
  // step was 0.001 until this fix (project audit, discovered via screenshot
  // testing for the User Manual/Reflective Report): real wine density needs
  // 4 decimal places (e.g. 0.9978, as used in this file's own "Still Red"
  // preset above and in the backend's own SAMPLE_WINE test fixture), but
  // 0.001 only allows 3. The HTML5 <input type="number"> step validation
  // silently rejected every single preset's density value and blocked form
  // submission with a native "please enter a valid value" tooltip - this
  // was a real, undiscovered bug that made the Predict form unusable with
  // its own default presets. Fixed by tightening step to 0.0001.
  { key: 'density',          label: 'Density',             unit: 'g/cm³', min: 0.987,max: 1.039,step: 0.0001,tip: 'Related to alcohol and sugar content' },
  { key: 'ph',               label: 'pH Level',            unit: '',      min: 2.72, max: 4.01, step: 0.01,tip: 'Acidity scale — lower is more acidic' },
  { key: 'sulphates',        label: 'Sulphates',           unit: 'g/dm³', min: 0.22, max: 2.0,  step: 0.01,tip: 'Wine additive for antimicrobial purposes' },
  { key: 'alcohol',          label: 'Alcohol Content',     unit: '%vol',  min: 8,    max: 14.9, step: 0.1, tip: 'Alcohol percentage by volume' },
];

export default function Predict() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [wineStyle, setWineStyle] = useState('red');
  const [form, setForm] = useState(WINE_STYLES[0].defaults);
  const [loading, setLoading] = useState(false);
  const [tooltip, setTooltip] = useState(null);

  const handleChange = (key, val) => setForm(f => ({ ...f, [key]: val }));

  const handleStyleChange = (styleId) => {
    const style = WINE_STYLES.find(s => s.id === styleId);
    setWineStyle(styleId);
    setForm(style.defaults);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Backend model was trained on 'free_sulfur_dioxide' / 'total_sulfur_dioxide'
      // (year is not used by the model — UCI dataset has no year column)
      const styleLabel = WINE_STYLES.find(s => s.id === wineStyle)?.label || 'Wine';
      const payload = {
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
        is_red: WINE_STYLES.find(s => s.id === wineStyle)?.is_red ?? 1,
        // wine_style is not a model input (it's not in FEATURES, so the
        // backend ignores it for prediction) — it's only used to label the
        // saved history record, since the backend can't infer "Rosé" vs
        // "Sparkling" from chemistry alone.
        wine_style: styleLabel,
      };

      // Sending the Authorization header (when logged in) is what lets the
      // backend save this prediction to the user's real history — see
      // predictions_db.py. Without a token, the prediction still works
      // exactly as before, it just isn't saved anywhere.
      const response = await axios.post(API_URL, payload, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      const resultWithStyle = {
        ...response.data,
        wine_style: styleLabel,
      };
      sessionStorage.setItem('vino_result', JSON.stringify(resultWithStyle));
      setLoading(false);
      navigate('/dashboard/results');
    } catch (err) {
      console.error('Prediction failed:', err);
      setLoading(false);
      alert('Prediction failed. Make sure the backend server is running on port 5000.');
    }
  };

  const handleReset = () => setForm(WINE_STYLES.find(s => s.id === wineStyle).defaults);

  return (
    <div className={styles.page}>
      <div className={`${styles.header} fade-up`}>
        <div>
          <h1 className={styles.title}>Wine Analysis</h1>
          <p className={styles.subtitle}>
            Enter the physicochemical properties of your wine sample
          </p>
        </div>
        <div className={styles.steps}>
          <span className={styles.stepActive}>1 · Input Data</span>
          <span className={styles.stepDivider}>→</span>
          <span className={styles.stepInactive}>2 · AI Analysis</span>
          <span className={styles.stepDivider}>→</span>
          <span className={styles.stepInactive}>3 · Results</span>
        </div>
      </div>

      <div className={`${styles.formCard} fade-up fade-up-1`} style={{ marginBottom: 20 }}>
        <div className={styles.formHeader}>
          <FlaskConical size={18} color="var(--gold)" />
          <span>Wine Style</span>
        </div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 10 }}>
          {WINE_STYLES.map(s => (
            <button
              key={s.id}
              type="button"
              onClick={() => handleStyleChange(s.id)}
              style={{
                padding: '9px 18px',
                borderRadius: 999,
                border: `1.5px solid ${wineStyle === s.id ? 'var(--gold)' : 'var(--border)'}`,
                background: wineStyle === s.id ? 'rgba(201,168,76,0.12)' : 'transparent',
                color: wineStyle === s.id ? 'var(--gold-light)' : 'var(--text-muted)',
                fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer',
              }}
            >
              {s.label}
            </button>
          ))}
        </div>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', lineHeight: 1.5 }}>
          The model reads physicochemical measurements, not a variety label, so it works
          across wine styles. Selecting a style loads typical starting chemistry —
          replace these with your own lab measurements for an accurate result.
        </p>
      </div>

      <form className={`${styles.formCard} fade-up fade-up-1`} onSubmit={handleSubmit}>
        <div className={styles.formHeader}>
          <FlaskConical size={18} color="var(--gold)" />
          <span>Physicochemical Properties</span>
        </div>

        <div className={styles.grid}>
          {fields.map(({ key, label, unit, min, max, step, tip }) => (
            <div key={key} className={styles.field}>
              <div className={styles.labelRow}>
                <label className={styles.label}>{label}</label>
                <button
                  type="button"
                  className={styles.tipBtn}
                  onMouseEnter={() => setTooltip(key)}
                  onMouseLeave={() => setTooltip(null)}
                >
                  <Info size={13} />
                  {tooltip === key && (
                    <span className={styles.tooltip}>{tip}</span>
                  )}
                </button>
              </div>
              <div className={styles.inputRow}>
                <input
                  className={styles.input}
                  type="number"
                  min={min} max={max} step={step}
                  value={form[key]}
                  onChange={e => handleChange(key, e.target.value)}
                  required
                />
                {unit && <span className={styles.unit}>{unit}</span>}
              </div>
            </div>
          ))}
        </div>

        <div className={styles.actions}>
          <button type="button" className={styles.resetBtn} onClick={handleReset}>
            Reset to Default
          </button>
          <button type="submit" className={styles.submitBtn} disabled={loading}>
            {loading ? (
              <><Loader size={16} className={styles.spin} /> Analysing...</>
            ) : (
              <><FlaskConical size={16} /> Run Prediction</>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
