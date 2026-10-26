
import { Suspense } from "react";
import Link from "next/link";
import { PageLoading } from "@/components/LoadingBazarYa";

type DetalleProps = {
    params: Promise<{ id: string }>;
};

type ImagenProducto = {
    id: number;
    url_imagen: string;
    es_principal: boolean;
};

type Producto = {
    id: number;
    usuario_id: string;
    nombre: string;
    descripcion: string;
    precio: number | string;
    stock: number;
    estado: string;
    categoria: {
        id: number;
        nombre: string;
    };
    imagenes: ImagenProducto[];
};

const API_URL =
    process.env.API_URL || "http://127.0.0.1:8000";

async function obtenerProducto(id: string): Promise<Producto | null> {
    try {
        const respuesta = await fetch(
            `${API_URL}/api/productos/${encodeURIComponent(id)}`,
            { cache: "no-store" }
        );

        if (!respuesta.ok) return null;

        return (await respuesta.json()) as Producto;
    } catch {
        return null;
    }
}

const tarjeta: React.CSSProperties = {
    background: "#ffffff",
    border: "1px solid #e2e8f0",
    borderRadius: 12,
    padding: 28,
};

export default function DetalleProducto({ params }: DetalleProps) {
    return (
        <Suspense
            fallback={
                <PageLoading
                    layout="page"
                    title="Cargando información del producto"
                    subtitle="Estamos preparando las fotos, el precio y los datos del artículo."
                    variant="detail"
                />
            }
        >
            <ContenidoDetalle params={params} />
        </Suspense>
    );
}

