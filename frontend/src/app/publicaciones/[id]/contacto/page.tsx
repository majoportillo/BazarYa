
import Link from "next/link";
import { Suspense } from "react";

type ContactoProps = {
    params: Promise<{ id: string }>;
};

type VendedorContacto = {
    nombre: string;
    telefono?: string | null;
    email?: string | null;
    whatsapp?: string | null;
};

// Los datos vendrán de la API del backend.
// Por ahora no se muestran datos inventados.
const vendedor: VendedorContacto | null = null;

export default function PaginaContacto({
                                           params,
                                       }: ContactoProps) {
    return (
        <Suspense
            fallback={
                <main style={{ padding: 40 }}>
                    Cargando información de contacto...
                </main>
            }
        >
            <ContenidoContacto params={params} />
        </Suspense>
    );
}

async function ContenidoContacto({
                                     params,
                                 }: ContactoProps) {
    const { id } = await params;

    // Se reemplazará por la consulta real al backend.
    const contacto: VendedorContacto | null = vendedor;

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
                    gap: 20,
                    flexWrap: "wrap",
                }}
            >
                <Link
                    href="/"
                    style={{
                        color: "#2563eb",
                        fontSize: 28,
                        fontWeight: "bold",
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
                        style={{ color: "#334155" }}
                    >
                        Publicaciones
                    </Link>
                </nav>
            </header>

            <section
                style={{
                    maxWidth: 850,
                    margin: "0 auto",
                    padding: "45px 20px",
                }}
            >
                <Link
                    href={`/publicaciones/${encodeURIComponent(id)}`}
                    style={{
                        color: "#2563eb",
                        textDecoration: "none",
                    }}
                >
                    ← Volver al producto
                </Link>

                <h1
                    style={{
                        fontSize: "clamp(28px, 4vw, 36px)",
                        color: "#1e3a8a",
                        fontWeight: "bold",
                        marginTop: 30,
                        marginBottom: 12,
                    }}
                >
                    Contactar al vendedor
                </h1>

                <p
                    style={{
                        color: "#64748b",
                        marginBottom: 30,
                    }}
                >
                    Consultá la información pública del vendedor
                    para comunicarte directamente sobre el artículo.
                </p>

                <div
                    style={{
                        background: "#ffffff",
                        border: "1px solid #e2e8f0",
                        borderRadius: 14,
                        padding: 30,
                    }}
                >
                    <h2
                        style={{
                            fontSize: 23,
                            fontWeight: "bold",
                            marginBottom: 20,
                        }}
                    >
                        Información de contacto
                    </h2>

                    <p
                        style={{
                            color: "#64748b",
                            marginBottom: 18,
                        }}
                    >
                        Publicación: {id}
                    </p>

                    {contacto ? (
                        <div style={{ display: "grid", gap: 18 }}>
                            <p>
                                <strong>Vendedor:</strong>{" "}
                                {contacto.nombre}
                            </p>

                            {contacto.telefono && (
                                <p>
                                    <strong>Teléfono:</strong>{" "}
                                    <a
                                        href={`tel:${contacto.telefono}`}
                                        style={{ color: "#2563eb" }}
                                    >
                                        {contacto.telefono}
                                    </a>
                                </p>
                            )}

                            {contacto.email && (
                                <p>
                                    <strong>Correo:</strong>{" "}
                                    <a
                                        href={`mailto:${contacto.email}`}
                                        style={{ color: "#2563eb" }}
                                    >
                                        {contacto.email}
                                    </a>
                                </p>
                            )}

                            {contacto.whatsapp && (
                                <a
                                    href={`https://wa.me/${contacto.whatsapp.replace(/\D/g, "")}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    style={{
                                        display: "inline-block",
                                        width: "fit-content",
                                        padding: "12px 20px",
                                        background: "#16803c",
                                        color: "#ffffff",
                                        borderRadius: 8,
                                        textDecoration: "none",
                                        fontWeight: "bold",
                                    }}
                                >
                                    Contactar por WhatsApp
                                </a>
                            )}
                        </div>
                    ) : (
                        <div
                            style={{
                                padding: 25,
                                background: "#eff6ff",
                                borderRadius: 10,
                                textAlign: "center",
                            }}
                        >
                            <i
                                className="pi pi-users"
                                style={{
                                    fontSize: 35,
                                    color: "#64748b",
                                }}
                            />

                            <h3
                                style={{
                                    fontSize: 19,
                                    fontWeight: "bold",
                                    marginTop: 15,
                                    marginBottom: 10,
                                }}
                            >
                                Información no disponible
                            </h3>

                            <p style={{ color: "#64748b" }}>
                                Los datos públicos del vendedor se
                                mostrarán cuando estén disponibles
                                mediante la API de BazarYa.
                            </p>
                        </div>
                    )}
                </div>

                <div
                    style={{
                        background: "#eff6ff",
                        borderRadius: 12,
                        padding: 22,
                        marginTop: 25,
                    }}
                >
                    <h3
                        style={{
                            fontSize: 18,
                            fontWeight: "bold",
                            marginBottom: 10,
                        }}
                    >
                        Información importante
                    </h3>

                    <p style={{ color: "#475569" }}>
                        BazarYa facilita el contacto directo entre
                        compradores y vendedores. La plataforma
                        no procesa pagos ni administra envíos.
                    </p>
                </div>
            </section>
        </main>
    );
}
