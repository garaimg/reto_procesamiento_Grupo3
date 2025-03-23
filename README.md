# Reto2 Grupo3 - Desarrollo de aplicaciones IoT

## Proyecto: Simulación y Procesamiento de Datos en un Parque Eólico

Este proyecto implementa un modelo de datos para un parque eólico compuesto por **10 generadores** y un **concentrador**. Los generadores simulan datos sintéticos de producción eólica y los envían al concentrador, que los valida y almacena en una base de datos PostgreSQL. Además, se implementan funcionalidades de agregación, persistencia y seguridad mediante **API-Keys**. El sistema se orquesta mediante **Docker Compose** y la API se desarrolla con **FastAPI**.

---

## Miembros del Equipo

- **Miembro 1:** Markel Aguirre
- **Miembro 2:** Garai Martínez de Santos
- **Miembro 3:** Pablo Ruiz de Azúa

---

## Explicación de los Pasos Seguidos  

### 1. **Generación de Datos Sintéticos en los Generadores**
   - Se han desarrollado **10 generadores** como contenedores individuales en Docker.  
   - Cada generador ejecuta un programa en Python que **genera datos en formato JSON cada X segundos**.  
   - Se incluye una probabilidad de generar datos erróneos.  
   - Cada generador tiene un **hostname** único definido por Docker para su identificación.
   - En el docker compose está en campo réplicas, el cual permite desplegar 10 contenedores del mismo servicio (generador).

