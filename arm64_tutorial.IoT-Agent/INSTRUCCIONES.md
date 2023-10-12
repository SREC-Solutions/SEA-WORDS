# Instalar en Raspberry

## Instalar docker 

```
curl -ssL https://get.docker.com | sh
```

## Instalar docker-compose
```
sudo pip install docker-compose
```
Estos pasos se realizaron con un docker completamente vacío sin ninguna imagen creada previamente. Para borrar imagenes, contenedores y redes de docker:
```
.dokcer system prune -a
```

## Docker IoT Agent

Ubicarse en el directorio ./docker y crear la imagen de iot-agent:

```
cd docker
docker build -t iot-agent . --build-arg DOWNLOAD=latest
```
## Orion y mongo-db

Ubicarse en el directorio tutorials.IoT-Agent y descargar el resto de imagenes
Ignorar los errores realacionados con iot-agent.

```
cd tutorials.IoT-Agent
./services create
```

Ejecutar los servicios

```
./services start
```

Una ejecutados ya podremos realizar las peticiones (mirar fichero request_agent.txt) para enviar y leer datos de fiware.
Para cambiar las entidades y dispositivos de la base de datos de fiware modificar el fichero import-data.

Para detener los servicios:

```
./services stop
```
