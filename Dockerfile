FROM python:3-slim

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get -y install xvfb cron chromium-driver && \
    apt-get clean && \
    ln -f -s /usr/share/zoneinfo/Europe/Warsaw /etc/localtime && \
    echo "Europe/Warsaw" > /etc/timezone && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --no-cache-dir selenium pyvirtualdisplay paho-mqtt

ADD main.py docker_entry.sh /app/

RUN chmod 0744 /app/main.py && chmod 0744 /app/docker_entry.sh

CMD ["/app/docker_entry.sh"]