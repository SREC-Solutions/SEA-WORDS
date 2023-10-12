#!/bin/bash

PWD=$(pwd)

TERM="mate-terminal --tab"

## First, launch all servers
# broker mosquitto que simula red loRa (sin opcion '-d' para ver todas las salidas)
gnome-terminal --tab --title "broker loRa" -e "mosquitto -p 8000 -c broker/mosquitto_8000.conf  "

# broker mosquitto que actua como paso de mensajes de FLINT (sin opcion '-d' para ver todas las salidas)
gnome-terminal --tab --title "bus FLINT" -e "mosquitto -p 8001  "


cd adapters/

# ejecucion del agente lora (primero el sink y despues el adaptador)

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

gcc -o sink.exe sink.c sink/conf_parser.c sink/inih/ini.c sink/mqtt_handler.c sock/socket_server.c sink/print.c -lpaho-mqtt3c -lcjson -fsanitize=address
gcc -o lora_agent.exe lora_agent.c sink/conf_parser.c sink/inih/ini.c sink/mqtt_handler.c sock/socket_client.c sink/flint_parser.c sink/print.c -lpaho-mqtt3c -lcjson -fsanitize=address

gnome-terminal --tab --title "loRa sink" -e "./sink.exe examples/01_direct/lora/conf/adapter_conf.ini DEBUG "

gnome-terminal --tab --title "loRa agent" -e "./lora_agent.exe examples/01_direct/lora/conf/adapter_conf.ini DEBUG "

#ejecucion del agente orion
gnome-terminal --tab --title "orion sink" -e "./sink.exe examples/01_direct/OrionAgent/conf/adapter_conf.ini DEBUG "

gnome-terminal --tab --title "orion sink" -e " python3 OrionAgent.py -f adapter_conf.ini -l DEBUG "

cd ../

gnome-terminal --tab --title "dB node" -e "./enviar_dato_mqtt_FLINT.sh "
