
import { Suspense } from "react";
import Link from "next/link";
import ContactoVendedor from "@/components/ContactoVendedor";

type DetalleProps = {
    params: Promise<{ id: string }>;
};

export default function DetalleProducto({
                                            params,
                                        }: DetalleProps) {
    return (
        <Suspense
            fallback={
                <main
                    style={{
                        padding: 40,
                        color: "#1e293b",
                        background: "#f8fafc",
                        minHeight: "100vh",
                    }}
                >
                    Cargando publicación...
                </main>
            }
        >
            <ContenidoDetalle params={params} />
        </Suspense>
    );
}

async function ContenidoDetalle({
                                    params,
                                }: DetalleProps) {
    const { id: productoId } = await params;

    return (
        <main
            style={{
                minHeight: "100vh",
                background: "#f8fafc",
                color: "#1e293b",
            }}
        >
            {/* Encabezado */}
            <header
                style={{
                    background: "#ffffff",
                    padding: "20px 6%",
                    borderBottom: "1px solid #e2e8f0",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: 20,
                }}
            >
                <Link
                    href="/"
                    style={{
                        fontSize: 28,
                        fontWeight: "bold",
                        color: "#2563eb",
                        textDecoration: "none",
                    }}
                >
                    BazarYa
                </Link>

                <nav
                    style={{
                        display: "flex",
                        gap: 20,
                        flexWrap: "wrap",
                    }}
                >
                    <Link
                        href="/"
                        style={{
                            color: "#334155",
                            textDecoration: "none",
                        }}
                    >
                        Inicio
                    </Link>

                    <Link
                        href="/publicaciones"
                        style={{
                            color: "#334155",
                            textDecoration: "none",
                        }}
                    >
                        Publicaciones
                    </Link>
                </nav>
            </header>

            {/* Contenido principal */}
            <section style={{ padding: "35px 6%" }}>
                <Link
                    href="/publicaciones"
                    style={{
                        color: "#2563eb",
                        textDecoration: "none",
                    }}
                >
                    ← Volver al catálogo
                </Link>

                <h1
                    style={{
                        marginTop: 30,
                        marginBottom: 25,
                        fontSize: 32,
                        fontWeight: "bold",
                        color: "#1e3a8a",
                    }}
                >
                    Detalle de publicación
                </h1>

                {/* Distribución de información */}
                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns:
                            "repeat(auto-fit, minmax(min(100%, 320px), 1fr))",
                        gap: 25,
                    }}
                >
                    {/* Fotografías */}
                    <div
                        style={{
                            background: "#ffffff",
                            border: "1px solid #e2e8f0",
                            borderRadius: 12,
                            padding: 30,
                            minHeight: 320,
                            display: "flex",
                            flexDirection: "column",
                            justifyContent: "center",
                            alignItems: "center",
                            gap: 15,
                        }}
                    >
                        <i
                            className="pi pi-image"
                            style={{
                                fontSize: 65,
                                color: "#94a3b8",
                            }}
                        />

                        <p
                            style={{
                                color: "#64748b",
                                textAlign: "center",
                            }}
                        >
                            Las fotografías del producto se mostrarán
                            cuando se conecte la API.
                        </p>
                    </div>

                    {/* Información del producto */}
                    <div
                        style={{
                            background: "#ffffff",
                            border: "1px solid #e2e8f0",
                            borderRadius: 12,
                            padding: 30,
                        }}
                    >
                        <p
                            style={{
                                color: "#64748b",
                                fontSize: 14,
                                marginBottom: 15,
                                overflowWrap: "anywhere",
                            }}
                        >
                            Identificador: {productoId}
                        </p>

                        <h2
                            style={{
                                fontSize: 25,
                                fontWeight: "bold",
                                marginBottom: 20,
                                color: "#1e293b",
                            }}
                        >
                            Información del producto
                        </h2>

                        <p
                            style={{
                                color: "#64748b",
                                marginBottom: 15,
                            }}
                        >
                            La información de esta publicación
                            todavía no está disponible.
                        </p>

                        <p style={{ marginBottom: 12 }}>
                            <strong>Precio:</strong> Pendiente
                        </p>

                        <p style={{ marginBottom: 12 }}>
                            <strong>Categoría:</strong> Pendiente
                        </p>

                        <p style={{ marginBottom: 12 }}>
                            <strong>Disponibilidad:</strong> Por consultar
                        </p>

                        {/* Componente reutilizable del vendedor */}
                        <ContactoVendedor
                            vendedor={null}
                            productoId={productoId}
                            disponible={false}
                        />
                    </div>
                </div>

                {/* Aviso sobre el funcionamiento */}
                <p
                    style={{
                        marginTop: 30,
                        textAlign: "center",
                        color: "#64748b",
                    }}
                >
                    BazarYa no procesa pagos ni administra envíos.
                    El contacto se realizará directamente entre
                    comprador y vendedor.
                </p>
            </section>
        </main>
    );
}
