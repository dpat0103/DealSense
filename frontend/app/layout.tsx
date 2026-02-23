export const metadata = {
  title: "Car Deal Analyzer",
  description: "AI-powered used car deal scoring MVP",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          fontFamily: "system-ui, Arial",
          background: "#0b0d12",
          color: "#e9eefc",
        }}
      >
        <div style={{ maxWidth: 1100, margin: "0 auto", padding: 24 }}>
          <header
            style={{
              display: "flex",
              alignItems: "baseline",
              justifyContent: "space-between",
            }}
          >
            <div>
              <div style={{ fontSize: 24, fontWeight: 800 }}>
                Car Deal Analyzer
              </div>
              <div style={{ opacity: 0.8, marginTop: 4 }}>
                Search listings → get a fair price + deal score
              </div>
            </div>
            <a href="/" style={{ color: "#9db4ff", textDecoration: "none" }}>
              Home
            </a>
          </header>

          <main style={{ marginTop: 20 }}>{children}</main>

          <footer style={{ marginTop: 28, opacity: 0.6, fontSize: 12 }}>
            MVP • Local demo • FastAPI + Next.js
          </footer>
        </div>
      </body>
    </html>
  );
}
