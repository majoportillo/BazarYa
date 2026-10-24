'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { InputNumber } from 'primereact/inputnumber';
import { Dropdown } from 'primereact/dropdown';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';

export default function CreatePostPage() {
    const router = useRouter();
    // Categorías de ejemplo
    const categorias = [
        { label: 'Electrónica', value: 'electronica' },
        { label: 'Ropa', value: 'ropa' },
        { label: 'Hogar', value: 'hogar' },
        { label: 'Otros', value: 'otros' }
    ];

    const [postData, setPostData] = useState({
        titulo: '',
        descripcion: '',
        precio: null,
        categoria: null,
        imagenUrl: '' 
    });

    // Verificación de usuario autenticado (AC-01)
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            alert('Debes iniciar sesión para crear una publicación.');
            router.push('/login');
        }
    }, [router]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setPostData(prev => ({ ...prev, [name]: value }));
    };

    const handleDropdownChange = (e) => {
         setPostData(prev => ({ ...prev, categoria: e.value }));
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try {
            
            const token = localStorage.getItem('token');
            
            
            const response = await fetch('http://localhost:8000/api/publicaciones', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` // Enviamos el pase de seguridad
                },
                body: JSON.stringify(postData)
            });

            if (response.ok) {
                alert('¡Publicación creada con éxito!');
                // Limpiamos el formulario
                setPostData({ titulo: '', descripcion: '', precio: null, categoria: null, imagenUrl: '' });
                
            } else {
                const errorData = await response.json();
                alert(`Error al crear: ${errorData.message || 'Revisa los datos ingresados'}`);
            }
        } catch (error) {
            console.error('Error de red:', error);
            alert('Error de conexión. Asegúrate de que el backend esté encendido.');
        }
    };

    return (
        <div className="flex justify-content-center p-4 min-h-screen surface-ground">
            <Card title="Crear Nueva Publicación" className="w-full max-w-40rem shadow-4">
                <form onSubmit={handleSubmit} className="flex flex-column gap-4">
                    <div className="flex flex-column gap-2">
                        <label htmlFor="titulo" className="font-bold">Título de la Publicación *</label>
                        <InputText 
                            id="titulo" 
                            name="titulo" 
                            value={postData.titulo} 
                            onChange={handleChange} 
                            placeholder="Ej. Bicicleta de montaña"
                            required 
                        />
                    </div>

                    <div className="flex flex-column gap-2">
                        <label htmlFor="descripcion" className="font-bold">Descripción *</label>
                        <InputTextarea 
                            id="descripcion" 
                            name="descripcion" 
                            value={postData.descripcion} 
                            onChange={handleChange} 
                            rows={4} 
                            placeholder="Describe los detalles de tu artículo..."
                            required 
                        />
                    </div>

                    <div className="flex gap-4">
                         <div className="flex flex-column gap-2 flex-1">
                            <label htmlFor="precio" className="font-bold">Precio (Q) *</label>
                            <InputNumber 
                                inputId="precio" 
                                value={postData.precio} 
                                onValueChange={(e) => setPostData(prev => ({...prev, precio: e.value}))} 
                                mode="currency" 
                                currency="GTQ" 
                                locale="es-GT"
                                required 
                            />
                        </div>
                        <div className="flex flex-column gap-2 flex-1">
                            <label htmlFor="categoria" className="font-bold">Categoría *</label>
                            <Dropdown 
                                id="categoria" 
                                value={postData.categoria} 
                                onChange={handleDropdownChange} 
                                options={categorias} 
                                placeholder="Selecciona una categoría" 
                                className="w-full" 
                                required
                            />
                        </div>
                    </div>

                     <div className="flex flex-column gap-2">
                        <label htmlFor="imagenUrl" className="font-bold">URL de la Imagen</label>
                        <InputText 
                            id="imagenUrl" 
                            name="imagenUrl" 
                            value={postData.imagenUrl} 
                            onChange={handleChange} 
                            placeholder="https://ejemplo.com/imagen.jpg"
                        />
                    </div>

                    <Button type="submit" label="Crear Publicación" icon="pi pi-check" className="mt-4" />
                </form>
            </Card>
        </div>
    );
}