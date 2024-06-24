#!/bin/bash

function shX(){
        CMD=$*
        echo -e "\e[32m[$(date +"%F %T")] " EXEC: ${CMD} " \e[0m"
        ${CMD}
}


container_id=`docker ps -a | awk '{print $10}' | grep h`
array=(`echo $container_id | tr '\n' ' '` )
for var in ${array[@]}
do
	#echo $var
	shX docker exec ${var} sh /root/nova_compute_auto_restart.sh & 
done
