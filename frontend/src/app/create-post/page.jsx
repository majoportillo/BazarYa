'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

// PrimeReact UI Components
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { InputNumber } from 'primereact/inputnumber';
import { Dropdown } from 'primereact/dropdown';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';

// Importación de estilos PrimeReact (requeridos para que los componentes se vean limpios)
import 'primereact/resources/themes/lara-light-indigo/theme.css';
import 'primereact/resources/primereact.min.css';
import 'primeicons/primeicons.css';

export default function CreatePostPage() {
    const router = useRouter();

    // Opciones de categorías (Mapeadas a los IDs esperados por la base de datos)
    const categorias = [
        { label: 'Electrónica', value: 1 },
        { label: 'Ropa', value: 2 },
        { label: 'Hogar', value: 3 },
        { label: 'Otros', value: 4 }
    ];

    const [postData, setPostData] = useState({
        nombre: '',
        descripcion: '',
        precio: null,
        categoria_id: null,
        imagen_url: '' 
    });

    const [loading, setLoading] = useState(false);

    // Verificación de sesión de usuario (AC-01)
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

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!postData.categoria_id) {
            alert('Por favor, selecciona una categoría.');
            return;
        }

        setLoading(true);

        try {
            const token = localStorage.getItem('token');
            
            // Petición al backend FastAPI
            const response = await fetch('http://localhost:8000/api/productos/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    nombre: postData.nombre,
                    descripcion: postData.descripcion,
                    precio: postData.precio,
                    categoria_id: postData.categoria_id,
                    imagenes: postData.imagen_url ? [{ url: postData.imagen_url, es_principal: true }] : []
                })
            });

            if (response.ok) {
                alert('¡Publicación creada exitosamente! Quedó en estado pendiente de aprobación.');
                setPostData({ nombre: '', descripcion: '', precio: null, categoria_id: null, imagen_url: '' });
                router.push('/mis-publicaciones');
            } else {
                const errorData = await response.json();
                const mensaje = errorData.detail 
                    ? (Array.isArray(errorData.detail) ? errorData.detail[0].msg : errorData.detail)
                    : 'Revisa los datos ingresados';
                alert(`Error al crear publicación: ${mensaje}`);
            }
        } catch (error) {
            console.error('Error de red:', error);
            alert('Error de conexión con el servidor. Verifica que FastAPI esté corriendo en http://localhost:8000');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex justify-center p-6 min-h-screen bg-gray-50">
            <Card title="Crear Nueva Publicación" className="w-full max-w-2xl shadow-md p-4 bg-white rounded-lg">
                <form onSubmit={handleSubmit} className="flex flex-col gap-5">
                    
                    {/* Título / Nombre */}
                    <div className="flex flex-col gap-2">
                        <label htmlFor="nombre" className="font-semibold text-gray-700">Título de la Publicación *</label>
                        <InputText 
                            id="nombre" 
                            name="nombre" 
                            value={postData.nombre} 
                            onChange={handleChange} 
                            placeholder="Ej. Bicicleta de montaña"
                            className="p-inputtext-sm w-full border p-2 rounded"
                            required 
                        />
                    </div>

                    {/* Descripción */}
                    <div className="flex flex-col gap-2">
                        <label htmlFor="descripcion" className="font-semibold text-gray-700">Descripción *</label>
                        <InputTextarea 
                            id="descripcion" 
                            name="descripcion" 
                            value={postData.descripcion} 
                            onChange={handleChange} 
                            rows={4} 
                            placeholder="Describe los detalles de tu artículo..."
                            className="w-full border p-2 rounded"
                            required 
                        />
                    </div>

                    {/* Precio y Categoría */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="flex flex-col gap-2">
                            <label htmlFor="precio" className="font-semibold text-gray-700">Precio (Q) *</label>
                            <InputNumber 
                                inputId="precio" 
                                value={postData.precio} 
                                onValueChange={(e) => setPostData(prev => ({...prev, precio: e.value}))} 
                                mode="currency" 
                                currency="GTQ" 
                                locale="es-GT"
                                placeholder="Q0.00"
                                className="w-full"
                                inputClassName="w-full border p-2 rounded"
                                required 
                            />
                        </div>
                        <div className="flex flex-col gap-2">
                            <label htmlFor="categoria_id" className="font-semibold text-gray-700">Categoría *</label>
                            <Dropdown 
                                id="categoria_id" 
                                value={postData.categoria_id} 
                                onChange={(e) => setPostData(prev => ({ ...prev, categoria_id: e.value }))} 
                                options={categorias} 
                                placeholder="Selecciona una categoría" 
                                className="w-full border rounded" 
                                required
                            />
                        </div>
                    </div>

                    {/* URL de la Imagen */}
                    <div className="flex flex-col gap-2">
                        <label htmlFor="imagen_url" className="font-semibold text-gray-700">URL de la Imagen</label>
                        <InputText 
                            id="imagen_url" 
                            name="imagen_url" 
                            value={postData.imagen_url} 
                            onChange={handleChange} 
                            placeholder="https://ejemplo.com/imagen.jpg"
                            className="p-inputtext-sm w-full border p-2 rounded"
                        />
                    </div>

                    {/* Botón Guardar */}
                    <Button 
                        type="submit" 
                        label={loading ? "Guardando..." : "Crear Publicación"} 
                        icon={loading ? "pi pi-spin pi-spinner" : "pi pi-check"} 
                        disabled={loading}
                        className="mt-4 bg-blue-600 text-white font-bold p-3 rounded hover:bg-blue-700 transition-colors w-full" 
                    />
                </form>
            </Card>
        </div>
    );
}