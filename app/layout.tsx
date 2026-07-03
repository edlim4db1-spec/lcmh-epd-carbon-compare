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
      {/* LCMH's own logo mark (downloaded from lcmhub.com) */}
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/lcmh-logo.svg" alt="Low Carbon Materials Hub" width={32} height={27} />
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
