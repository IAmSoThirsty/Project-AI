'use client';

import '../styles/globals.css';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';

const NAV_ITEMS = [
  { href: '/', label: 'Home' },
  { href: '/triumvirate', label: 'Triumvirate' },
  { href: '/defense', label: 'Defense' },
  { href: '/languages', label: 'Languages' },
  { href: '/architecture', label: 'Architecture' },
  { href: '/demos', label: 'Demos' },
  { href: '/knowledge', label: 'Knowledge' },
  { href: '/compliance', label: 'Compliance' },
  { href: '/licenses', label: 'Licenses' },
  { href: '/changelog', label: 'Changelog' },
  { href: '/vision', label: 'The Vision' },
];

function Navigation() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <nav className="nav" role="navigation" aria-label="Main navigation">
      <Link href="/" className="nav-brand">
        <span className="nav-logo"><span>TP</span></span>
        ThirstysProjects
      </Link>

      <button
        className="nav-toggle"
        onClick={() => setOpen(!open)}
        aria-label="Toggle navigation"
        aria-expanded={open}
      >
        <span /><span /><span />
      </button>

      <ul className={`nav-links${open ? ' open' : ''}`}>
        {NAV_ITEMS.map(({ href, label }) => (
          <li key={href}>
            <Link
              href={href}
              className={pathname === href ? 'active' : ''}
              onClick={() => setOpen(false)}
            >
              {label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-brand">
          <span className="gradient-text">ThirstysProjects</span>
        </div>
        <p className="footer-text">
          © 2025 Project AI Team · Sovereign Intelligence · MIT License
        </p>
        <div className="footer-links">
          {NAV_ITEMS.map(({ href, label }) => (
            <Link key={href} href={href}>{label}</Link>
          ))}
          <a href="https://github.com/IAmSoThirsty/Project-AI" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
        </div>
      </div>
    </footer>
  );
}

function Orbs() {
  return (
    <div className="orb-container" aria-hidden="true">
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />
    </div>
  );
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <title>ThirstysProjects — Project-AI · Sovereign Intelligence</title>
        <meta name="description" content="Project-AI: A sovereign AI partner combining ethical governance, kernel-level security, constitutional programming languages, and planetary-scale defense systems." />
        <meta name="keywords" content="Project-AI, ThirstysProjects, Sovereign AI, Triumvirate, OctoReflex, Thirsty-Lang, TARL, Shadow Thirst, AGI Charter, Planetary Defense" />
        <meta name="author" content="Project AI Team" />
        <meta name="robots" content="index, follow" />
        <meta property="og:title" content="ThirstysProjects — Project-AI" />
        <meta property="og:description" content="Sovereign Intelligence for Planetary Defense. Ethical AI governance, kernel-level security, and constitutionally-bound computation." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://thirstysprojects.com" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="ThirstysProjects — Project-AI" />
        <meta name="twitter:description" content="Sovereign Intelligence for Planetary Defense." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body>
        <Orbs />
        <Navigation />
        <main className="page">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
