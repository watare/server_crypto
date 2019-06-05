#!/bin/bash
#recuperation de l'image straton

docker build --no-cache -t crypto:latest .

#lancement d'un containeur ayant le runtime straton
sudo docker run -i -t  -it crypto:latest
