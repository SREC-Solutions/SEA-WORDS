# FLINT configuración

```
sudo apt install cmake -y
sudo apt install libpaho-mqtt1.3
```
## Instalación MQTT
```
sudo apt-get install mosquitto -y
git clone https://github.com/eclipse/paho.mqtt.c
cd paho.mqtt.c
mkdir build
cd build
sudo apt install cmake -y
cmake ..
make 
sudo make install
```
## Instalación cJson
```
 git clone https://github.com/DaveGamble/cJSON.git
 cd cJSON
 mkdir build
 cd build
 cmake ..
 make 
 sudo make install
```
# FLINT Funcionamiento
## (Need 7 terminals)
## Setup mosquitto 
```
mosquitto -p 8000 -c broker/mosquitto_8000.conf   
mosquitto -p 8001
````
## Lora SINK y Agent
```
 cd adapters/
 export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

 sudo gcc -o sink.exe sink.c sink/conf_parser.c sink/inih/ini.c sink/mqtt_handler.c sock/socket_server.c sink/print.c -lpaho-mqtt3c -lcjson -fsanitize=address
 sudo gcc -o lora_agent.exe lora_agent.c sink/conf_parser.c sink/inih/ini.c sink/mqtt_handler.c sock/socket_client.c sink/flint_parser.c sink/print.c -lpaho-mqtt3c -lcjson -fsanitize=address
#Lora Sink and Agent
 ./sink.exe examples/01_direct/lora/conf/adapter_conf.ini DEBUG
 ./lora_agent.exe examples/01_direct/lora/conf/adapter_conf.ini DEBUG
```
## Correr Agente Orion
```
 pip install sseclient
 pip install paho-mqtt
 pip install jsonschema
 ./sink.exe examples/01_direct/OrionAgent/conf/adapter_conf.ini DEBUG
 python3 OrionAgent.py -f adapter_conf.ini  -l DEBUG
````

## Prueba envío datos
```
cd ../
sudo chmod +x enviar_dato_mqtt_FLINT.sh
./enviar_dato_mqtt_FLINT.sh
```
