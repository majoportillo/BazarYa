'use client';
import { useState } from 'react';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';

export default function LoginPage() {
    const [credentials, setCredentials] = useState({
        email: '',
        password: ''
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setCredentials(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log('Credenciales listas para enviar al API:', credentials);
        // La conexión fetch se implementará en la siguiente tarea
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