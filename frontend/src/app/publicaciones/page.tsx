
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { InputText } from "primereact/inputtext";
import { Button } from "primereact/button";

type Producto = {
    id: string;
    titulo: string;
    descripcion: string;
    precio: number;
    categoria: string;
    estado: "PENDING" | "APPROVED" | "REJECTED" | "SOLD";
};

// Se conectará a la API cuando esté disponible.
const productos: Producto[] = [];

export default function Publicaciones() {
    const [busqueda, setBusqueda] = useState("");
    const [categoria, setCategoria] = useState("Todas");

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        setBusqueda(params.get("q") || "");
    }, []);

    const categorias = [
        "Todas",
        ...new Set(
            productos
                .filter((p) => p.estado === "APPROVED" || p.estado === "SOLD")
                .map((p) => p.categoria)
        ),
    ];

    const resultados = productos.filter((producto) => {
        const visible =
            producto.estado === "APPROVED" ||
            producto.estado === "SOLD";

        const texto = busqueda.toLowerCase().trim();

        const coincide =
            producto.titulo.toLowerCase().includes(texto) ||
            producto.descripcion.toLowerCase().includes(texto);

        const coincideCategoria =
            categoria === "Todas" ||
            producto.categoria === categoria;

        return visible && coincide && coincideCategoria;
    });

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
                    background: "white",
                    padding: "20px 6%",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    gap: 20,
                    flexWrap: "wrap",
                    borderBottom: "1px solid #e2e8f0",
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
                    <Link href="/publicaciones" style={{ color: "#2563eb" }}>
                        Publicaciones
                    </Link>
                </nav>
            </header>

            <section
                style={{
                    background: "#eff6ff",
                    padding: "50px 6%",
                    textAlign: "center",
                }}
            >
                <h1
                    style={{
                        fontSize: "clamp(28px, 4vw, 40px)",
                        fontWeight: "bold",
                        color: "#1e3a8a",
                        marginBottom: 15,
                    }}
                >
                    Explorá las publicaciones
                </h1>

                <p style={{ color: "#475569", fontSize: 17 }}>
                    Encontrá artículos y dales una segunda oportunidad.
                </p>
            </section>

            <section style={{ padding: "35px 6%" }}>
                <div
                    style={{
                        display: "flex",
                        flexWrap: "wrap",
                        gap: 15,
                        marginBottom: 35,
                    }}
                >
                    <InputText
                        value={busqueda}
                        onChange={(e) => setBusqueda(e.target.value)}
                        placeholder="Buscar por palabra clave..."
                        aria-label="Buscar publicaciones"
                        style={{
                            flex: "1 1 250px",
                            padding: 12,
                            background: "#fff",
                            color: "#1e293b",
                            border: "1px solid #cbd5e1",
                        }}
                    />

                    <select
                        value={categoria}
                        onChange={(e) => setCategoria(e.target.value)}
                        aria-label="Filtrar por categoría"
                        style={{
                            padding: 12,
                            minWidth: 180,
                            background: "white",
                            color: "#1e293b",
                            border: "1px solid #cbd5e1",
                            borderRadius: 6,
                        }}
                    >
                        {categorias.map((cat) => (
                            <option key={cat} value={cat}>
                                {cat}
                            </option>
                        ))}
                    </select>

                    <Button
                        label="Limpiar filtros"
                        outlined
                        onClick={() => {
                            setBusqueda("");
                            setCategoria("Todas");
                            window.history.replaceState(
                                null,
                                "",
                                "/publicaciones"
                            );
                        }}
                    />
                </div>

                <h2
                    style={{
                        fontSize: 24,
                        fontWeight: "bold",
                        marginBottom: 25,
                    }}
                >
                    Productos publicados
                </h2>

                {resultados.length === 0 ? (
                    <div
                        style={{
                            background: "white",
                            border: "1px solid #e2e8f0",
                            borderRadius: 12,
                            padding: "60px 20px",
                            textAlign: "center",
                        }}
                    >
                        <i
                            className="pi pi-inbox"
                            style={{
                                fontSize: 42,
                                color: "#94a3b8",
                                marginBottom: 18,
                            }}
                        />

                        <h3 style={{ fontSize: 20, marginBottom: 10 }}>
                            No hay publicaciones para mostrar
                        </h3>

                        <p style={{ color: "#64748b" }}>
                            El catálogo se conectará próximamente
                            con la API de BazarYa.
                        </p>
                    </div>
                ) : (
                    <div
                        style={{
                            display: "grid",
                            gridTemplateColumns:
                                "repeat(auto-fit, minmax(240px, 1fr))",
                            gap: 20,
                        }}
                    >
                        {resultados.map((producto) => (
                            <article
                                key={producto.id}
                                style={{
                                    background: "white",
                                    padding: 22,
                                    borderRadius: 12,
                                    border: "1px solid #e2e8f0",
                                }}
                            >
                                <h3 style={{ fontSize: 20, fontWeight: "bold" }}>
                                    {producto.titulo}
                                </h3>

                                <p style={{ color: "#64748b", marginTop: 8 }}>
                                    {producto.descripcion}
                                </p>

                                <p style={{ marginTop: 12, fontWeight: "bold" }}>
                                    Q {producto.precio.toFixed(2)}
                                </p>

                                {producto.estado === "SOLD" && (
                                    <p style={{ color: "#b45309", marginTop: 8 }}>
                                        Vendido — No disponible
                                    </p>
                                )}

                                <Link
                                    href={`/publicaciones/${producto.id}`}
                                    style={{
                                        display: "inline-block",
                                        marginTop: 15,
                                        color: "#2563eb",
                                        fontWeight: "bold",
                                    }}
                                >
                                    Ver detalle
                                </Link>
                            </article>
                        ))}
                    </div>
                )}
            </section>
        </main>
    );
}
