
import Link from "next/link";

type VendedorPublico = {
    id: string;
    nombre: string;
    telefono?: string | null;
};

type ContactoVendedorProps = {
    vendedor: VendedorPublico | null;
    productoId: string;
    disponible: boolean;
};

export default function ContactoVendedor({
                                             vendedor,
                                             productoId,
                                             disponible,
                                         }: ContactoVendedorProps) {
    return (
        <section
            style={{
                marginTop: 25,
                padding: 20,
                background: "#eff6ff",
                borderRadius: 10,
            }}
        >
            <h3
                style={{
                    fontSize: 19,
                    fontWeight: "bold",
                    marginBottom: 12,
                    color: "#1e293b",
                }}
            >
                Información del vendedor
            </h3>

            {vendedor ? (
                <>
                    <p style={{ color: "#475569", marginBottom: 8 }}>
                        <strong>Vendedor:</strong> {vendedor.nombre}
                    </p>

                    <Link
                        href={`/vendedores/${encodeURIComponent(vendedor.id)}`}
                        style={{
                            color: "#2563eb",
                            display: "inline-block",
                            marginBottom: 16,
                        }}
                    >
                        Ver perfil público
                    </Link>

                    {disponible ? (
                        <Link
                            href={`/publicaciones/${encodeURIComponent(productoId)}/contacto`}
                            style={{
                                display: "inline-block",
                                padding: "12px 18px",
                                background: "#2563eb",
                                color: "white",
                                borderRadius: 8,
                                textDecoration: "none",
                                fontWeight: "bold",
                            }}
                        >
                            Contactar al vendedor
                        </Link>
                    ) : (
                        <p style={{ color: "#64748b" }}>
                            Esta publicación no está disponible para contacto.
                        </p>
                    )}
                </>
            ) : (
                <p style={{ color: "#64748b" }}>
                    La información pública del vendedor estará disponible
                    cuando se conecte la API de BazarYa.
                </p>
            )}
        </section>
    );
}
