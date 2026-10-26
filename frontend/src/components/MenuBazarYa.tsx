"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

type Estado = { autentificado: boolean; administrador: boolean };
const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function MenuBazarYa() {
  const pathname = usePathname();
  const router = useRouter();
  const [estado, setEstado] = useState<Estado>({ autentificado: false, administrador: false });
  const actualizar = useCallback(async () => {
    const token = localStorage.getItem("token") || localStorage.getItem("access_token");
    if (!token) { setEstado({ autentificado: false, administrador: false }); return; }
    // La API valida el token y el rol real. Nunca confiar solo en el rol guardado en el navegador.
    try {
      const respuesta = await fetch(`${API}/usuarios/me`, {headers:{Authorization:`Bearer ${token}`}, cache:"no-store"});
      if (!respuesta.ok) {
        if (respuesta.status === 401 || respuesta.status === 403) {
          localStorage.removeItem("token");localStorage.removeItem("access_token");localStorage.removeItem("usuario");
          setEstado({autentificado:false,administrador:false});return;
        }
        setEstado({autentificado:true,administrador:false});return;
      }
      const usuario = await respuesta.json();
      setEstado({autentificado:true,administrador:usuario?.rol === "ADMINISTRADOR"});
    } catch {
      // En fallo de red no mostrar acceso administrativo sin verificación.
      setEstado({autentificado:true,administrador:false});
    }
  }, []);
  useEffect(() => {
    void actualizar();
    window.addEventListener("bazarya-auth-change", actualizar);
    window.addEventListener("storage", actualizar);
    const alVolver = () => { void actualizar(); };
    window.addEventListener("focus", alVolver);
    return () => {
      window.removeEventListener("bazarya-auth-change", actualizar);
      window.removeEventListener("storage", actualizar);
      window.removeEventListener("focus", alVolver);
    };
  }, [actualizar, pathname]);
  function cerrarSesion() {
    localStorage.removeItem("token");localStorage.removeItem("access_token");localStorage.removeItem("usuario");
    setEstado({autentificado:false,administrador:false});
    window.dispatchEvent(new Event("bazarya-auth-change"));
    router.replace("/login");router.refresh();
  }
  const enlace = (href:string, texto:string) => <Link href={href} style={{color:pathname===href?"#2563eb":"#334155",fontWeight:pathname===href?700:500,textDecoration:"none",fontSize:15}}>{texto}</Link>;
  return <nav aria-label="Navegación principal" style={{display:"flex",gap:18,alignItems:"center",flexWrap:"wrap"}}>
    {enlace("/", "Inicio")}
    {enlace("/publicaciones", "Publicaciones")}
    {estado.autentificado ? <>
      {enlace("/create-post", "+ Publicar")}
      {enlace("/mis-publicaciones", "Mis publicaciones")}
      {enlace("/profile", "Mi perfil")}
      {estado.administrador && enlace("/admin", "Administración")}
      <button type="button" onClick={cerrarSesion} style={{background:"transparent",border:0,padding:0,cursor:"pointer",color:"#b91c1c",fontSize:15,fontWeight:600}}>Cerrar sesión</button>
    </> : <>
      {enlace("/login", "Iniciar sesión")}
      {enlace("/register", "Registrarse")}
    </>}
  </nav>;
}