### 2. **Desarrollo del Concentrador con FastAPI**
   - Se ha desarrollado un **concentrador** que recibe los datos de los generadores y los **valida** usando `pydantic`.  
   - Implementa un sistema de **persistencia en PostgreSQL** para almacenar los datos recibidos.  
   - Expone **endpoints en FastAPI** para permitir consultas GET y POST sobre los datos registrados. 
   - Los generadores mandan los datos al concentrador mediante el **POST**.
   - Se ha incluido **agregación de datos** por cada minuto, con cálculos como **media, máximo y mínimo**, incluyendo información del generador con los valores máximos y mínimos.  
   - Para las consultas se ha usado SQL.
   - Se puede acceder al swagger de la API en: [http://localhost:8000/docs](http://localhost:8000/docs).  

### 3. **Implementación de Seguridad con API-Keys**
   - Se ha añadido un sistema de **autenticación basado en API-Keys** para restringir el acceso a la API.  
   - Cada cliente debe proporcionar una API-Key válida en las solicitudes.  

### 4. **Persistencia de Datos con PostgreSQL**
   - Se ha utilizado **PostgreSQL** como base de datos para almacenar los datos enviados por los generadores.  
   - Se ha creado una tabla específica para organizar los datos de los generadores (llamada medidas). 
   - Se ha utilizado el ORM SQLAlchemy para interactuar con la base de datos.


### 5. **Orquestación con Docker Compose**
   - Se ha creado un `docker-compose.yml` para definir la infraestructura del sistema:  
     - **10 generadores** como contenedores individuales gracias al campo replicas dentro de deploy.  
     - **Un concentrador** basado en FastAPI.  
     - **Un servicio PostgreSQL** para la persistencia de datos.  
   - Los servicios de generador y de concentrador tienen su propio `Dockerfile` y `requirements.txt` para facilitar la construcción y despliegue.  

### 6. **Consulta y Monitorización de Datos**
   - Se pueden realizar **consultas GET** para obtener datos de los generadores.  
   - Se pueden obtener **agregaciones** de cada minuto, como la media, máximo y mínimo, indicando qué generador produjo los valores máximos y mínimos.  
   - Se pueden ver los datos en la base de datos accediendo al contenedor PostgreSQL.  

---

## Instrucciones de Uso

### 1. **Requisitos Previos:**
   - Tener instalado [Docker](https://www.docker.com/get-started) y [Docker Compose](https://docs.docker.com/compose/install/).
   - Clonar el repositorio del proyecto.

### 2. **Ejecución del Sistema:**
   - Levantar los contenedores ejecutando el siguiente comando:
     ```bash
     docker compose up --build
     ```
   - Verificar los logs para observar el flujo de datos y las validaciones.
   - Acceder a la API en [http://localhost:8000/docs](http://localhost:8000/docs) para probar los endpoints disponibles.

### 3. **Acceso a la Base de Datos:**
   - Ingresar al contenedor de PostgreSQL:
     ```bash
     docker exec -it reto_procesamiento_grupo3-postgres-1 sh
     ```
   - Acceder a PostgreSQL:
     ```bash
     psql -U postgres
     ```
   - Ver las bases de datos disponibles:
     ```
     \l
     ```
   - Conectarse a la base de datos del proyecto:
     ```
     \c windpark_db
     ```
   - Ver las tablas existentes:
     ```
     \dt
     ```
   - Realizar consultas personalizadas sobre los datos almacenados.

---

## Posibles Vías de Mejora  

- **Modularidad del Código:**  
  - Mejorar la estructura del código separando los componentes en módulos más específicos.  
  - Implementar clases para encapsular la lógica de validación y procesamiento.  

- **Manejo de Errores y Logging Mejorado:**  
  - Implementar logs detallados para cada proceso del concentrador y los generadores.  
  - Agregar **reintentos automáticos** en caso de errores en la comunicación.  

- **Seguridad Avanzada:**  
  - Implementar autenticación **OAuth 2.0** o **JWT** en lugar de API-Keys.  
  - Agregar **cifrado de datos** en la base de datos para mayor protección.  

- **Monitorización en Tiempo Real:**  
  - Integrar **Prometheus y Grafana** para visualizar métricas del sistema.  
  - Configurar alertas para detectar fallos en los generadores o el concentrador.  

- **Optimización de Consultas SQL:**  
  - Crear **índices** en la base de datos para mejorar la velocidad de consultas.  
  - Implementar **particionamiento** de datos para manejar grandes volúmenes de información.  

- **Escalabilidad:**  
  - Permitir la conexión de **más de 10 generadores**, balanceando la carga en el concentrador.  
  - Implementar un sistema de **cacheo** para mejorar la eficiencia de las consultas frecuentes.  

---
## Problemas / Retos Encontrados

- **Validación de Datos:**
  - Se presentaron dificultades en la validación de datos debido a la inclusión de valores erróneos con probabilidad N.
  - Se utilizó **Pydantic** para asegurar que solo se procesaran datos válidos.

- **Gestión de la Persistencia y de consultas SQL:**
  - Se implementó **SQLAlchemy** para facilitar la interacción con la base de datos PostgreSQL,lo cual se nos dificultó.
  - Realizar consultas SQL para las agregaciones presentó dificultades, ya que eran bastante complejas.

- **Configuración de Seguridad:**
  - Se implementaron **API-Keys** para evitar accesos no autorizados a la API, lo cual tuvimos que investigar, ya que no sabíamos como funcionaba.

---

## Alternativas Posibles

## 1. Base de Datos Especializada en Series Temporales
- En vez de **PostgreSQL**, usar una base optimizada para series temporales como:
  - **InfluxDB** (rápido para datos de IoT y monitoreo).
  - **TimescaleDB** (extensión de PostgreSQL optimizada para series temporales).
  - **MongoDB con Time-Series Collections** (para datos estructurados y no estructurados).

## 2. Comunicación Alternativa Entre Generadores y Concentrador
- En lugar de una API para enviar datos, se pueden usar:
  - **MQTT** (protocolo ligero y eficiente para IoT).
  - **Apache Kafka o RabbitMQ** (gestión avanzada de eventos y streaming de datos).
  - **gRPC** (comunicación más rápida y eficiente que REST).

## 3. Orquestación con Kubernetes
- Usar **Kubernetes** en lugar de Docker Compose para mejor escalabilidad.
- **Ventajas:**
  - Balanceo de carga automático.
  - Recuperación automática de fallos.
  - Escalado dinámico según la demanda.

---

## Extras y Mejoras Implementadas

- **Persistencia de Datos con PostgreSQL**
- **Seguridad de la API con API-Keys**
- **Proceso Automatizado con Docker**
- **Opción de Obtener Información de los Generadores con Consultas GET**
- **Agregaciones (Máximo, Mínimo y Media) por Cada Minuto**
- **Uso del ORM SQLAlchemy para Interactuar con la Base de Datos**
- **Validación de Datos con Pydantic para Garantizar Consistencia**



