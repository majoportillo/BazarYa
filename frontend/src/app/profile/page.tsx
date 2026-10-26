'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { SectionLoading } from '@/components/LoadingBazarYa';

type Usuario = {
  nombre_completo?: string;
  nombre?: string;
  email?: string;
  telefono?: string;
  rol?: string;
};

const API = 'http://127.0.0.1:8000';

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<Usuario | null>(null);
  const [hasToken, setHasToken] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    setHasToken(Boolean(token));

    if (!token) {
      setReady(true);
      return;
    }

    fetch(`${API}/usuarios/me`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: 'no-store',
    })
      .then(async (response) => {
        if (!response.ok) throw new Error('No fue posible obtener el perfil.');
        return response.json();
      })
      .then((datos: Usuario) => {
        setUser(datos);
        localStorage.setItem('usuario', JSON.stringify(datos));
      })
      .catch(() => {
        try {
          const raw = localStorage.getItem('usuario');
          if (raw) setUser(JSON.parse(raw) as Usuario);
        } catch {
          // Datos locales inválidos.
        }
      })
      .finally(() => setReady(true));
  }, []);

  function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('usuario');
    router.push('/login');
    router.refresh();
  }

  const line = (label: string, value?: string) => (
    <div
      style={{
        borderBottom: '1px solid #edf2f7',
        padding: '12px 0',
      }}
    >
      <div style={{ fontSize: 13, color: '#64748b', marginBottom: 5 }}>{label}</div>
      <div style={{ fontSize: 16, fontWeight: 600 }}>{value || 'No disponible en la sesión'}</div>
    </div>
  );

  return (
    <main style={{ minHeight: '100vh', background: '#f3f6fb', color: '#172b4d' }}>
      <header
        style={{
          background: '#fff',
          padding: '18px 6%',
          borderBottom: '1px solid #e2e8f0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: 12,
          flexWrap: 'wrap',
        }}
      >
        <Link
          href="/"
          style={{ fontSize: 27, fontWeight: 800, color: '#2563eb', textDecoration: 'none' }}
        >
          BazarYa
        </Link>

        <nav style={{ display: 'flex', gap: 18, flexWrap: 'wrap' }}>
          <Link href="/publicaciones">Catálogo</Link>
          <Link href="/mis-publicaciones">Mis publicaciones</Link>
          <Link href="/create-post">Vender producto</Link>
        </nav>
      </header>

      <section style={{ maxWidth: 750, margin: '50px auto', padding: '0 18px' }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, marginBottom: 10 }}>Mi perfil</h1>
        <p style={{ color: '#64748b', marginBottom: 25 }}>
          Información disponible de tu cuenta de BazarYa.
        </p>

        <div
          style={{
            background: '#fff',
            padding: 30,
            borderRadius: 15,
            border: '1px solid #e2e8f0',
            boxShadow: '0 9px 30px #102b500f',
          }}
        >
          {!ready ? (
            <SectionLoading
              title="Cargando tu perfil"
              subtitle="Estamos consultando los datos de tu cuenta para mostrarlos en pantalla."
              variant="contact"
            />
          ) : !hasToken ? (
            <>
              <p style={{ color: '#9a3412' }}>Necesitás iniciar sesión para consultar tu perfil.</p>
              <Link href="/login" style={{ color: '#2563eb', fontWeight: 700 }}>
                Iniciar sesión
              </Link>
            </>
          ) : (
            <>
              {!user ? (
                <p style={{ color: '#9a3412' }}>
                  Hay una sesión guardada, pero el servidor no proporcionó datos del usuario.
                </p>
              ) : (
                <>
                  {line('Nombre completo', user.nombre_completo || user.nombre)}
                  {line('Correo electrónico', user.email)}
                  {line('Teléfono', user.telefono)}
                  {line('Rol', user.rol)}
                </>
              )}

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 25 }}>
                <Link
                  href="/mis-publicaciones"
                  style={{
                    background: '#2563eb',
                    padding: '12px 18px',
                    borderRadius: 8,
                    color: '#fff',
                    textDecoration: 'none',
                    fontWeight: 700,
                  }}
                >
                  Mis publicaciones
                </Link>

                <button
                  onClick={logout}
                  style={{
                    background: '#fff',
                    border: '1px solid #cbd5e1',
                    padding: '12px 18px',
                    borderRadius: 8,
                    cursor: 'pointer',
                    fontWeight: 700,
                  }}
                >
                  Cerrar sesión
                </button>
              </div>
            </>
          )}
        </div>
      </section>
    </main>
  );
}
