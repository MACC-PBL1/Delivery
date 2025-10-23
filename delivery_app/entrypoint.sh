#!/bin/bash
set -e
# entrypoint.sh: arranca el microservicio Delivery con Hypercorn

# Mostrar el nombre del servicio
SERVICE_NAME=${SERVICE_NAME:-"Delivery Service"}
echo "Service: ${SERVICE_NAME}"

# Obtener la IP del contenedor (opcional)
IP=$(hostname -i)
export IP
echo "IP: ${IP}"

# Configurar PYTHONPATH para que Python encuentre el módulo 'app'
export PYTHONPATH=/home/pyuser/code:$PYTHONPATH
echo "PYTHONPATH: $PYTHONPATH"

# Función para manejar señales de terminación
terminate() {
    echo "Termination signal received, shutting down..."
    kill -SIGTERM "$HYPERCORN_PID"
    wait "$HYPERCORN_PID"
    echo "Hypercorn has been terminated"
}

trap terminate SIGTERM SIGINT

# Opcional: esperar a RabbitMQ si el microservicio depende de él
until nc -z rabbitmq 5672; do
    echo "Esperando a RabbitMQ..."
    sleep 1
done

# Arranca Hypercorn para exponer FastAPI en 0.0.0.0:8000
hypercorn --bind 0.0.0.0:8000 app.main:app &

# Guarda el PID de Hypercorn y espera
HYPERCORN_PID=$!
wait "$HYPERCORN_PID"
