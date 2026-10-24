import MenuBazarYa from "../../../../components/MenuBazarYa";

import Link from "next/link";
import { Suspense } from "react";

type ContactoProps = {
    params: Promise<{ id: string }>;
};

type VendedorContacto = {
    vendedor_id: string;
    nombre_completo: string;
    telefono: string | null;
    email: string | null;
    nota?: string;
};

type ResultadoContacto = {
    contacto: VendedorContacto | null;
    error: string | null;
};

const API_URL =
    process.env.API_URL || "http://127.0.0.1:8000";

async function obtenerContacto(
    id: string
): Promise<ResultadoContacto> {
    try {
        const respuesta = await fetch(
            `${API_URL}/api/productos/${encodeURIComponent(id)}/contacto`,
            { cache: "no-store" }
        );

        if (respuesta.status === 404) {
            return {
                contacto: null,
                error: "No se encontró información pública del vendedor para esta publicación.",
            };
        }

        if (!respuesta.ok) {
            return {
                contacto: null,
                error: `No se pudo consultar el contacto (error ${respuesta.status}).`,
            };
        }

        const contacto: VendedorContacto = await respuesta.json();

        return { contacto, error: null };
    } catch {
        return {
            contacto: null,
            error: "No fue posible conectarse con la API de BazarYa.",
        };
    }
}

function obtenerWhatsApp(
    telefono: string | null
): string | null {
    if (!telefono) return null;

    const digitos = telefono.replace(/\D/g, "");

    // Número guatemalteco de 8 dígitos.
    if (/^[2-9]\d{7}$/.test(digitos)) {
        return `502${digitos}`;
    }

    // Número guatemalteco con código de país.
    if (/^502[2-9]\d{7}$/.test(digitos)) {
        return digitos;
    }

    return null;
}

export default function PaginaContacto({
    params,
}: ContactoProps) {
    return (
        <Suspense
            fallback={
                <main
                    style={{
                        minHeight: "100vh",
                        background: "#f8fafc",
                        padding: 40,
                        color: "#1e293b",
                    }}
                >
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

    const resultado = /^\d+$/.test(id)
        ? await obtenerContacto(id)
        : {
              contacto: null,
              error: "El identificador de la publicación no es válido.",
          };

    const { contacto, error } = resultado;

    const whatsapp = contacto
        ? obtenerWhatsApp(contacto.telefono)
        : null;

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

                <MenuBazarYa />
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
                    Consultá los datos de contacto autorizados
                    para comunicarte directamente con el vendedor.
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
                                <strong>Vendedor: </strong>
                                {contacto.nombre_completo}
                            </p>

                            {contacto.telefono && (
                                <p>
                                    <strong>Teléfono: </strong>
                                    <a
                                        href={`tel:${contacto.telefono.replace(/[^+\d]/g, "")}`}
                                        style={{ color: "#2563eb" }}
                                    >
                                        {contacto.telefono}
                                    </a>
                                </p>
                            )}

                            {contacto.email && (
                                <p>
                                    <strong>Correo electrónico: </strong>
                                    <a
                                        href={`mailto:${contacto.email}`}
                                        style={{ color: "#2563eb" }}
                                    >
                                        {contacto.email}
                                    </a>
                                </p>
                            )}

                            {whatsapp && (
                                <a
                                    href={`https://wa.me/${whatsapp}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    style={{
                                        display: "inline-block",
                                        width: "fit-content",
                                        padding: "13px 20px",
                                        background: "#16803c",
                                        color: "#ffffff",
                                        borderRadius: 8,
                                        textDecoration: "none",
                                        fontWeight: "bold",
                                        textAlign: "center",
                                    }}
                                >
                                    <i
                                        className="pi pi-whatsapp"
                                        style={{ marginRight: 8 }}
                                    />
                                    Contactar por WhatsApp
                                </a>
                            )}

                            <p
                                style={{
                                    color: "#64748b",
                                    fontSize: 14,
                                }}
                            >
                                Utilizá estos datos únicamente para
                                consultar sobre la publicación.
                            </p>
                        </div>
                    ) : (
                        <div
                            role="status"
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
                                {error ||
                                    "No hay datos de contacto disponibles."}
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
                        compradores y vendedores. La plataforma no
                        procesa pagos ni administra envíos.
                    </p>
                </div>
            </section>
        </main>
    );
}
