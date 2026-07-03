import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";
import { Inter, Montserrat } from "next/font/google";

// Match lcmhub.com's brand typography: Inter for body, Montserrat for the wordmark/display.
const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const montserrat = Montserrat({ subsets: ["latin"], weight: ["700", "800"], variable: "--font-mont" });

export const metadata: Metadata = {
  title: "LCMH · Concrete Carbon Compare",
  description:
    "Compare embodied carbon of concrete products across the full life cycle, with full EPD provenance. Low Carbon Materials Hub.",
};

function Logo() {
  return (
    <span className="brand">
      {/* LCMH's own logo mark (downloaded from lcmhub.com) */}
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/lcmh-logo.svg" alt="Low Carbon Materials Hub" width={34} height={29} />
      {/* Official lockup: stacked all-caps Montserrat wordmark, ink — as on lcmhub.com */}
      <span className="brand-words">
        Low Carbon<br />Materials Hub
      </span>
      <span className="brand-app">Carbon Compare</span>
    </span>
  );
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    // Font variable classes must sit on <html>: the --font/--font-display chains are
    // declared in :root and var() substitution happens where the property is declared.
    <html lang="en" className={`${inter.variable} ${montserrat.variable}`}>
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
