'use client';
import { useState } from 'react';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';

export default function RegisterPage() {
    const [formData, setFormData] = useState({
        nombre: '',
        email: '',
        password: ''
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log('Datos listos para enviar:', formData);
    };

    return (
        <div className="flex justify-content-center align-items-center min-h-screen surface-ground p-3">
            <Card title="Crear Cuenta en BazarYa" className="w-full max-w-26rem shadow-4">
                <form onSubmit={handleSubmit} className="flex flex-column gap-3">
                    <div className="flex flex-column gap-2">
                        <label htmlFor="nombre" className="font-bold">Nombre Completo</label>
                        <InputText 
                            id="nombre" 
                            name="nombre" 
                            value={formData.nombre} 
                            onChange={handleChange} 
                            placeholder="Ej. Ergil Cárdenas" 
                            required 
                        />
                    </div>

                    <div className="flex flex-column gap-2">
                        <label htmlFor="email" className="font-bold">Correo Electrónico</label>
                        <InputText 
                            id="email" 
                            name="email" 
                            type="email" 
                            value={formData.email} 
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
                            value={formData.password} 
                            onChange={handleChange} 
                            placeholder="Mínimo 6 caracteres" 
                            required 
                            minLength={6}
                        />
                    </div>

                    <Button type="submit" label="Registrarse" icon="pi pi-user-plus" className="mt-2" />
                </form>
            </Card>
        </div>
    );
}