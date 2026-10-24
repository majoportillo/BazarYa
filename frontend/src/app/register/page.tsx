
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API = "http://127.0.0.1:8000";

export default function RegisterPage() {
 const router = useRouter();

 const [formData, setFormData] = useState({
  nombre_completo: "",
  email: "",
  telefono: "",
  password: "",
 });

 const [loading, setLoading] = useState(false);
 const [error, setError] = useState("");

 const handleChange = (
     e: React.ChangeEvent<HTMLInputElement>
 ) => {
  const { name, value } = e.target;

  setFormData((prev) => ({
   ...prev,
   [name]: value,
  }));
 };

 const handleSubmit = async (
     e: React.FormEvent<HTMLFormElement>
 ) => {
  e.preventDefault();
  setError("");
  setLoading(true);

  try {
   const response = await fetch(`${API}/auth/register`, {
    method: "POST",
    headers: {
     "Content-Type": "application/json",
    },
    body: JSON.stringify({
     ...formData,
     nombre_completo: formData.nombre_completo.trim(),
     email: formData.email.trim().toLowerCase(),
     telefono: formData.telefono.trim(),
    }),
   });

   const data = await response.json().catch(() => null);

   if (!response.ok) {
    const detail = data?.detail;

    const mensaje =
        typeof detail === "string"
            ? detail
            : Array.isArray(detail)
                ? detail.map((item) => item.msg).join(", ")
                : "No se pudo crear la cuenta.";

    throw new Error(mensaje);
   }

   // Registro exitoso: ir a iniciar sesión.
   router.push("/login");
  } catch (err) {
   setError(
       err instanceof Error
           ? err.message
           : "No se pudo conectar con el servidor."
   );
  } finally {
   setLoading(false);
  }
 };

 const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "12px 14px",
  border: "1px solid #cbd5e1",
  borderRadius: 9,
  fontSize: 15,
  color: "#172554",
  background: "#fff",
  outlineColor: "#2563eb",
  marginTop: 7,
 };

 const labelStyle: React.CSSProperties = {
  display: "block",
  fontWeight: 600,
  fontSize: 14,
  color: "#172554",
  marginBottom: 17,
 };

 return (
     <main
         style={{
          minHeight: "100vh",
          background: "#f1f5f9",
          padding: "40px 16px",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          color: "#172554",
         }}
     >
      <div
          style={{
           width: "100%",
           maxWidth: 450,
           background: "#fff",
           padding: 32,
           borderRadius: 15,
           boxShadow: "0 10px 35px rgba(15,23,42,.08)",
          }}
      >
       <Link
           href="/"
           style={{
            color: "#2563eb",
            fontSize: 25,
            fontWeight: 800,
            textDecoration: "none",
           }}
       >
        BazarYa
       </Link>

       <h1
           style={{
            fontSize: 28,
            fontWeight: 800,
            marginTop: 22,
            marginBottom: 6,
           }}
       >
        Crear cuenta
       </h1>

       <p
           style={{
            color: "#64748b",
            marginBottom: 24,
           }}
       >
        Registrate para publicar y vender en BazarYa.
       </p>

       {error && (
           <div
               role="alert"
               style={{
                background: "#fef2f2",
                color: "#b91c1c",
                padding: 14,
                borderRadius: 9,
                marginBottom: 20,
               }}
           >
            {error}
           </div>
       )}

       <form onSubmit={handleSubmit}>
        <label style={labelStyle}>
         Nombre completo
         <input
             style={inputStyle}
             type="text"
             name="nombre_completo"
             value={formData.nombre_completo}
             onChange={handleChange}
             minLength={2}
             maxLength={100}
             required
             placeholder="Tu nombre completo"
         />
        </label>

        <label style={labelStyle}>
         Correo electrónico
         <input
             style={inputStyle}
             type="email"
             name="email"
             value={formData.email}
             onChange={handleChange}
             required
             placeholder="correo@ejemplo.com"
         />
        </label>

        <label style={labelStyle}>
         Teléfono
         <input
             style={inputStyle}
             type="tel"
             name="telefono"
             value={formData.telefono}
             onChange={handleChange}
             minLength={8}
             maxLength={20}
             required
             placeholder="Número de teléfono"
         />
        </label>

        <label style={labelStyle}>
         Contraseña
         <input
             style={inputStyle}
             type="password"
             name="password"
             value={formData.password}
             onChange={handleChange}
             minLength={8}
             maxLength={72}
             required
             autoComplete="new-password"
             placeholder="Mínimo 8 caracteres"
         />
        </label>

        <button
            type="submit"
            disabled={loading}
            style={{
             width: "100%",
             padding: 14,
             background: loading ? "#93c5fd" : "#2563eb",
             color: "#fff",
             border: "none",
             borderRadius: 9,
             fontWeight: 700,
             fontSize: 16,
             cursor: loading ? "wait" : "pointer",
            }}
        >
         {loading ? "Creando cuenta..." : "Crear cuenta"}
        </button>
       </form>

       <p
           style={{
            textAlign: "center",
            marginTop: 23,
            color: "#64748b",
           }}
       >
        ¿Ya tenés una cuenta?{" "}
        <Link
            href="/login"
            style={{
             color: "#2563eb",
             fontWeight: 700,
            }}
        >
         Iniciar sesión
        </Link>
       </p>
      </div>
     </main>
 );
}
