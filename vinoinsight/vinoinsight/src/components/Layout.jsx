import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import {
  LayoutDashboard, FlaskConical, BarChart3, History,
  TrendingUp, LogOut, Menu, X, Wine, Scale, Sun, Moon, ShieldCheck
} from 'lucide-react';
import styles from './Layout.module.css';

const BASE_ITEMS = [
  { to: '/dashboard',          icon: LayoutDashboard, label: 'Dashboard'  },
  { to: '/dashboard/predict',  icon: FlaskConical,    label: 'Predict'    },
  { to: '/dashboard/results',  icon: BarChart3,       label: 'Results'    },
  { to: '/dashboard/compare',  icon: Scale,           label: 'Compare'    },
  { to: '/dashboard/history',  icon: History,         label: 'History'    },
  { to: '/dashboard/trends',   icon: TrendingUp,      label: 'Trends'     },
];

const ADMIN_ITEM = { to: '/dashboard/admin', icon: ShieldCheck, label: 'Seller Verification' };

export default function Layout() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const handleLogout = () => { logout(); navigate('/login'); };

  const navItems = user?.role === 'admin' ? [BASE_ITEMS[0], ADMIN_ITEM] : BASE_ITEMS;
  const isPendingSeller = user?.role === 'seller' && user?.status === 'pending';

  return (
    <div className={styles.shell}>
      {open && <div className={styles.overlay} onClick={() => setOpen(false)} />}

      <aside className={`${styles.sidebar} ${open ? styles.sidebarOpen : ''}`}>
        <div className={styles.sidebarTop}>
          <div className={styles.logo} onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
            <Wine size={22} color="var(--gold)" />
            <span>VinoInsight<span className={styles.logoAi}>AI</span></span>
          </div>
          <button className={styles.closeBtn} onClick={() => setOpen(false)}>
            <X size={18} />
          </button>
        </div>

        <div style={{ padding: '0 16px 10px' }}>
          <span style={{
            display: 'inline-block', fontSize: '0.68rem', fontWeight: 700,
            letterSpacing: '0.05em', textTransform: 'uppercase',
            color: 'var(--gold)', background: 'rgba(201,168,76,0.1)',
            padding: '4px 10px', borderRadius: 999,
          }}>
            {user?.role === 'admin' ? 'Admin' : user?.role === 'seller' ? 'Seller / Producer' : 'Buyer'}
          </span>
        </div>

        <nav className={styles.nav}>
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/dashboard'}
              className={({ isActive }) =>
                `${styles.navItem} ${isActive ? styles.navActive : ''}`
              }
              onClick={() => setOpen(false)}
            >
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className={styles.sidebarBottom}>
          <div className={styles.userChip}>
            <div className={styles.avatar}>
              {user?.name?.[0]?.toUpperCase() || 'U'}
            </div>
            <span className={styles.userName}>{user?.name}</span>
          </div>
          <button className={styles.logoutBtn} onClick={handleLogout}>
            <LogOut size={16} />
            <span>Sign out</span>
          </button>
        </div>
      </aside>

      <div className={styles.main}>
        <header className={styles.topbar}>
          <button className={styles.menuBtn} onClick={() => setOpen(true)}>
            <Menu size={22} />
          </button>
          <div className={styles.topbarRight}>
            <button className={styles.themeToggle} onClick={toggleTheme} title="Toggle light/dark mode">
              {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
            </button>
            <div className={styles.badge}>
              <span className={styles.dot} />
              System Online
            </div>
          </div>
        </header>
        <main className={styles.content}>
          {isPendingSeller && (
            <div style={{
              background: 'rgba(201,168,76,0.1)', border: '1px solid var(--border-hover)',
              borderRadius: 12, padding: '14px 18px', marginBottom: 20,
              color: 'var(--gold-light)', fontSize: '0.86rem',
            }}>
              Your seller account is pending admin verification. You can still explore
              predictions, but some seller-specific features are limited until approved.
            </div>
          )}
          <Outlet />
        </main>
      </div>
    </div>
  );
}
