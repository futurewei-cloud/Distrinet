## deploy in bare machine
### Step1:install dependcies
```bash
apt install wget openjdk-11-jdk
```

### Step2:download onos
```bash
sudo mkdir /opt
cd /opt
sudo wget -c https://repo1.maven.org/maven2/org/onosproject/onos-releases/2.7.0/onos-2.7.0.tar.gz
sudo tar xzf onos-2.7.0.tar.gz
sudo mv onos-2.7.0 onos
```

### Step3:launch onos 
```bash
vim onos/apache-karaf*/bin/setenv     # * is your apache-karaf version
#add the follow
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/
```

```bash
export ONOS_APPS="drivers,openflow-base,openflow,proxyarp,lldpprovider,fwd,optical-model,hostprovider"   #add apps and excute
/opt/onos/bin/onos-service start
```

## deploy in docker cluster
### Step1:import docker images
```bash
docker pull atomix/atomix
docker pull onosproject/onos
```

### Step2:create atomix container
```bash
docker run -t -d --name atomix-1 atomix/atomix
docker run -t -d --name atomix-2 atomix/atomix
docker run -t -d --name atomix-3 atomix/atomix
```

### Step3:git onos source code
```bash
cd ~
git clone https://gerrit.onosproject.org/onos
```

### Step4:generate atomix config files
```bash
export OC1=172.17.0.2                  #atomix-1 ip
export OC2=172.17.0.3                  #atomix-2 ip
export OC3=172.17.0.4                  #atomix-3 ip
cd ~/onos
./tools/test/bin/atomix-gen-config 172.17.0.2 ~/atomix-1.conf 172.17.0.2 172.17.0.3 172.17.0.4     #maybe need python2
./tools/test/bin/atomix-gen-config 172.17.0.3 ~/atomix-2.conf 172.17.0.2 172.17.0.3 172.17.0.4
./tools/test/bin/atomix-gen-config 172.17.0.4 ~/atomix-3.conf 172.17.0.2 172.17.0.3 172.17.0.4
docker cp ~/atomix-1.conf atomix-1:/opt/atomix/conf/atomix.conf
docker cp ~/atomix-2.conf atomix-2:/opt/atomix/conf/atomix.conf
docker cp ~/atomix-3.conf atomix-3:/opt/atomix/conf/atomix.conf
docker restart atomix-1
docker restart atomix-2
docker restart atomix-3
```

### Step5:create onos container
```bash
docker run -t -d -p 6653:6653 -e ONOS_APPS="drivers,openflow-base,netcfghostprovider,openflow,proxyarp,lldpprovider,fwd,optical-model,hostprovider,gui2" --name onos1 onosproject/onos
docker run -t -d -p 6654:6653 -e ONOS_APPS="drivers,openflow-base,netcfghostprovider,openflow,proxyarp,lldpprovider,fwd,optical-model,hostprovider,gui2" --name onos2 onosproject/onos
docker run -t -d -p 6655:6653 -e ONOS_APPS="drivers,openflow-base,netcfghostprovider,openflow,proxyarp,lldpprovider,fwd,optical-model,hostprovider,gui2" --name onos3 onosproject/onos
```

### Step6:generate onos config files
```bash
cd ~/onos
./tools/test/bin/onos-gen-config 172.17.0.5 ~/cluster-1.json -n 172.17.0.2 172.17.0.3 172.17.0.4     #maybe need python2
./tools/test/bin/onos-gen-config 172.17.0.6 ~/cluster-2.json -n 172.17.0.2 172.17.0.3 172.17.0.4
./tools/test/bin/onos-gen-config 172.17.0.7 ~/cluster-3.json -n 172.17.0.2 172.17.0.3 172.17.0.4
docker exec onos1 mkdir /root/onos/config
docker exec onos2 mkdir /root/onos/config
docker exec onos3 mkdir /root/onos/config
docker cp ~/cluster-1.json onos1:/root/onos/config/cluster.json
docker cp ~/cluster-2.json onos2:/root/onos/config/cluster.json
docker cp ~/cluster-3.json onos3:/root/onos/config/cluster.json
docker restart onos1
docker restart onos2
docker restart onos3
```

 