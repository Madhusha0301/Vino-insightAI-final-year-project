import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Wine, ArrowLeft } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

/**
 * 404 / unknown-route page.
 *
 * Why this exists (project audit fix): the router previously had no catch-all
 * route, so ANY url that didn't match — a typo, a stale bookmark, or the very
 * natural guess "/predict" instead of the real nested "/dashboard/predict" —
 * rendered a completely blank page. No message, no navigation, no way back
 * except the browser's back button. It looked like the app had crashed.
 *
 * The "did you mean" hint below is deliberate: the most likely way a user hits
 * this page is by guessing a top-level path for a page that actually lives
 * under /dashboard, so we detect that specific case and offer the real link
 * rather than just saying "not found".
 */

// Pages that live under /dashboard but which a user might reasonably try to
// reach at the top level.
const DASHBOARD_PAGES = [
  'predict', 'results', 'history', 'trends', 'compare', 'admin',
];

export default function NotFound() {
  const { pathname } = useLocation();
  const { user } = useAuth();

  // "/predict" -> "predict"; also handles a trailing slash.
  const firstSegment = pathname.replace(/^\/+|\/+$/g, '').split('/')[0].toLowerCase();
  const suggestion = DASHBOARD_PAGES.includes(firstSegment)
    ? `/dashboard/${firstSegment}`
    : null;

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem',
      background: 'var(--bg)',
      color: 'var(--text)',
      fontFamily: 'var(--font-body)',
    }}>
      <div style={{ maxWidth: 520, textAlign: 'center' }}>
        <div style={{
          width: 64, height: 64, margin: '0 auto 1.5rem',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          borderRadius: 16,
          background: 'var(--bg-surface)',
          border: '1px solid var(--border)',
        }}>
          <Wine size={30} color="var(--gold)" />
        </div>

        <p style={{
          fontFamily: 'var(--font-display)',
          fontSize: '3.5rem',
          lineHeight: 1,
          color: 'var(--gold)',
          marginBottom: '0.75rem',
        }}>
          404
        </p>

        <h1 style={{
          fontFamily: 'var(--font-display)',
          fontSize: '1.6rem',
          fontWeight: 600,
          marginBottom: '0.75rem',
        }}>
          This page doesn&apos;t exist
        </h1>

        <p style={{ color: 'var(--text-muted)', marginBottom: '1.75rem' }}>
          We couldn&apos;t find <code style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border)',
            borderRadius: 6,
            padding: '0.1rem 0.4rem',
            fontSize: '0.9em',
          }}>{pathname}</code>.
          {suggestion && ' That page lives inside your dashboard.'}
        </p>

        <div style={{
          display: 'flex', gap: '0.75rem',
          justifyContent: 'center', flexWrap: 'wrap',
        }}>
          {suggestion && (
            <Link to={suggestion} style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              padding: '0.7rem 1.4rem',
              borderRadius: 999,
              background: 'var(--wine)',
              color: '#fff',
              textDecoration: 'none',
              fontWeight: 600,
            }}>
              Go to {firstSegment.charAt(0).toUpperCase() + firstSegment.slice(1)}
            </Link>
          )}

          <Link to={user ? '/dashboard' : '/'} style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            padding: '0.7rem 1.4rem',
            borderRadius: 999,
            background: suggestion ? 'transparent' : 'var(--wine)',
            border: suggestion ? '1px solid var(--border-hover)' : 'none',
            color: suggestion ? 'var(--text)' : '#fff',
            textDecoration: 'none',
            fontWeight: 600,
          }}>
            <ArrowLeft size={16} />
            {user ? 'Back to dashboard' : 'Back to home'}
          </Link>
        </div>
      </div>
    </div>
  );
}
