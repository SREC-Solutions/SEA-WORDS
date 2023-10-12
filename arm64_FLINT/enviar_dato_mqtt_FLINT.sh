MSG='{
    "device-ctrl":
    {
        "data": "BY4RQqBIuk3cCfmPzbCAQSwA",
        "dev-eui": "0000000000000001",
        "device-custom-ctrl": { }
    },
    "input-ctrl":
    {
        "input-type": "AgentName",
        "input-ip": "192.168.1.138",
        "input-port": 8001,
        "input-protocol": "mqtt"
    },
    "output-ctrl":
    {
        "method": "POST",
        "ipv6": "0:0:0:0:0:0:0:0",
        "thing-id": "urn:uuid:f927f1bd-477e-4f99-bc3b-7734d81dd863",
        "output-custom-ctrl":
        ""
    },
    "adapter-ctrl":
    {
        ""
    }
} '

LORA_BROKER1="-h 127.0.0.1 -p 8001"
LORA_BROKER="-h 127.0.0.1 -p 8000"

TOPIC="application/1/device/8001/event/up"

MSG2_ok='{"devEUI":"8000", "data":"0",  "fPort": 10, "txInfo": { "measurement":"001"}, "type": {"noise":10}, "rxInfo": [{"name": "CVR", "rssi": "111"}], "type":"noise"} '

MSG2='{"devEUI":"8001", "data":"0",  "fPort": 10, "txInfo": { "measurement":"001"}, "type": {"noise":10}, "rxInfo": [{"name": "CVR", "rssi": "143"}], "type":"noise"} '

echo " enviado: " $LORA_BROKER1  $TOPIC  $MSG2 "\n"
mosquitto_pub $LORA_BROKER -t "$TOPIC"   -m "$MSG2"
