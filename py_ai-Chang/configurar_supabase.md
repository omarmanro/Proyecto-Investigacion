"""
Guía paso a paso para encontrar y configurar las credenciales de Supabase.

1. Obtener credenciales de Supabase:

   - Accede a https://supabase.com/ e inicia sesión
   - Selecciona tu proyecto
   - Ve a "Settings" (Configuración) > "API"
   - Ahí encontrarás:
     - "Project URL" (URL del proyecto) → SUPABASE_URL
     - "anon public" (clave pública para operaciones anónimas) → SUPABASE_KEY
     - "service_role" (clave con privilegios elevados) → SUPABASE_SERVICE_ROLE_KEY

2. Obtener credenciales de conexión directa a PostgreSQL:

   - En la misma página de configuración, ve a "Settings" > "Database"
   - En la sección "Connection Info" o "Connection Pooling" encontrarás:
     - "Host" → DB_SERVER
     - "Database name" → DB_DATABASE (generalmente es "postgres")
     - "Port" → DB_PORT (generalmente es 5432)
     - "User" → DB_USERNAME (generalmente es "postgres")
     - "Password" → DB_PASSWORD (la que estableciste al crear el proyecto)

3. Actualizar el archivo .env:

   - Copia el archivo .env.supabase a .env
   - Reemplaza los valores de las variables con las credenciales obtenidas

4. Ejecutar la migración:

   - Accede a Supabase
   - Ve a "SQL Editor" (Editor SQL)
   - Crea un nuevo script y pega el contenido del archivo "migraciones/create_weatherdata_table.sql"
   - Haz clic en "RUN" para ejecutar el script

5. Iniciar la importación de datos:
   - Ejecuta: python bulk_supabase.py
     """
