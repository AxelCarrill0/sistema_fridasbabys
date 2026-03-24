# Guía de Configuración del Proyecto - Sistema FridasBabys

Esta guía detalla los pasos necesarios para recrear el entorno de desarrollo desde cero en una nueva máquina.

## 1. Requisitos Previos

Asegúrate de tener instalado lo siguiente:
- **Python 3.10+** (Recomendado 3.12)
- **PostgreSQL 15+**
- **Git**

## 2. Configuración del Entorno Virtual

Desde la raíz del proyecto, ejecuta los siguientes comandos en tu terminal (PowerShell o CMD):

```bash
# Crear el entorno virtual
python -m venv .venv

# Activar el entorno virtual (Windows)
.\.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## 3. Configuración de la Base de Datos

El proyecto utiliza **PostgreSQL**. Sigue estos pasos para configurar la base de datos:

1.  Asegúrate de que el servicio de PostgreSQL esté corriendo.
2.  Crea una base de datos llamada `bd_sistema_fb`:
    ```sql
    CREATE DATABASE bd_sistema_fb;
    ```
3.  El usuario configurado por defecto es `postgres` con la contraseña `A001`. Si tienes una configuración distinta, actualiza los valores en `Sistema_FridasBabys/settings.py` dentro de la sección `DATABASES`.

## 4. Migraciones y Datos Iniciales

Una vez configurada la base de datos y activado el entorno virtual, aplica las migraciones de Django:

```bash
python manage.py makemigrations
python manage.py migrate
```

Para crear un usuario administrador:
```bash
python manage.py createsuperuser
```

## 5. Ejecutar el Servidor de Desarrollo

Para iniciar el proyecto localmente:

```bash
python manage.py runserver
```

El sistema estará disponible en `http://127.0.0.1:8000/`.

## Estructura del Proyecto

- `core/`: Contiene las aplicaciones principales (usuarios, pedidos, productos, etc.).
- `media/`: Directorio para archivos subidos (imágenes de productos).
- `static/`: Archivos CSS, JS e imágenes estáticas.
- `templates/`: Plantillas HTML.

---
*Nota: Esta guía fue generada automáticamente para facilitar la migración y el despliegue del sistema.*
