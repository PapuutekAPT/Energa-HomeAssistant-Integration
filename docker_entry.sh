#! /bin/bash

PARAMETERS=""

if [ -z "${CRON}" ]; then 
    echo "Niewłaściwe ustawienie zmiennej CRON"; 
    exit 1;
fi

if [ -z "${ENERGA_USERNAME}" ]; then 
    echo "Niewłaściwe ustawienie zmiennej ENERGA_USERNAME"; 
    exit 1;
fi

if [ -z "${ENERGA_PASSWORD}" ]; then 
    echo "Niewłaściwe ustawienie zmiennej ENERGA_PASSWORD"; 
    exit 1;
fi

if [ -z "${TYPE}" ]; then 
    echo "Niewłaściwe ustawienie zmiennej TYPE"; 
    exit 1;
fi

if [ -z "${MQTT_SERVER}" ]; then 
    echo "Niewłaściwe ustawienie zmiennej MQTT_SERVER"; 
    exit 1;
fi

if [ -z "${MQTT_TOPIC}" ]; then 
    echo "Niewłaściwe ustawiedocker run nie zmiennej MQTT_TOPIC"; 
    exit 1;
fi

if [ -n "$MQTT_USERNAME" ]; then
    if [ -z "${MQTT_PASSWORD}" ]; then
        echo "Brak hasła dla użytkownika MQTT";
        exit 1;
    fi
    PARAMETERS="-mu '$MQTT_USERNAME' -mp '$MQTT_PASSWORD'";
fi

if [ -n "$MQTT_PORT" ]; then
    PARAMETERS="$PARAMETERS -msp $MQTT_PORT"
fi

PARAMETERS="-eu '$ENERGA_USERNAME' -ep '$ENERGA_PASSWORD' -ms $MQTT_SERVER -mt '$MQTT_TOPIC' $PARAMETERS -tm $TYPE"

echo "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" > /tmp/crontab 
echo "$CRON /app/main.py $PARAMETERS > /proc/\$(cat /var/run/crond.pid)/fd/1 2>&1" >> /tmp/crontab
/usr/bin/crontab /tmp/crontab
/usr/sbin/cron -f

