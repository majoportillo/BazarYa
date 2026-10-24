
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { InputText } from "primereact/inputtext";
import { Button } from "primereact/button";

const API = "http://127.0.0.1:8000";

type Categoria = {
    id: number;
    nombre: string;
    descripcion?: string;
    activo: boolean;
};

type Producto = {
    id: number;
    nombre: string;
    descripcion: string;
    precio: number | string;
    categoria_id: number;
    estado: string;
};

export default function Publicaciones() {
    const [busqueda, setBusqueda] = useState("");
    const [categoria, setCategoria] = useState("Todas");
    const [categorias, setCategorias] = useState<Categoria[]>([]);
    const [productos, setProductos] = useState<Producto[]>([]);
    const [cargando, setCargando] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        setBusqueda(params.get("q") || "");

        fetch(`${API}/api/productos/categorias`)
            .then(async (respuesta) => {
                if (!respuesta.ok) {
                    throw new Error("No se pudieron obtener las categorías");
                }
                return respuesta.json();
            })
            .then((datos: Categoria[]) => setCategorias(datos))
            .catch((err) => console.error(err));
    }, []);

    useEffect(() => {
        const controlador = new AbortController();

        const temporizador = setTimeout(async () => {
            setCargando(true);
            setError("");

            try {
                const parametros = new URLSearchParams();
                parametros.set("limit", "100");

                if (busqueda.trim()) {
                    parametros.set("q", busqueda.trim());
                }

                if (categoria !== "Todas") {
                    parametros.set("categoria_id", categoria);
                }

                const respuesta = await fetch(
                    `${API}/api/productos/buscar?${parametros.toString()}`,
                    { signal: controlador.signal }
                );

                if (!respuesta.ok) {
                    throw new Error(
                        `Error ${respuesta.status} al cargar publicaciones`
                    );
                }

                const datos: Producto[] = await respuesta.json();
                setProductos(datos);
            } catch (err) {
                if (controlador.signal.aborted) return;

                setProductos([]);
                setError(
                    err instanceof Error
                        ? err.message
                        : "No se pudo conectar con BazarYa"
                );
            } finally {
                if (!controlador.signal.aborted) {
                    setCargando(false);
                }
            }
        }, 300);

        return () => {
            clearTimeout(temporizador);
            controlador.abort();
        };
    }, [busqueda, categoria]);

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
                    <Link
                        href="/publicaciones"
                        style={{ color: "#2563eb" }}
                    >
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
                        <option value="Todas">Todas</option>

                        {categorias
                            .filter((cat) => cat.activo)
                            .map((cat) => (
                                <option key={cat.id} value={String(cat.id)}>
                                    {cat.nombre}
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
                <Link 
                    href="/create-post" 
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                    + Crear publicación
                </Link>
                {cargando ? (
                    <div style={{ textAlign: "center", padding: 50 }}>
                        <i className="pi pi-spin pi-spinner" />
                        <p>Cargando publicaciones...</p>
                    </div>
                ) : error ? (
                    <div
                        role="alert"
                        style={{
                            background: "#fef2f2",
                            color: "#991b1b",
                            borderRadius: 12,
                            padding: 24,
                        }}
                    >
                        No se pudieron cargar las publicaciones: {error}
                    </div>
                ) : productos.length === 0 ? (
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
                            Todavía no hay productos que coincidan con
                            tu búsqueda o categoría.
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
                        {productos.map((producto) => {
                            const vendida =
                                producto.estado === "VENDIDO" ||
                                producto.estado === "SOLD";

                            return (
                                <article
                                    key={producto.id}
                                    style={{
                                        background: "white",
                                        padding: 22,
                                        borderRadius: 12,
                                        border: "1px solid #e2e8f0",
                                    }}
                                >
                                    <h3
                                        style={{
                                            fontSize: 20,
                                            fontWeight: "bold",
                                        }}
                                    >
                                        {producto.nombre}
                                    </h3>

                                    <p
                                        style={{
                                            color: "#64748b",
                                            marginTop: 8,
                                        }}
                                    >
                                        {producto.descripcion}
                                    </p>

                                    <p
                                        style={{
                                            marginTop: 12,
                                            fontWeight: "bold",
                                        }}
                                    >
                                        Q {Number(producto.precio).toFixed(2)}
                                    </p>

                                    {vendida && (
                                        <p
                                            style={{
                                                color: "#b45309",
                                                marginTop: 8,
                                            }}
                                        >
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
                            );
                        })}
                    </div>
                )}
            </section>
        </main>
    );
}