async function ContenidoDetalle({ params }: DetalleProps) {
    const { id } = await params;

    const producto = /^\d+$/.test(id)
        ? await obtenerProducto(id)
        : null;

    const vendido = producto?.estado === "VENDIDO";
    const disponible =
        producto?.estado === "ACTIVO" && producto.stock > 0;

    const imagenPrincipal =
        producto?.imagenes?.find((imagen) => imagen.es_principal) ??
        producto?.imagenes?.[0];

    return (
        <main
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

                <nav style={{ display: "flex", gap: 20 }}>
                    <Link href="/" style={{ color: "#334155" }}>
                        Inicio
                    </Link>
                    <Link
                        href="/publicaciones"
                        style={{ color: "#2563eb" }}
                    >
                        Publicaciones
                    </Link>
                </nav>
            </header>

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

                {!producto ? (
                    <div
                        style={{
                            ...tarjeta,
                            marginTop: 30,
                            textAlign: "center",
                            padding: 50,
                        }}
                    >
                        <i
                            className="pi pi-exclamation-circle"
                            style={{
                                fontSize: 46,
                                color: "#94a3b8",
                            }}
                        />
                        <h1
                            style={{
                                fontSize: 27,
                                color: "#1e3a8a",
                                marginTop: 20,
                            }}
                        >
                            Publicación no disponible
                        </h1>
                        <p
                            style={{
                                color: "#64748b",
                                marginTop: 12,
                            }}
                        >
                            No encontramos el producto o no fue posible
                            consultar la API de BazarYa.
                        </p>
                    </div>
                ) : (
                    <>
                        <h1
                            style={{
                                marginTop: 30,
                                marginBottom: 25,
                                fontSize: 32,
                                fontWeight: "bold",
                                color: "#1e3a8a",
                            }}
                        >
                            {producto.nombre}
                        </h1>

                        <div
                            style={{
                                display: "grid",
                                gridTemplateColumns:
                                    "repeat(auto-fit, minmax(min(100%, 320px), 1fr))",
                                gap: 25,
                            }}
                        >
                            <div style={tarjeta}>
                                {imagenPrincipal ? (
                                    <img
                                        src={imagenPrincipal.url_imagen}
                                        alt={producto.nombre}
                                        style={{
                                            width: "100%",
                                            maxHeight: 380,
                                            objectFit: "contain",
                                            borderRadius: 10,
                                        }}
                                    />
                                ) : (
                                    <div
                                        style={{
                                            minHeight: 270,
                                            display: "flex",
                                            flexDirection: "column",
                                            alignItems: "center",
                                            justifyContent: "center",
                                            gap: 15,
                                            color: "#94a3b8",
                                        }}
                                    >
                                        <i
                                            className="pi pi-image"
                                            style={{ fontSize: 65 }}
                                        />
                                        <p>Producto sin fotografía</p>
                                    </div>
                                )}

                                {producto.imagenes?.length > 1 && (
                                    <div
                                        style={{
                                            display: "flex",
                                            flexWrap: "wrap",
                                            gap: 10,
                                            marginTop: 20,
                                        }}
                                    >
                                        {producto.imagenes.map((imagen) => (
                                            <img
                                                key={imagen.id}
                                                src={imagen.url_imagen}
                                                alt={`Fotografía de ${producto.nombre}`}
                                                style={{
                                                    width: 75,
                                                    height: 75,
                                                    objectFit: "cover",
                                                    borderRadius: 8,
                                                    border: "1px solid #e2e8f0",
                                                }}
                                            />
                                        ))}
                                    </div>
                                )}
                            </div>

                            <div style={tarjeta}>
                                <p
                                    style={{
                                        color: "#64748b",
                                        fontSize: 14,
                                        marginBottom: 15,
                                    }}
                                >
                                    Publicación #{producto.id}
                                </p>

                                <h2
                                    style={{
                                        fontSize: 25,
                                        fontWeight: "bold",
                                        marginBottom: 20,
                                    }}
                                >
                                    Información del producto
                                </h2>

                                <p
                                    style={{
                                        color: "#475569",
                                        marginBottom: 20,
                                        whiteSpace: "pre-line",
                                    }}
                                >
                                    {producto.descripcion}
                                </p>

                                <p
                                    style={{
                                        color: "#2563eb",
                                        fontSize: 27,
                                        fontWeight: "bold",
                                        marginBottom: 20,
                                    }}
                                >
                                    Q {Number(producto.precio).toFixed(2)}
                                </p>

                                <p style={{ marginBottom: 12 }}>
                                    <strong>Categoría: </strong>
                                    {producto.categoria?.nombre ??
                                        "Sin categoría"}
                                </p>

                                <p style={{ marginBottom: 12 }}>
                                    <strong>Existencias: </strong>
                                    {producto.stock}
                                </p>

                                <p style={{ marginBottom: 20 }}>
                                    <strong>Disponibilidad: </strong>
                                    <span
                                        style={{
                                            color: disponible
                                                ? "#15803d"
                                                : "#b45309",
                                            fontWeight: "bold",
                                        }}
                                    >
                                        {vendido
                                            ? "Vendido — No disponible"
                                            : disponible
                                              ? "Disponible"
                                              : "No disponible"}
                                    </span>
                                </p>

                                <div
                                    style={{
                                        borderTop: "1px solid #e2e8f0",
                                        paddingTop: 20,
                                        marginTop: 20,
                                    }}
                                >
                                    <h3
                                        style={{
                                            fontSize: 20,
                                            fontWeight: "bold",
                                            marginBottom: 15,
                                        }}
                                    >
                                        Contacto del vendedor
                                    </h3>

                                    {disponible ? (
                                        <Link
                                            href={`/publicaciones/${producto.id}/contacto`}
                                            style={{
                                                display: "block",
                                                background: "#2563eb",
                                                color: "#ffffff",
                                                padding: "13px 20px",
                                                borderRadius: 8,
                                                textAlign: "center",
                                                textDecoration: "none",
                                                fontWeight: "bold",
                                            }}
                                        >
                                            Contactar al vendedor
                                        </Link>
                                    ) : (
                                        <p style={{ color: "#64748b" }}>
                                            Esta publicación no está
                                            disponible para contacto.
                                        </p>
                                    )}
                                </div>
                            </div>
                        </div>

                        <p
                            style={{
                                marginTop: 30,
                                textAlign: "center",
                                color: "#64748b",
                            }}
                        >
                            BazarYa no procesa pagos ni administra envíos.
                            El contacto se realiza directamente entre
                            comprador y vendedor.
                        </p>
                    </>
                )}
            </section>
        </main>
    );
}
