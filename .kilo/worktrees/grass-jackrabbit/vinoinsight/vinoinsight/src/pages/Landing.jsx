import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Wine, Star, DollarSign, Grape, Users, Wind,
  FlaskConical, ArrowRight, BarChart3, Scale, Lightbulb, Menu, X
} from 'lucide-react';
import WineBottle3D from '../components/WineBottle3D';
import styles from './Landing.module.css';

const outputs = [
  { icon: Star, label: 'Quality Score', desc: 'A precise score based on the wine\'s chemical composition', color: '#A61A30' },
  { icon: Grape, label: 'Quality Range', desc: 'Low / Medium / High classification for quick decisions', color: '#8B2942' },
  { icon: DollarSign, label: 'Price Range', desc: 'An estimated market price band for the sample', color: '#2E7D5B' },
  { icon: Wind, label: 'Aroma Profile', desc: 'The wine\'s likely aromatic character and descriptors', color: '#7B5EA7' },
  { icon: Users, label: 'Consumer Segment', desc: 'The audience most likely to enjoy this wine', color: '#3F6FB5' },
];

const steps = [
  { n: '01', title: 'Enter Chemical Data', desc: 'Input physicochemical properties — acidity, pH, alcohol, sulphates and more' },
  { n: '02', title: 'AI Analysis', desc: 'The system processes the sample across five prediction targets at once' },
  { n: '03', title: 'Review Results', desc: 'See which properties most influenced each prediction' },
  { n: '04', title: 'Improve & Decide', desc: 'Get suggestions to improve quality or position pricing correctly' },
];

const styleChips = ['Red Wine Analysis', 'White Wine Analysis', 'Price Positioning', 'Aroma Prediction', 'Quality Improvement'];

