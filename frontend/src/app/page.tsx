
"use client";

import { useState } from "react";
import Link from "next/link";
import { InputText } from "primereact/inputtext";
import { Button } from "primereact/button";

export default function Home() {
    const [busqueda, setBusqueda] = useState("");

    const buscarProductos = () => {
        const texto = busqueda.trim();

        window.location.href =
            "/publicaciones?q=" + encodeURIComponent(texto);
    };

    const estiloEnlace = {
        color: "#334155",
        textDecoration: "none",
        fontSize: 15,
        fontWeight: 500,
    } as const;

    return (
        <main
            style={{
                minHeight: "100vh",
                background: "#f8fafc",
                color: "#1e293b",
            }}
        >
            {/* ENCABEZADO */}
            <header
                style={{
                    background: "#ffffff",
                    padding: "20px 6%",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: "20px",
                    borderBottom: "1px solid #e5e7eb",
                }}
            >
                <Link
                    href="/"
                    style={{
                        fontSize: "28px",
                        fontWeight: "bold",
                        color: "#2563eb",
                        textDecoration: "none",
                    }}
                >
                    BazarYa
                </Link>

                {/* MENÚ DE NAVEGACIÓN */}
                <nav
                    aria-label="Navegación principal"
                    style={{
                        display: "flex",
                        alignItems: "center",
                        flexWrap: "wrap",
                        gap: "20px",
                    }}
                >
                    <Link
                        href="/"
                        style={{
                            ...estiloEnlace,
                            color: "#2563eb",
                            fontWeight: 700,
                        }}
                    >
                        Inicio
                    </Link>

                    <Link
                        href="/publicaciones"
                        style={estiloEnlace}
                    >
                        Publicaciones
                    </Link>

                    <Link href="/create-post">Vender producto</Link>

                    <Link
                        href="/mis-publicaciones"
                        style={estiloEnlace}
                    >
                        Mis publicaciones
                    </Link>

                    <Link
                        href="/profile"
                        style={estiloEnlace}
                    >
                        Mi perfil
                    </Link>
                </nav>
            </header>

            {/* SECCIÓN PRINCIPAL */}
            <section
                style={{
                    padding: "80px 6%",
                    textAlign: "center",
                    background: "#eff6ff",
                }}
            >
                <h1
                    style={{
                        fontSize: "clamp(30px, 5vw, 48px)",
                        fontWeight: "bold",
                        color: "#1e3a8a",
                        marginBottom: "20px",
                    }}
                >
                    Dale una segunda vida a lo que ya no usás
                </h1>

                <p
                    style={{
                        fontSize: "18px",
                        color: "#475569",
                        marginBottom: "30px",
                    }}
                >
                    Descubrí productos, explorá publicaciones y contactá
                    directamente a los vendedores.
                </p>

                {/* BUSCADOR */}
                <div
                    style={{
                        maxWidth: "650px",
                        margin: "0 auto",
                        display: "flex",
                        gap: "10px",
                        flexWrap: "wrap",
                        justifyContent: "center",
                    }}
                >
                    <InputText
                        value={busqueda}
                        onChange={(e) => setBusqueda(e.target.value)}
                        placeholder="¿Qué producto estás buscando?"
                        aria-label="Buscar productos"
                        onKeyDown={(e) => {
                            if (e.key === "Enter") buscarProductos();
                        }}
                        style={{
                            flex: "1 1 250px",
                            padding: "12px",
                            background: "#ffffff",
                            color: "#1e293b",
                            border: "1px solid #cbd5e1",
                            borderRadius: "8px",
                        }}
                    />

                    <Button
                        label="Buscar"
                        icon="pi pi-search"
                        onClick={buscarProductos}
                    />
                </div>
            </section>

            {/* SECCIÓN DE PUBLICACIONES */}
            <section
                style={{
                    padding: "60px 6%",
                    textAlign: "center",
                }}
            >
                <h2
                    style={{
                        fontSize: "28px",
                        fontWeight: "bold",
                        color: "#1e293b",
                        marginBottom: "16px",
                    }}
                >
                    Explorá las publicaciones
                </h2>

                <p
                    style={{
                        color: "#64748b",
                        marginBottom: "24px",
                    }}
                >
                    Encontrá artículos disponibles publicados por los
                    vendedores de BazarYa.
                </p>

                <Link
                    href="/publicaciones"
                    style={{
                        display: "inline-block",
                        padding: "13px 25px",
                        background: "#2563eb",
                        color: "#ffffff",
                        borderRadius: "8px",
                        fontWeight: 700,
                        textDecoration: "none",
                        marginBottom: "35px",
                    }}
                >
                    Ver publicaciones
                </Link>

                <p
                    style={{
                        color: "#64748b",
                        marginTop: "20px",
                    }}
                >
                    BazarYa no procesa pagos ni administra envíos.
                    El contacto se realiza directamente entre
                    comprador y vendedor.
                </p>
            </section>
        </main>
    );
}
