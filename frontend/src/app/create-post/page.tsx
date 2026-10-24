"use client";

import { useEffect, useState, type ChangeEvent, type CSSProperties, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
const MAX_IMAGENES = 5;
const MAX_BYTES = 2 * 1024 * 1024;

type Categoria = { id: number; nombre: string; activo: boolean };
type Imagen = { url_imagen: string; es_principal: boolean };

type Formulario = {
  nombre: string;
  descripcion: string;
  precio: string;
  stock: string;
  categoria_id: string;
};

const campo: CSSProperties = {
  display: "block", width: "100%", padding: "12px 14px", marginTop: 7,
  color: "#1e293b", background: "#fff", borderRadius: 9,
  border: "1px solid #cbd5e1", fontSize: 15, boxSizing: "border-box",
};
const etiqueta: CSSProperties = { display: "block", fontWeight: 600, color: "#334155", fontSize: 14 };
const boton: CSSProperties = {
  padding: "12px 20px", background: "#2563eb", color: "#fff",
  border: 0, borderRadius: 9, cursor: "pointer", fontWeight: 700, fontSize: 15,
};

function detalleError(payload: unknown, status: number): string {
  if (typeof payload === "object" && payload !== null && "detail" in payload) {
    const detail = (payload as { detail?: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail.map((e: { msg?: string }) => e.msg || "Dato inválido").join(". ");
    }
  }
  if (status === 401 || status === 403) return "Tu sesión no es válida. Iniciá sesión nuevamente.";
  return `No se pudo crear la publicación (error ${status}).`;
}

export default function CrearPublicacion() {
  const router = useRouter();
  const [form, setForm] = useState<Formulario>({
    nombre: "", descripcion: "", precio: "", stock: "1", categoria_id: "",
  });
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [imagenes, setImagenes] = useState<Imagen[]>([]);
  const [urlImagen, setUrlImagen] = useState("");
  const [cargandoCategorias, setCargandoCategorias] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");
  const [haySesion, setHaySesion] = useState<boolean | null>(null);

  useEffect(() => {
    setHaySesion(Boolean(localStorage.getItem("token") || localStorage.getItem("access_token")));
    const controller = new AbortController();
    fetch(`${API}/api/productos/categorias`, { signal: controller.signal })
      .then(async r => {
        if (!r.ok) throw new Error("No se pudieron cargar las categorías.");
        return (await r.json()) as Categoria[];
      })
      .then(datos => setCategorias(datos.filter(c => c.activo)))
      .catch(err => {
        if (!controller.signal.aborted) setError(err instanceof Error ? err.message : "Error al cargar categorías.");
      })
      .finally(() => { if (!controller.signal.aborted) setCargandoCategorias(false); });
    return () => controller.abort();
  }, []);

  async function cargarImagenes(e: ChangeEvent<HTMLInputElement>) {
    const archivos = Array.from(e.target.files || []);
    if (!archivos.length) return;
    setError("");
    if (imagenes.length + archivos.length > MAX_IMAGENES) {
      setError(`Solo podés incluir hasta ${MAX_IMAGENES} imágenes.`);
      e.target.value = "";
      return;
    }
    if (archivos.some(a => !["image/jpeg", "image/png", "image/webp", "image/gif"].includes(a.type) || a.size > MAX_BYTES)) {
      setError("Usá imágenes JPG, PNG, WebP o GIF de máximo 2 MB cada una.");
      e.target.value = "";
      return;
    }
    try {
      const nuevas = await Promise.all(archivos.map(archivo => new Promise<Imagen>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve({ url_imagen: String(reader.result), es_principal: false });
        reader.onerror = () => reject(new Error("No se pudo leer una imagen."));
        reader.readAsDataURL(archivo);
      })));
      setImagenes(actuales => [...actuales, ...nuevas].map((img, i) => ({ ...img, es_principal: i === 0 })));
    } catch {
      setError("No se pudieron cargar las imágenes seleccionadas.");
    }
    e.target.value = "";
  }

  function agregarUrl() {
    setError("");
    const url = urlImagen.trim();
    if (imagenes.length >= MAX_IMAGENES) { setError("Ya agregaste el máximo de 5 imágenes."); return; }
    try {
      const parsed = new URL(url);
      if (!["http:", "https:"].includes(parsed.protocol)) throw new Error();
    } catch { setError("Ingresá una URL de imagen http:// o https:// válida."); return; }
    setImagenes(actuales => [...actuales, { url_imagen: url, es_principal: actuales.length === 0 }]);
    setUrlImagen("");
  }

  function quitarImagen(indice: number) {
    setImagenes(actuales => actuales.filter((_, i) => i !== indice).map((img, i) => ({ ...img, es_principal: i === 0 })));
  }

  async function publicar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (guardando) return;
    setError(""); setAviso("");
    const token = localStorage.getItem("token") || localStorage.getItem("access_token");
    if (!token || token === "undefined") { setError("Iniciá sesión antes de publicar un producto."); setHaySesion(false); return; }
    const precio = Number(form.precio);
    const stock = Number(form.stock);
    const categoria_id = Number(form.categoria_id);
    if (form.nombre.trim().length < 3 || form.descripcion.trim().length < 10 ||
        !Number.isFinite(precio) || precio <= 0 || !Number.isInteger(stock) || stock < 1 ||
        !Number.isInteger(categoria_id) || categoria_id < 1 || imagenes.length < 1) {
      setError("Completá el nombre, una descripción de al menos 10 caracteres, precio, stock, categoría y al menos una imagen.");
      return;
    }
    setGuardando(true);
    try {
      const respuesta = await fetch(`${API}/api/productos`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          nombre: form.nombre.trim(), descripcion: form.descripcion.trim(), precio, stock, categoria_id,
          imagenes,
        }),
      });
      const datos: unknown = await respuesta.json().catch(() => null);
      if (!respuesta.ok) throw new Error(detalleError(datos, respuesta.status));
      if (respuesta.status !== 201) throw new Error("La API no confirmó la creación del producto.");
      setAviso("¡Publicación creada! Quedará pendiente de aprobación administrativa. Abriendo tus publicaciones...");
      router.push("/mis-publicaciones");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo conectar con FastAPI.");
    } finally { setGuardando(false); }
  }

  return (
    <main style={{ minHeight: "100vh", background: "#f8fafc", color: "#1e293b" }}>
      <header style={{ background: "white", padding: "20px 6%", borderBottom: "1px solid #e2e8f0", display: "flex", flexWrap: "wrap", gap: 18, alignItems: "center", justifyContent: "space-between" }}>
        <Link href="/" style={{ fontWeight: 800, fontSize: 28, color: "#2563eb", textDecoration: "none" }}>BazarYa</Link>
        <nav style={{ display: "flex", flexWrap: "wrap", gap: 20, alignItems: "center" }}>
          <Link href="/" style={{ color: "#334155" }}>Inicio</Link>
          <Link href="/publicaciones" style={{ color: "#334155" }}>Publicaciones</Link>
          <Link href="/mis-publicaciones" style={{ color: "#334155" }}>Mis publicaciones</Link>
          <Link href="/profile" style={{ color: "#334155" }}>Mi perfil</Link>
        </nav>
      </header>
      <section style={{ padding: "40px 6% 70px", maxWidth: 940, margin: "0 auto" }}>
        <h1 style={{ fontSize: "clamp(26px, 4vw, 36px)", fontWeight: 800, color: "#1e3a8a" }}>Vender un producto</h1>
        <p style={{ color: "#64748b", margin: "12px 0 28px" }}>Publicá tu artículo. Se mostrará en el catálogo después de ser aprobado.</p>
        {haySesion === false && <div role="alert" style={{ padding: 16, background: "#fff7ed", color: "#9a3412", borderRadius: 10, marginBottom: 20 }}>Para vender necesitás una cuenta. <Link href="/login" style={{ fontWeight: 700 }}>Iniciar sesión</Link></div>}
        {error && <div role="alert" style={{ padding: 16, background: "#fef2f2", color: "#991b1b", borderRadius: 10, marginBottom: 20 }}>{error}</div>}
        {aviso && <div role="status" style={{ padding: 16, background: "#f0fdf4", color: "#166534", borderRadius: 10, marginBottom: 20 }}>{aviso}</div>}
        <form onSubmit={publicar} style={{ padding: "clamp(18px, 4vw, 34px)", background: "white", border: "1px solid #e2e8f0", borderRadius: 16, boxShadow: "0 8px 26px rgba(15,23,42,.04)", display: "grid", gap: 21 }}>
          <label style={etiqueta}>Nombre del producto *
            <input style={campo} required minLength={3} maxLength={150} placeholder="Ej. Laptop HP en buen estado" value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} />
          </label>
          <label style={etiqueta}>Descripción *
            <textarea style={campo} required rows={5} minLength={10} placeholder="Describí el estado, características y detalles del artículo" value={form.descripcion} onChange={e => setForm({ ...form, descripcion: e.target.value })} />
          </label>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 18 }}>
            <label style={etiqueta}>Precio en quetzales (Q) *
              <input style={campo} required type="number" min="0.01" step="0.01" placeholder="Ej. 2500.00" value={form.precio} onChange={e => setForm({ ...form, precio: e.target.value })} />
            </label>
            <label style={etiqueta}>Existencias *
              <input style={campo} required type="number" min="1" step="1" value={form.stock} onChange={e => setForm({ ...form, stock: e.target.value })} />
            </label>
            <label style={etiqueta}>Categoría *
              <select style={campo} required disabled={cargandoCategorias} value={form.categoria_id} onChange={e => setForm({ ...form, categoria_id: e.target.value })}>
                <option value="">{cargandoCategorias ? "Cargando categorías..." : "Seleccioná una categoría"}</option>
                {categorias.map(c => <option key={c.id} value={String(c.id)}>{c.nombre}</option>)}
              </select>
            </label>
          </div>
          <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: 23 }}>
            <h2 style={{ fontSize: 19, fontWeight: 700, marginBottom: 8 }}>Imágenes del producto *</h2>
            <p style={{ color: "#64748b", marginBottom: 16, fontSize: 14 }}>Agregá entre 1 y 5 imágenes. La primera será la imagen principal.</p>
            <label style={etiqueta}>Seleccionar fotos desde tu equipo
              <input style={campo} type="file" accept="image/png,image/jpeg,image/webp,image/gif" multiple onChange={cargarImagenes} />
            </label>
            <p style={{ color: "#64748b", fontSize: 13, margin: "8px 0 20px" }}>JPG, PNG, WebP o GIF; máximo 2 MB por imagen.</p>
            <label style={etiqueta}>O utilizar la dirección de una imagen
              <div style={{ display: "flex", flexWrap: "wrap", gap: 10, alignItems: "end" }}>
                <input style={{ ...campo, flex: "1 1 250px" }} type="url" placeholder="https://ejemplo.com/foto.jpg" value={urlImagen} onChange={e => setUrlImagen(e.target.value)} />
                <button type="button" onClick={agregarUrl} style={{ ...boton, background: "#475569" }}>Agregar imagen</button>
              </div>
            </label>
            {imagenes.length > 0 && <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 12, marginTop: 18 }}>
              {imagenes.map((img, index) => <div key={index} style={{ border: "1px solid #e2e8f0", borderRadius: 10, padding: 10 }}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={img.url_imagen} alt={`Imagen ${index + 1} del artículo`} style={{ width: "100%", height: 110, objectFit: "contain", borderRadius: 6 }} />
                <p style={{ fontSize: 12, color: "#64748b", margin: "7px 0" }}>{index === 0 ? "Imagen principal" : `Imagen ${index + 1}`}</p>
                <button type="button" onClick={() => quitarImagen(index)} style={{ border: 0, background: "none", color: "#b91c1c", cursor: "pointer", fontWeight: 600 }}>Quitar</button>
              </div>)}
            </div>}
          </div>
          <div style={{ padding: 15, borderRadius: 10, background: "#eff6ff", color: "#1e40af", fontSize: 14 }}>
            BazarYa facilita el contacto entre comprador y vendedor. No procesa pagos ni envíos. Las publicaciones nuevas quedan pendientes de aprobación.
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center" }}>
            <button type="submit" disabled={guardando || cargandoCategorias || haySesion !== true} style={{ ...boton, opacity: guardando || cargandoCategorias || haySesion !== true ? 0.6 : 1, cursor: guardando ? "wait" : "pointer" }}>
              {guardando ? "Publicando..." : "Publicar producto"}
            </button>
            <Link href="/mis-publicaciones" style={{ color: "#2563eb", fontWeight: 600 }}>Ver mis publicaciones</Link>
          </div>
        </form>
      </section>
    </main>
  );
}
