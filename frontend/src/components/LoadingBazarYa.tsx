import React from "react";

type Variant = "cards" | "detail" | "contact";

type BaseProps = {
  title: string;
  subtitle?: string;
  variant?: Variant;
};

type SectionProps = BaseProps & {
  layout?: "section";
};

type PageProps = BaseProps & {
  layout: "page";
};

function SkeletonLine({ width, height = 14, radius = 999 }: { width: string; height?: number; radius?: number }) {
  return (
    <div
      className="bz-skeleton"
      style={{ width, height, borderRadius: radius }}
    />
  );
}

function LoadingBlocks({ variant = "cards" }: { variant?: Variant }) {
  if (variant === "detail") {
    return (
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 320px), 1fr))",
          gap: 22,
          marginTop: 26,
        }}
      >
        <div className="bz-loading-card" style={{ minHeight: 360 }}>
          <div className="bz-skeleton" style={{ width: "100%", height: 290, borderRadius: 20 }} />
          <div style={{ marginTop: 18, display: "grid", gap: 12 }}>
            <SkeletonLine width="55%" />
            <SkeletonLine width="35%" />
          </div>
        </div>

        <div className="bz-loading-card" style={{ minHeight: 360 }}>
          <div style={{ display: "grid", gap: 14 }}>
            <SkeletonLine width="24%" />
            <SkeletonLine width="72%" height={20} radius={10} />
            <SkeletonLine width="40%" height={38} radius={12} />
            <SkeletonLine width="48%" />
            <SkeletonLine width="42%" />
            <SkeletonLine width="52%" />
            <div style={{ height: 1, background: "#e2e8f0", margin: "8px 0" }} />
            <SkeletonLine width="44%" height={18} radius={10} />
            <div className="bz-skeleton" style={{ width: "100%", height: 50, borderRadius: 12 }} />
          </div>
        </div>
      </div>
    );
  }

  if (variant === "contact") {
    return (
      <div style={{ display: "grid", gap: 18, marginTop: 26 }}>
        <div className="bz-loading-card">
          <div style={{ display: "grid", gap: 12 }}>
            <SkeletonLine width="22%" />
            <SkeletonLine width="58%" height={24} radius={10} />
            <SkeletonLine width="46%" />
            <SkeletonLine width="34%" />
            <div className="bz-skeleton" style={{ width: "100%", height: 52, borderRadius: 12, marginTop: 8 }} />
            <div className="bz-skeleton" style={{ width: "100%", height: 52, borderRadius: 12 }} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))",
        gap: 18,
        marginTop: 26,
      }}
    >
      {Array.from({ length: 3 }).map((_, index) => (
        <div key={index} className="bz-loading-card">
          <div className="bz-skeleton" style={{ width: "100%", height: 150, borderRadius: 16, marginBottom: 16 }} />
          <div style={{ display: "grid", gap: 10 }}>
            <SkeletonLine width="62%" height={18} radius={10} />
            <SkeletonLine width="92%" />
            <SkeletonLine width="78%" />
            <SkeletonLine width="40%" height={18} radius={10} />
            <SkeletonLine width="34%" />
          </div>
        </div>
      ))}
    </div>
  );
}

function LoadingContent({ title, subtitle, variant = "cards" }: BaseProps) {
  return (
    <>
      <div
        className="bz-loading-card"
        style={{
          display: "flex",
          gap: 18,
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <div className="bz-loader-badge">
          <i className="pi pi-shopping-bag" aria-hidden="true" />
        </div>

        <div style={{ flex: 1, minWidth: 240 }}>
          <h2
            style={{
              fontSize: "clamp(23px, 3vw, 30px)",
              fontWeight: 800,
              color: "#1e3a8a",
              marginBottom: 8,
            }}
          >
            {title}
          </h2>

          <p style={{ color: "#64748b", marginBottom: 14 }}>
            {subtitle || "Estamos preparando la información para vos."}
          </p>

          <div className="bz-loader-dots" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
        </div>
      </div>

      <LoadingBlocks variant={variant} />
    </>
  );
}

export function SectionLoading({ title, subtitle, variant = "cards" }: SectionProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      style={{
        background: "transparent",
      }}
    >
      <LoadingContent title={title} subtitle={subtitle} variant={variant} />
    </div>
  );
}

export function PageLoading({ title, subtitle, variant = "cards" }: PageProps) {
  return (
    <main
      role="status"
      aria-live="polite"
      style={{
        minHeight: "100vh",
        background: "#f8fafc",
        color: "#1e293b",
      }}
    >
      <header
        style={{
          background: "#ffffff",
          padding: "20px 6%",
          borderBottom: "1px solid #e2e8f0",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: 20,
          flexWrap: "wrap",
        }}
      >
        <div style={{ fontSize: 28, fontWeight: 800, color: "#2563eb" }}>
          BazarYa
        </div>
        <nav style={{ display: "flex", gap: 20, flexWrap: "wrap", color: "#94a3b8" }}>
          <span>Inicio</span>
          <span>Publicaciones</span>
          <span>Mi perfil</span>
        </nav>
      </header>

      <section style={{ maxWidth: 1180, margin: "0 auto", padding: "38px 6% 60px" }}>
        <SkeletonLine width="180px" height={16} radius={10} />
        <div style={{ marginTop: 22 }}>
          <LoadingContent title={title} subtitle={subtitle} variant={variant} />
        </div>
      </section>
    </main>
  );
}
