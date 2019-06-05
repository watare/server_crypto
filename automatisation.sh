#!/bin/bash

#lancement du script cron
crontab cron_instruction
cron && tail -f /root/server_crypto/cron_instruction