const SHOWCASE_IMAGES = [
  { src: 'https://images.unsplash.com/photo-1560493676-04071c5f467b?auto=format&fit=crop&w=700&q=80', alt: 'vineyard', caption: 'Vineyard sourcing' },
  { src: 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=700&q=80', alt: 'lab-testing', caption: 'Chemical measurement' },
  { src: 'https://images.unsplash.com/photo-1558346490-a72e53ae2d4f?auto=format&fit=crop&w=700&q=80', alt: 'tasting', caption: 'Predicted profile' },
];

export default function Landing() {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = React.useState(false);

  return (
    <div className={styles.page}>
      {/* NAV */}
      <nav className={styles.nav}>
        <div className={styles.logo} onClick={() => navigate('/')}>
          <Wine size={22} color="var(--wine)" />
          <span>VinoInsight<span className={styles.logoAi}>AI</span></span>
        </div>
        <div className={styles.navLinks}>
          <button className={styles.navLink} onClick={() => document.getElementById('features').scrollIntoView({ behavior: 'smooth' })}>Features</button>
          <button className={styles.navLink} onClick={() => document.getElementById('how-it-works').scrollIntoView({ behavior: 'smooth' })}>How It Works</button>
          <button className={styles.navLink} onClick={() => document.getElementById('audience').scrollIntoView({ behavior: 'smooth' })}>For Buyers &amp; Sellers</button>
        </div>
        <div className={styles.navRight}>
          <button className={styles.navLinkBtn} onClick={() => navigate('/login')}>Sign In</button>
          <button className={styles.navCta} onClick={() => navigate('/login')}>Get Started</button>
        </div>
        <button className={styles.menuBtn} onClick={() => setMenuOpen(m => !m)}>
          {menuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </nav>
      {menuOpen && (
        <div className={styles.mobileMenu}>
          <button onClick={() => { document.getElementById('features').scrollIntoView({ behavior: 'smooth' }); setMenuOpen(false); }}>Features</button>
          <button onClick={() => { document.getElementById('how-it-works').scrollIntoView({ behavior: 'smooth' }); setMenuOpen(false); }}>How It Works</button>
          <button onClick={() => { document.getElementById('audience').scrollIntoView({ behavior: 'smooth' }); setMenuOpen(false); }}>For Buyers &amp; Sellers</button>
          <button onClick={() => navigate('/login')}>Sign In</button>
          <button className={styles.mobileCta} onClick={() => navigate('/login')}>Get Started</button>
        </div>
      )}

      {/* HERO */}
      <section className={styles.hero}>
        <div className={styles.heroContent}>
          <h1 className={styles.heroTitle}>
            Predict Wine Quality<br />From The Chemistry Up
          </h1>
          <p className={styles.heroSubtitle}>
            Enter physicochemical measurements and get quality, price range,
            aroma profile, and consumer segment predictions — with a clear
            breakdown of what drove each result.
          </p>
          <div className={styles.heroCtas}>
            <button className={styles.ctaPrimary} onClick={() => navigate('/login')}>
              Try a Prediction <ArrowRight size={16} />
            </button>
            <button className={styles.ctaSecondary} onClick={() => document.getElementById('how-it-works').scrollIntoView({ behavior: 'smooth' })}>
              See How It Works
            </button>
          </div>

          <div className={styles.chipsRow}>
            {styleChips.map(c => <span key={c} className={styles.chip}>{c}</span>)}
          </div>
        </div>

        <div className={styles.heroVisual}>
          <WineBottle3D aroma="Balanced & Floral" height={420} />
          <p className={styles.dragHint}>Drag to rotate 360°</p>
        </div>
      </section>

      {/* OUTPUTS */}
      <section id="features" className={styles.section}>
        <div className={styles.sectionHead}>
          <h2>Five Predictions From One Sample</h2>
          <p>A single set of chemical measurements produces a complete picture of the wine.</p>
        </div>
        <div className={styles.outputsGrid}>
          {outputs.map(({ icon: Icon, label, desc, color }) => (
            <div key={label} className={styles.outputCard} style={{ '--c': color }}>
              <div className={styles.outputIcon}><Icon size={22} /></div>
              <h3>{label}</h3>
              <p>{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how-it-works" className={styles.sectionAlt}>
        <div className={styles.sectionHead}>
          <h2>How It Works</h2>
          <p>From raw chemistry to a clear decision, in seconds.</p>
        </div>
        <div className={styles.stepsGrid}>
          {steps.map(({ n, title, desc }) => (
            <div key={n} className={styles.stepCard}>
              <span className={styles.stepNum}>{n}</span>
              <h3>{title}</h3>
              <p>{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* VISUAL SHOWCASE */}
      <section className={styles.sectionAlt}>
        <div className={styles.sectionHead}>
          <h2>From Vineyard To Verdict</h2>
          <p>Every prediction starts with the same raw material — the wine itself.</p>
        </div>
        <div className={styles.showcaseGrid}>
          {SHOWCASE_IMAGES.map(({ src, alt, caption }) => (
            <div key={alt} className={styles.showcaseCard}>
              <img
                src={src}
                alt={alt}
                loading="lazy"
                onError={(e) => { e.currentTarget.parentElement.classList.add(styles.showcaseFallback); }}
              />
              <span className={styles.showcaseCaption}>{caption}</span>
            </div>
          ))}
        </div>
      </section>

      {/* WHO IT'S FOR */}
      <section id="audience" className={styles.section}>
        <div className={styles.sectionHead}>
          <h2>Useful On Both Sides Of The Bottle</h2>
        </div>
        <div className={styles.audienceGrid}>
          <div className={styles.audienceCard}>
            <FlaskConical size={26} color="var(--wine)" />
            <h3>For Producers &amp; Sellers</h3>
            <ul>
              <li>Predict quality before bottling or export</li>
              <li>Get chemical-level recommendations to raise quality</li>
              <li>Position pricing accurately using predicted price range</li>
              <li>Understand which consumer segment a batch will appeal to</li>
            </ul>
          </div>
          <div className={styles.audienceCard}>
            <BarChart3 size={26} color="#2E7D5B" />
            <h3>For Buyers &amp; Retailers</h3>
            <ul>
              <li>Verify whether a wine's price matches its predicted quality</li>
              <li>Compare two or more wines side-by-side before purchasing</li>
              <li>Understand aroma profile before committing to a case order</li>
              <li>Get food pairing suggestions based on the aroma profile</li>
            </ul>
          </div>
        </div>
        <div className={styles.audienceFeatureRow}>
          <div className={styles.miniFeature}>
            <Scale size={18} color="var(--wine)" />
            <span>Side-by-side wine comparison</span>
          </div>
          <div className={styles.miniFeature}>
            <Lightbulb size={18} color="var(--wine)" />
            <span>Quality improvement suggestions</span>
          </div>
          <div className={styles.miniFeature}>
            <Wind size={18} color="var(--wine)" />
            <span>Chemistry-based aroma profiling</span>
          </div>
        </div>
      </section>

      {/* FINAL CTA */}
      <section className={styles.finalCta}>
        <h2>Ready to analyse your first wine?</h2>
        <p>No lab equipment integration needed — just enter the measurements you already have.</p>
        <button className={styles.ctaPrimary} onClick={() => navigate('/login')}>
          Get Started <ArrowRight size={16} />
        </button>
      </section>

      {/* FOOTER */}
      <footer className={styles.footer}>
        <div className={styles.footerTop}>
          <div className={styles.footerLogo}>
            <Wine size={18} color="var(--wine)" />
            <span>VinoInsight AI</span>
          </div>
          <div className={styles.footerLinks}>
            <button onClick={() => document.getElementById('features').scrollIntoView({ behavior: 'smooth' })}>Features</button>
            <button onClick={() => document.getElementById('how-it-works').scrollIntoView({ behavior: 'smooth' })}>How It Works</button>
            <button onClick={() => navigate('/login')}>Sign In</button>
          </div>
        </div>
      </footer>
    </div>
  );
}
