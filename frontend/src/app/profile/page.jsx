'use client';
import { useState, useEffect } from 'react';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';

export default function ProfilePage() {
    const [user, setUser] = useState({
        nombre: 'Nombre de Usuario',
        email: 'prueba@ejemplo.com',
        telefono: '12345678'
    });

    
    useEffect(() => {
        const storedUser = localStorage.getItem('usuario');
        if (storedUser) {
           
            console.log('Usuario cargado:', storedUser);
        }
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setUser(prev => ({ ...prev, [name]: value }));
    };

    const handleUpdate = (e) => {
        e.preventDefault();
        
        console.log('Información actualizada:', user);
        alert('Perfil actualizado (Simulación)');
    };

    return (
        <div className="flex justify-content-center p-4 min-h-screen surface-ground">
            <Card title="Mi Perfil Privado" className="w-full max-w-30rem shadow-4">
                <form onSubmit={handleUpdate} className="flex flex-column gap-3">
                    <div className="flex flex-column gap-2">
                        <label htmlFor="nombre" className="font-bold">Nombre Completo</label>
                        <InputText 
                            id="nombre" 
                            name="nombre" 
                            value={user.nombre} 
                            onChange={handleChange} 
                            required 
                        />
                    </div>

                    <div className="flex flex-column gap-2">
                        <label htmlFor="email" className="font-bold">Correo Electrónico</label>
                        <InputText 
                            id="email" 
                            name="email" 
                            value={user.email} 
                            onChange={handleChange}
                        />
                    </div>
                    
                    <div className="flex flex-column gap-2">
                        <label htmlFor="telefono" className="font-bold">Teléfono de Contacto</label>
                        <InputText 
                            id="telefono" 
                            name="telefono" 
                            value={user.telefono} 
                            onChange={handleChange} 
                        />
                    </div>

                    <Button type="submit" label="Actualizar Perfil" icon="pi pi-save" className="mt-2" />
                </form>
            </Card>
        </div>
    );
}