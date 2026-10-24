"use client";

import MenuBazarYa from "../../components/MenuBazarYa";
import { useCallback, useEffect, useState } from "react";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
type Imagen = { id: number; url_imagen: string; es_principal: boolean };
type Producto = { id: number; nombre: string; descripcion: string; precio: string | number; stock: number; estado: string; imagenes: Imagen[]; categoria?: { nombre: string } };
const btn: React.CSSProperties = {background: "#2563eb",border:0,borderRadius:8,padding:"11px 17px",fontWeight:700,color:"white",cursor:"pointer"};
const card: React.CSSProperties = {background:"white",border:"1px solid #e2e8f0",borderRadius:14,padding:22};

export default function Administracion() {
  const [productos, setProductos] = useState<Producto[]>([]);
  const [cargando, setCargando] = useState(true);
  const [procesando, setProcesando] = useState<number|null>(null);
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");
  const [sinSesion, setSinSesion] = useState(false);
  const cargar = useCallback(async () => {
    setCargando(true);setError("");
    const token = localStorage.getItem("token") || localStorage.getItem("access_token");
    if (!token) {setSinSesion(true);setCargando(false);return;}
    setSinSesion(false);
    try {
      const res = await fetch(`${API}/api/productos/admin/pendientes?limit=100`,{headers:{Authorization:`Bearer ${token}`},cache:"no-store"});
      if (res.status === 403) throw new Error("Acceso restringido: esta sección es exclusiva para administradores.");
      if (res.status === 401) throw new Error("Tu sesión venció. Volvé a iniciar sesión.");
      if (!res.ok) throw new Error(`No fue posible consultar los productos pendientes (${res.status}).`);
      setProductos(await res.json());
    } catch(e) {setError(e instanceof Error ? e.message : "Error de conexión.");setProductos([]);}
    finally {setCargando(false);}
  },[]);
  useEffect(()=>{void cargar();},[cargar]);
  async function moderar(p:Producto,estado:"ACTIVO"|"RECHAZADO") {
    const motivo_rechazo=estado==="RECHAZADO"?window.prompt(`Motivo de rechazo para «${p.nombre}»:`):null;
    if (estado==="RECHAZADO" && (motivo_rechazo===null || !motivo_rechazo.trim())) return;
    if (estado==="ACTIVO" && !window.confirm(`¿Aprobar «${p.nombre}» para el catálogo público?`)) return;
    const token=localStorage.getItem("token")||localStorage.getItem("access_token");
    if (!token) {setError("Iniciá sesión para continuar.");return;}
    setError("");setAviso("");setProcesando(p.id);
    try {
      const res=await fetch(`${API}/api/productos/admin/${p.id}/moderar`,{method:"PATCH",headers:{"Content-Type":"application/json",Authorization:`Bearer ${token}`},body:JSON.stringify({estado,motivo_rechazo:motivo_rechazo||null})});
      if (!res.ok) {const data=await res.json().catch(()=>null);throw new Error(typeof data?.detail==="string"?data.detail:`Error ${res.status} al moderar.`);}
      setAviso(`Publicación «${p.nombre}» ${estado==="ACTIVO"?"aprobada":"rechazada"} correctamente.`);
      await cargar();
    } catch(e){setError(e instanceof Error?e.message:"No fue posible moderar la publicación.");}
    finally {setProcesando(null);}
  }
  return <main style={{minHeight:"100vh",background:"#f8fafc",color:"#1e293b"}}>
    <header style={{background:"white",borderBottom:"1px solid #e2e8f0",padding:"20px 6%",display:"flex",justifyContent:"space-between",gap:20,flexWrap:"wrap",alignItems:"center"}}>
      <Link href="/" style={{fontSize:28,fontWeight:800,color:"#2563eb",textDecoration:"none"}}>BazarYa</Link>
      <MenuBazarYa />
    </header>
    <section style={{maxWidth:1100,margin:"auto",padding:"45px 6%"}}>
      <h1 style={{fontSize:33,fontWeight:800,color:"#1e3a8a"}}>Moderación de publicaciones</h1>
      <p style={{margin:"10px 0 30px",color:"#64748b"}}>Revisá los productos pendientes antes de que aparezcan en el catálogo público. Solo los administradores pueden aprobar o rechazar.</p>
      {sinSesion&&<div style={{...card,background:"#fff7ed"}}>Necesitás iniciar sesión. <Link href="/login">Ingresar</Link></div>}
      {error&&<div role="alert" style={{...card,background:"#fef2f2",color:"#991b1b",marginBottom:16}}>{error}</div>}
      {aviso&&<div role="status" style={{...card,background:"#f0fdf4",color:"#166534",marginBottom:16}}>{aviso}</div>}
      {cargando?<p>Cargando publicaciones pendientes...</p>:!error&&!sinSesion&&productos.length===0?<div style={card}>No hay publicaciones pendientes de moderación.</div>:<div style={{display:"grid",gap:18}}>
        {productos.map(p=><article key={p.id} style={card}>
          <div style={{display:"flex",gap:18,flexWrap:"wrap"}}>
            {p.imagenes?.[0]&&<img src={p.imagenes[0].url_imagen} alt={`Imagen de ${p.nombre}`} style={{width:145,height:130,objectFit:"contain",borderRadius:8}}/>}
            <div style={{flex:1,minWidth:230}}>
              <h2 style={{fontSize:22,fontWeight:700}}>{p.nombre} <span style={{fontSize:13,color:"#64748b"}}>#{p.id}</span></h2>
              <p style={{margin:"10px 0",color:"#475569",whiteSpace:"pre-wrap"}}>{p.descripcion}</p>
              <p style={{fontWeight:700}}>Q {Number(p.precio).toFixed(2)} · Existencias: {p.stock}</p>
              <p style={{color:"#64748b"}}>Categoría: {p.categoria?.nombre||"Sin categoría"} · Estado: {p.estado}</p>
              {p.imagenes?.length>1&&<p style={{color:"#64748b"}}>{p.imagenes.length} imágenes adjuntas</p>}
            </div>
          </div>
          <div style={{display:"flex",gap:12,marginTop:22,flexWrap:"wrap"}}>
            <button disabled={procesando!==null} onClick={()=>void moderar(p,"ACTIVO")} style={{...btn,background:"#15803d",opacity:procesando!==null ? 0.6 : 1}}>Aprobar</button>
            <button disabled={procesando!==null} onClick={()=>void moderar(p,"RECHAZADO")} style={{...btn,background:"#b91c1c",opacity:procesando!==null ? 0.6 : 1}}>Rechazar</button>
          </div>
        </article>)}
      </div>}
      <button onClick={()=>void cargar()} style={{...btn,marginTop:26,background:"#475569"}}>Actualizar listado</button>
    </section>
  </main>;
}
