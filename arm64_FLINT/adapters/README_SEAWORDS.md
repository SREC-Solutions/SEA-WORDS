#FLINT configuración
## Instalación MQTT
> sudo apt-get install mosquitto
> git clone https://github.com/eclipse/paho.mqtt.c
> cd paho.mqtt.c
> mkdir build
> cd build
> cmake ..
> make 
> sudo make install
## Instalación cJson
> git clone https://github.com/DaveGamble/cJSON.git
> cd cJson
> mkdir build
> cd build
> cmake ..
> make 
> sudo make install
## Instalación 
#FLINT Funcionamiento
## Setup mosquitto 
> mosquitto  -c /etc/mosquitto/conf.d/mosquitto_8001.conf  -p 8001
## Entrar en carpeta adapters y correr sink
### al ejecutar sink.exe no olvidar de ejecutar antes (poner en .bashrc !!)
> export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
> gcc -o sink.exe sink.c sink/conf_parser.c sink/inih/ini.c sink/mqtt_handler.c sock/socket_server.c sink/print.c -lpaho-mqtt3c -lcjson -fsanitize=address
> ./sink.exe examples/01_direct/OrionAgent/conf/adapter_conf.ini DEBUG
## Correr Agente 
> pip install sseclient
> pip install paho-mqtt
> pip install jsonchema
> python3 OrionAgent.py -f adapter_conf.ini  -l DEBUG