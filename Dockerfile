FROM ubuntu
ADD ./fetchdata_gdax.py  /root/server_crypto/
ADD ./walldetection.py   /root/server_crypto/
ADD ./algocompatarif.py  /root/server_crypto/
ADD ./automatisation.sh  /root/server_crypto/
ADD ./cron_instruction   /root/server_crypto/

RUN touch /var/log/cron.log

WORKDIR /root/server_crypto/

#installation cron

RUN apt-get update
RUN apt-get install cron
RUN apt-get install -y iputils-ping
RUN apt-get install -y python2.7
RUN apt-get install -y python-pip
RUN  pip install pandas
RUN  pip install numpy
RUN  pip install cbpro

#droits pour les dossier



CMD /bin/bash ./automatisation.sh
