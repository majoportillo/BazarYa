"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { SectionLoading } from "@/components/LoadingBazarYa";

const API = "http://127.0.0.1:8000";

type Categoria = { id: number; nombre: string };
type Producto = {
  id: number;
  nombre: string;
  descripcion: string;
  precio: number | string;
  stock: number;
  estado: string;
  categoria?: Categoria;
  categoria_id?: number;
};
type Edicion = {
  nombre: string;
  descripcion: string;
  precio: string;
  stock: string;
  categoria_id: string;
};

const caja: React.CSSProperties = {
  background: "#fff", border: "1px solid #e2e8f0", borderRadius: 12, padding: 24,
};
const entrada: React.CSSProperties = {
  display: "block", width: "100%", padding: 11, marginTop: 6,
  border: "1px solid #cbd5e1", borderRadius: 7, color: "#1e293b", background: "#fff",
};
const boton: React.CSSProperties = {
  border: 0, borderRadius: 8, padding: "11px 18px", background: "#2563eb",
  color: "#fff", cursor: "pointer", fontWeight: 600,
};

export default function MisPublicaciones() {
  const [productos, setProductos] = useState<Producto[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");
  const [editando, setEditando] = useState<number | null>(null);
  const [guardando, setGuardando] = useState(false);
  const [form, setForm] = useState<Edicion>({nombre: "", descripcion: "", precio: "", stock: "", categoria_id: ""});

  const cargar = useCallback(async () => {
    setCargando(true);
    setError("");
    const token = localStorage.getItem("token") || localStorage.getItem("access_token");
    if (!token) {
      setError("Necesitás iniciar sesión para consultar tus publicaciones.");
      setCargando(false);
      return;
    }
    try {
      const [rProductos, rCategorias] = await Promise.all([
        fetch(`${API}/api/productos/mis-publicaciones`, {
          headers: {Authorization: `Bearer ${token}`}, cache: "no-store",
        }),
        fetch(`${API}/api/productos/categorias`, {cache: "no-store"}),
      ]);
      if (rProductos.status === 401 || rProductos.status === 403) {
        throw new Error("Tu sesión venció o no es válida. Volvé a iniciar sesión.");
      }
      if (!rProductos.ok) throw new Error(`No se pudieron cargar tus publicaciones (${rProductos.status}).`);
      setProductos(await rProductos.json());
      if (rCategorias.ok) setCategorias(await rCategorias.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "No fue posible conectar con BazarYa.");
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => { void cargar(); }, [cargar]);

  async function ejecutarAccion(id: number, accion: "eliminar" | "vender") {
    const confirmado = window.confirm(accion === "eliminar" ? "¿Eliminar esta publicación definitivamente?" : "¿Marcar este artículo como vendido?");
    if (!confirmado) return;
    const token = localStorage.getItem("token") || localStorage.getItem("access_token");
    if (!token) { setError("Iniciá sesión para continuar."); return; }
    setError(""); setAviso(""); setGuardando(true);
    try {
      const respuesta = await fetch(`${API}/api/productos/${id}${accion === "vender" ? "/vender" : ""}`, {
        method: accion === "vender" ? "PATCH" : "DELETE",
        headers: {Authorization: `Bearer ${token}`},
      });
      if (!respuesta.ok) {
        const datos = await respuesta.json().catch(() => null);
        throw new Error(typeof datos?.detail === "string" ? datos.detail : `La operación no se completó (${respuesta.status}).`);
      }
      await cargar();
      setAviso(accion === "vender" ? "Producto marcado como vendido." : "Publicación eliminada correctamente.");
    } catch (e) { setError(e instanceof Error ? e.message : "No se pudo completar la operación."); }
    finally { setGuardando(false); }
  }

  function abrirEdicion(p: Producto) {
    setEditando(p.id);
    setAviso("");
    setForm({
      nombre: p.nombre, descripcion: p.descripcion, precio: String(p.precio),
      stock: String(p.stock), categoria_id: String(p.categoria_id ?? p.categoria?.id ?? ""),
    });
  }

  async function guardar(id: number) {
    setAviso("");
    const token = localStorage.getItem("token") || localStorage.getItem("access_token");
    if (!token) { setError("Iniciá sesión para continuar."); return; }
    const precio = Number(form.precio), stock = Number(form.stock), categoria_id = Number(form.categoria_id);
    if (form.nombre.trim().length < 3 || form.descripcion.trim().length < 10 ||
        !Number.isFinite(precio) || precio <= 0 || !Number.isInteger(stock) || stock < 0 ||
        !Number.isInteger(categoria_id) || categoria_id < 1) {
      setError("Revisá el nombre, la descripción, el precio, las existencias y la categoría.");
      return;
    }
    setGuardando(true);
    setError("");
    try {
      const r = await fetch(`${API}/api/productos/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          nombre: form.nombre.trim(), descripcion: form.descripcion.trim(), precio, stock, categoria_id,
        }),
      });
      if (!r.ok) {
        const detalle = await r.json().catch(() => null);
        throw new Error(typeof detalle?.detail === "string" ? detalle.detail : `No se guardó (${r.status}).`);
      }
      setEditando(null);
      await cargar();
      setAviso("Publicación actualizada correctamente.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudieron guardar los cambios.");
    } finally { setGuardando(false); }
  }

  return (
    <main style={{minHeight: "100vh", background: "#f8fafc", color: "#1e293b"}}>
      <header style={{background: "white", borderBottom: "1px solid #e2e8f0", padding: "20px 6%", display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 16}}>
        <Link href="/" style={{fontSize: 28, fontWeight: 700, color: "#2563eb", textDecoration: "none"}}>BazarYa</Link>
        <nav style={{display: "flex", gap: 20}}><Link href="/">Inicio</Link><Link href="/publicaciones">Catálogo</Link><Link href="/create-post">Vender producto</Link><Link href="/profile">Mi perfil</Link></nav>
      </header>
      <section style={{padding: "40px 6%", maxWidth: 1100, margin: "auto"}}>
        <h1 style={{fontSize: 32, fontWeight: 700, color: "#1e3a8a"}}>Mis publicaciones</h1>
        <p style={{color: "#64748b", margin: "12px 0 28px"}}>Consultá y editá los artículos que publicaste.</p>
        {error && <div role="alert" style={{...caja, background: "#fef2f2", color: "#991b1b", marginBottom: 20}}>{error} {error.toLowerCase().includes("sesión") && <Link href="/login">Iniciar sesión</Link>}</div>}
        {aviso && <p role="status" style={{color: "#166534", marginBottom: 20}}>{aviso}</p>}
        {cargando ? <SectionLoading title="Cargando tus publicaciones" subtitle="Estamos consultando los artículos que publicaste en BazarYa." variant="cards" /> : productos.length === 0 ?
          <div style={caja}>No hay publicaciones propias para mostrar. <Link href="/publicaciones">Ver catálogo</Link></div> :
          <div style={{display: "grid", gap: 20}}>
            {productos.map(p => <article key={p.id} style={caja}>
              {editando !== p.id ? <>
                <h2 style={{fontSize: 23, fontWeight: 700}}>{p.nombre}</h2>
                <p style={{marginTop: 10, color: "#475569"}}>{p.descripcion}</p>
                <p style={{marginTop: 12}}>Q {Number(p.precio).toFixed(2)} · Stock: {p.stock}</p>
                <p>Categoría: {p.categoria?.nombre ?? "Sin categoría"} · Estado: {p.estado}</p>
                <div style={{display:"flex",gap:10,flexWrap:"wrap",marginTop:15}}>
                  <button style={boton} onClick={() => abrirEdicion(p)}>Editar publicación</button>
                  {!(["VENDIDO","SOLD","RECHAZADO"].includes(p.estado)) && <button disabled={guardando} style={{...boton,background:"#0f766e"}} onClick={() => void ejecutarAccion(p.id,"vender")}>Marcar vendido</button>}
                  <button disabled={guardando} style={{...boton,background:"#b91c1c"}} onClick={() => void ejecutarAccion(p.id,"eliminar")}>Eliminar</button>
                </div>
              </> :
                <form onSubmit={e => {e.preventDefault(); void guardar(p.id);}} style={{display: "grid", gap: 14}}>
                  <h2 style={{fontSize: 23, fontWeight: 700}}>Editar publicación #{p.id}</h2>
                  <label>Nombre<input style={entrada} required minLength={3} maxLength={150} value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})}/></label>
                  <label>Descripción<textarea style={entrada} required minLength={10} rows={4} value={form.descripcion} onChange={e => setForm({...form, descripcion: e.target.value})}/></label>
                  <label>Precio (Q)<input style={entrada} type="number" required min="0.01" step="0.01" value={form.precio} onChange={e => setForm({...form, precio: e.target.value})}/></label>
                  <label>Existencias<input style={entrada} type="number" required min="0" step="1" value={form.stock} onChange={e => setForm({...form, stock: e.target.value})}/></label>
                  <label>Categoría<select style={entrada} required value={form.categoria_id} onChange={e => setForm({...form, categoria_id: e.target.value})}>
                    <option value="" disabled>Seleccioná una categoría</option>
                    {categorias.map(c => <option key={c.id} value={c.id}>{c.nombre}</option>)}
                  </select></label>
                  <div style={{display: "flex", gap: 12}}>
                    <button disabled={guardando} style={boton} type="submit">{guardando ? "Guardando..." : "Guardar cambios"}</button>
                    <button type="button" onClick={() => setEditando(null)} style={{...boton, background: "#e2e8f0", color: "#1e293b"}}>Cancelar</button>
                  </div>
                </form>}
            </article>)}
          </div>}
      </section>
    </main>
  );
}
