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


 