'use client';
import { useState, type FormEvent, type CSSProperties } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
const API = 'http://127.0.0.1:8000';
const input: CSSProperties = { width:'100%', padding:'12px 14px', border:'1px solid #cbd5e1', borderRadius:9, fontSize:15, color:'#0f172a', background:'#fff', boxSizing:'border-box' };
export default function LoginPage() {
  const router = useRouter();
  const [email,setEmail]=useState('');
  const [password,setPassword]=useState('');
  const [error,setError]=useState('');
  const [busy,setBusy]=useState(false);
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();setError('');setBusy(true);
    try {
      const res=await fetch(`${API}/auth/login`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email.trim().toLowerCase(),password})});
      const data=await res.json().catch(()=>null);
      if(!res.ok) throw new Error(typeof data?.detail==='string'?data.detail:'No se pudo iniciar sesión. Revisá tus credenciales.');
      const token=data?.access_token??data?.token;
      if(typeof token!=='string'||!token) throw new Error('El servidor aceptó las credenciales pero no devolvió un token de sesión. Hay que revisar la respuesta de /auth/login.');
      localStorage.setItem('token',token);
      if(data?.usuario && typeof data.usuario==='object') localStorage.setItem('usuario',JSON.stringify(data.usuario));
      else localStorage.removeItem('usuario');
      router.push('/mis-publicaciones'); router.refresh();
    } catch(err){setError(err instanceof Error?err.message:'No fue posible conectar con el servidor.');} finally{setBusy(false);}
  }
  return <main style={{minHeight:'100vh',background:'#f3f6fb',color:'#172b4d'}}>
    <header style={{background:'#fff',padding:'18px 6%',borderBottom:'1px solid #e2e8f0',display:'flex',justifyContent:'space-between',alignItems:'center'}}><Link href="/" style={{fontSize:27,fontWeight:800,color:'#2563eb',textDecoration:'none'}}>BazarYa</Link><Link href="/publicaciones" style={{color:'#334155',textDecoration:'none'}}>Ver catálogo</Link></header>
    <section style={{maxWidth:440,margin:'60px auto',padding:'0 18px'}}><div style={{background:'#fff',padding:32,borderRadius:16,boxShadow:'0 9px 30px #102b5012',border:'1px solid #e2e8f0'}}>
      <h1 style={{fontSize:29,fontWeight:800,margin:'0 0 8px'}}>Iniciar sesión</h1><p style={{color:'#64748b',margin:'0 0 24px'}}>Ingresá a tu cuenta de BazarYa.</p>
      {error&&<div role="alert" style={{background:'#fef2f2',color:'#991b1b',padding:12,borderRadius:8,marginBottom:16}}>{error}</div>}
      <form onSubmit={submit} style={{display:'grid',gap:18}}><label style={{display:'grid',gap:7,fontWeight:600}}>Correo electrónico<input style={input} type="email" placeholder="correo@ejemplo.com" value={email} onChange={e=>setEmail(e.target.value)} autoComplete="email" required /></label><label style={{display:'grid',gap:7,fontWeight:600}}>Contraseña<input style={input} type="password" placeholder="Ingresá tu contraseña" value={password} onChange={e=>setPassword(e.target.value)} autoComplete="current-password" required /></label><button disabled={busy} style={{padding:'13px',background:'#2563eb',border:0,borderRadius:9,color:'#fff',fontSize:16,fontWeight:700,cursor:'pointer'}}>{busy?'Ingresando...':'Ingresar'}</button></form>
      <p style={{marginTop:24,textAlign:'center',color:'#64748b'}}>¿No tenés cuenta? <Link href="/register" style={{color:'#2563eb',fontWeight:700}}>Registrate</Link></p>
    </div></section></main>;
}
