#workflowdemo dockfile
FROM ubuntu:latest
LABEL maintainer zhengge2012@gmail.com
WORKDIR /opt
RUN apt-get update -y
RUN apt-get install -y mysql-server libmysqlclient-dev redis-server python3 python3-pip python3-dev git supervisor nginx
RUN sed -i 's/bind 127.0.0.1 ::1/bind 127.0.0.1/g' /etc/redis/redis.conf

RUN apt-get install build-essential libpulse-dev libssh-dev libwebp-dev libvncserver-dev software-properties-common curl gcc libavcodec-dev libavutil-dev libcairo2-dev libswscale-dev libpango1.0-dev libfreerdp-dev libssh2-1-dev libossp-uuid-dev jq wget libpng-dev libvorbis-dev libtelnet-dev libssl-dev libjpeg-dev libjpeg-turbo8-dev -y

RUN mkdir -p /var/log/web
WORKDIR /opt
RUN git clone https://github.com/jimmy201602/workflowdemo.git
WORKDIR /opt/workflowdemo
RUN pip3 install -r requirements.txt
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate
RUN python3 createsuperuser.py

WORKDIR /opt
RUN git clone https://github.com/blackholll/loonflow.git
WORKDIR /opt/loonflow
RUN git checkout develop
WORKDIR /opt/loonflow/requirements
RUN pip3 install -r dev.txt

RUN mysql -u root -e "CREATE DATABASE if not exists loonflownew DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
RUN mysql -u root -e "CREATE USER loonflownew@127.0.0.1 IDENTIFIED BY '123456'";
RUN mysql -e "GRANT ALL PRIVILEGES ON loonflownew.* TO 'loonflownew'@'127.0.0.1';"
RUN mysql --one-database loonflownew < /opt/workflowdemo/loonflow.sql

ADD nginx.conf /etc/nginx/nginx.conf
ADD supervisord.conf /etc/supervisor/supervisord.conf
ADD docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
EXPOSE 80
CMD ["/docker-entrypoint.sh", "start"]
