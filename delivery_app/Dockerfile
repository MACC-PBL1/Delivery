# Usa Python 3.12 slim (ligero)
FROM python:3.12-slim-bookworm

# Trabajaremos como root temporalmente para instalar dependencias
USER root

# Instala dependencias del sistema incluyendo curl para healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala dependencias de Python
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /requirements.txt

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /home/pyuser/code

# Crea un usuario no root y ajusta permisos
RUN useradd -u 1000 -d /home/pyuser -m pyuser && \
    chown -R pyuser:pyuser /home/pyuser

# Copia el script de entrada y dale permisos de ejecución
COPY entrypoint.sh /home/pyuser/code/entrypoint.sh
RUN chmod +x /home/pyuser/code/entrypoint.sh

# Copia toda la aplicación al contenedor
COPY app /home/pyuser/code/app

# Cambia a usuario no root
USER 1000

# Configura el entrypoint para ejecutar la app
ENTRYPOINT ["/home/pyuser/code/entrypoint.sh"]

# Establece PYTHONPATH explícitamente
ENV PYTHONPATH=/home/pyuser/code