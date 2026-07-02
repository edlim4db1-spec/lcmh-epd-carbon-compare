import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "LCMH · Concrete Carbon Compare",
  description:
    "Compare embodied carbon of concrete products across the full life cycle, with full EPD provenance. Low Carbon Materials Hub.",
};

function Logo() {
  return (
    <span className="brand">
      <svg width="26" height="26" viewBox="0 0 32 32" fill="none" aria-hidden>
        <rect width="32" height="32" rx="8" fill="var(--teal-700)" />
        <path
          d="M8 21c0-5 3.6-9 8.4-9 2.2 0 3.9.8 5 2.1l-2.2 1.9c-.7-.8-1.6-1.2-2.8-1.2-2.7 0-4.6 2.3-4.6 6.2H8Z"
          fill="#fff"
        />
        <circle cx="22" cy="21" r="2.3" fill="var(--teal-100)" />
      </svg>
      <span>
        LCMH <span className="brand-sub">Carbon Compare</span>
      </span>
    </span>
  );
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="site-header">
          <div className="container">
            <Link href="/" style={{ textDecoration: "none" }}>
              <Logo />
            </Link>
            <nav className="nav">
              <Link href="/">Products</Link>
              <Link href="/compare">Compare</Link>
              <Link href="/methodology">Methodology</Link>
            </nav>
          </div>
        </header>
        <main>{children}</main>
        <footer className="footer">
          <div className="container">
            Low Carbon Materials Hub — assessment build. Every carbon figure links to its
            source EPD (PDF · page). A not-declared life-cycle stage is shown as{" "}
            <span className="badge nd">ND</span>, never as zero.
          </div>
        </footer>
      </body>
    </html>
  );
}
