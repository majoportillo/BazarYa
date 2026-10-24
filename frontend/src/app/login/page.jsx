'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';

export default function LoginPage() {
    const router = useRouter();
    const [credentials, setCredentials] = useState({
        email: '',
        password: ''
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setCredentials(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try {
            // Petición POST al backend (el puerto/ruta exacta puede variar según tu API)
            const response = await fetch('http://localhost:8000/api/usuarios/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials)
            });

            if (response.ok) {
                const data = await response.json();
                
                // Manejo de Sesión (Storage): Guardamos el token y datos del usuario
                localStorage.setItem('token', data.access_token || data.token);
                localStorage.setItem('usuario', JSON.stringify(data.usuario || credentials.email));
                
                alert('¡Inicio de sesión exitoso!');
                // Redirigimos a la pantalla principal
                router.push('/'); 
            } else {
                const errorData = await response.json();
                alert(`Error al ingresar: ${errorData.message || 'Credenciales incorrectas'}`);
            }
        } catch (error) {
            console.error('Error de red:', error);
            alert('Error de conexión con el servidor. Verifica que el backend esté encendido.');
        }
    };

    return (
        <div className="flex justify-content-center align-items-center min-h-screen surface-ground p-3">
            <Card title="Iniciar Sesión en BazarYa" className="w-full max-w-26rem shadow-4">
                <form onSubmit={handleSubmit} className="flex flex-column gap-3">
                    <div className="flex flex-column gap-2">
                        <label htmlFor="email" className="font-bold">Correo Electrónico</label>
                        <InputText 
                            id="email" 
                            name="email" 
                            type="email" 
                            value={credentials.email} 
                            onChange={handleChange} 
                            placeholder="correo@ejemplo.com" 
                            required 
                        />
                    </div>

                    <div className="flex flex-column gap-2">
                        <label htmlFor="password" className="font-bold">Contraseña</label>
                        <InputText 
                            id="password" 
                            name="password" 
                            type="password" 
                            value={credentials.password} 
                            onChange={handleChange} 
                            placeholder="Ingresa tu contraseña" 
                            required 
                        />
                    </div>

                    <Button type="submit" label="Ingresar" icon="pi pi-sign-in" className="mt-2" />
                </form>
            </Card>
        </div>
    );
}