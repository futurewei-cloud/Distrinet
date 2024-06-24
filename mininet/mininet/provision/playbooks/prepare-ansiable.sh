#/bin/bash
if [[ $# -ne 2 ]];then
        echo "Usage:    ./prepare-ansiable.sh {base-ip} {ip-num}"
else
	base_ip=$1
	base_ip_array=(`echo $base_ip | tr '.' ' '` )
	ip_num=$2
	
	echo "[master]" > /etc/ansible/hosts
	echo "127.0.0.1 ansible_connection=local ansible_python_interpreter=/usr/bin/python3" >> /etc/ansible/hosts
	echo "[workers]" >> /etc/ansible/hosts
	
	for ((cnt=0; cnt<${ip_num}; cnt++))
	do
		let temp=${base_ip_array[3]}+cnt
		let my_ip_1=${temp}%256
		let my_ip_2=${base_ip_array[2]}+${temp}/256
		my_ip=${base_ip_array[0]}.${base_ip_array[1]}.${my_ip_2}.${my_ip_1}
		#echo $my_ip
		echo "${my_ip} ansible_ssh_extra_args='-o StrictHostKeyChecking=no' ansible_python_interpreter=/usr/bin/python3" >> /etc/ansible/hosts
	done	
fi
