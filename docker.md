
This document is the development and testing document for `issue25:Investigate the possibility of replacing lxc/lxd with docker` .

* Figure out the detail steps to replace lxc/lxd engine with docker engine.
  > The replacement process can be divided into two steps
  > * Change the environment of lxd in the master and workers to docker
  > * Change the deployment and configuration commands of the lxd container in the master and workers to the commands with the same function under docker

* Study files under Distrinet/mininet/provision folder.
  > Distrinet provides an infrastructure provisioning mechanism that uses Ansible to automatically install and configure LXD on each machine to be used during the experiment.  
  > * install-lxd.yml:this file is used to install lxd and download two images(an Ubuntu:18.04 image to emulate the vHosts, and a modified version of that image with OVS installed)on each machine by Ansible,we change it to install docker,and these two images need to be remade according to Docker,the OVS process will be described in the ovs_image.md.
  > * configure-lxd-no-clustering.yml:this file is used to configure lxd init,but you don't neet to do it in docker,so we only use it to distribute and load the above two images.  

* Create related files (config, deploy, install, etc) for docker provision by referring lxd scenario  
  >install-docker.yml:install-lxd.yml's docker version
  ```
  ansible-playbook ~/install-docker.yml
  ```
  >configure-docker.yml:
  ```
  ansible-playbook ~/configure-docker.yml:
  ```
  >Reading through all the code in the LXD scenario, we can see that the creation and configuration of containers and the creation of network interfaces and links are mainly concentrated in lxc_cotainer.py and distrinet.py,We need to replace the code that uses LXC/LXD with a docker equivalent command  
  
  >As for the network interfaces and links,we'll discuss this in more detail in issue33,In addition,for container creation and configuration, you can keep an eye out for lXC_container.py changes.The most critical one is that we use a pair of virtual devices veth pair and a bridge to replace lXC network attach command.Besides,We use namespaces to attach one end of veth pair to the container.  
  
  >We don't change the lxc_container.py's name,because this file is referenced several times in the project.We added an autoSetDocker parameter to this file, which allows you to choose whether to use docker or not.This parameter is passed by the external command --docker when Distrinet is runned in client

* The Distrinet environment replaced by docker includes the three following entities 
  * Client: host in which the Distrinet script is running and decides where to place the vNodes around the physical infrastructure (round-robin by default). The Client must be able to connect via SSH to the Master host.
  * Master: host that acts as a relay to interconnect the Client with all the Worker hosts. It communicates with the Client and the different Workers via SSH. Note that the Master can also be configured as a Worker.
  * Worker(s): host(s) where all the vNodes (vSwitches and vHosts) are running. vNodes are managed by the Master and the Client, via the admin network.
  > To ensure the smooth deployment of vNodes, Ip forwarding needs to be allowed on workers and the netns of the container needs to be restored to the host directory,here are a few commands that you might configure on workers and Master.
  ```
  sysctl net.ipv4.conf.all.forwarding=1  
  iptables --policy FORWARD ACCEPT
  mkdir /var/run/netns
  ulimit -n 196835
  ```

* Experimental environment Configuration
  >clinet:192.168.71.128,master:192.168.71.141,worker:192.168.71.142.They are all Ubuntu virtual machines running on the same physical host  
  >We use distrinet to create a linear topology with two switches and two hosts, i.e. :  
  >Master:
  ```
  root@master:~# ryu-manager /usr/lib/python3/dist-packages/ryu/app/simple_switch_13.py --verbose
  ```
  >client:
  ```
  jxq@client:~$ python3 bin/dmn --workers="192.168.71.141,192.168.71.142" --controller=lxcremote,ip=192.168.0.1 --topo=linear,2 --docker
  ```

* Experimental results
  >Distrinet's CLI can be generated normally and pingall test also passes
  # ![client](https://github.com/J980419xq/Distrinet/blob/master/images/cli.png)  
  >The master and worker can create containers and interfaces normally  
  >master: ip a
  ```
  1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
  2: ens33: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 00:0c:29:eb:10:f4 brd ff:ff:ff:ff:ff:ff
    inet 192.168.71.141/24 brd 192.168.71.255 scope global noprefixroute ens33
       valid_lft forever preferred_lft forever
    inet6 fe80::20c:29ff:feeb:10f4/64 scope link 
       valid_lft forever preferred_lft forever
  3: docker0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
    link/ether 02:42:29:d0:a1:78 brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
       valid_lft forever preferred_lft forever
    inet6 fe80::42:29ff:fed0:a178/64 scope link 
       valid_lft forever preferred_lft forever
  26: admin-br: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 72:97:2f:43:4c:cb brd ff:ff:ff:ff:ff:ff
    inet 192.168.0.1/8 brd 192.255.255.255 scope global admin-br
       valid_lft forever preferred_lft forever
    inet6 fe80::80f7:25ff:fe05:b735/64 scope link 
       valid_lft forever preferred_lft forever
  27: intf3@if28: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master admin-br state UP group default qlen 1000
    link/ether 72:97:2f:43:4c:cb brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet6 fe80::7097:2fff:fe43:4ccb/64 scope link 
       valid_lft forever preferred_lft forever
  29: intf1@if30: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master admin-br state UP group default qlen 1000
    link/ether 9a:aa:18:f7:72:0b brd ff:ff:ff:ff:ff:ff link-netnsid 1
    inet6 fe80::98aa:18ff:fef7:720b/64 scope link 
       valid_lft forever preferred_lft forever
  31: vNone@vadmin-br: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 36:9f:9e:c7:9b:52 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::349f:9eff:fec7:9b52/64 scope link 
       valid_lft forever preferred_lft forever
  32: vadmin-br@vNone: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master admin-br state UP group default qlen 1000
    link/ether a2:06:41:fd:a4:7c brd ff:ff:ff:ff:ff:ff
    inet6 fe80::a006:41ff:fefd:a47c/64 scope link 
       valid_lft forever preferred_lft forever
  33: vx_21: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master admin-br state UNKNOWN group default qlen 1000
    link/ether 9e:3b:48:ef:89:6f brd ff:ff:ff:ff:ff:ff
    inet6 fe80::9c3b:48ff:feef:896f/64 scope link 
       valid_lft forever preferred_lft forever
  34: intf6: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether c2:e5:e4:21:a2:78 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::c0e5:e4ff:fe21:a278/64 scope link 
       valid_lft forever preferred_lft forever
  35: intf5@if36: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master intf6 state UP group default qlen 1000
    link/ether c2:e5:e4:21:a2:78 brd ff:ff:ff:ff:ff:ff link-netnsid 1
    inet6 fe80::c0e5:e4ff:fe21:a278/64 scope link 
       valid_lft forever preferred_lft forever
  37: intf8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether a6:0f:bc:97:d5:4d brd ff:ff:ff:ff:ff:ff
    inet6 fe80::f4e0:f3ff:fe8f:37f5/64 scope link 
       valid_lft forever preferred_lft forever
  38: intf7@if39: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master intf8 state UP group default qlen 1000
    link/ether f6:e0:f3:8f:37:f5 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet6 fe80::f4e0:f3ff:fe8f:37f5/64 scope link 
       valid_lft forever preferred_lft forever
  40: vintf8@vintf6: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master intf8 state UP group default qlen 1000
    link/ether a6:0f:bc:97:d5:4d brd ff:ff:ff:ff:ff:ff
    inet6 fe80::a40f:bcff:fe97:d54d/64 scope link 
       valid_lft forever preferred_lft forever
  41: vintf6@vintf8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master intf6 state UP group default qlen 1000
    link/ether e6:31:f4:e8:39:38 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::e431:f4ff:fee8:3938/64 scope link 
       valid_lft forever preferred_lft forever
  42: intf16: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 4e:63:dc:70:fd:e0 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::b085:44ff:fed3:599/64 scope link 
       valid_lft forever preferred_lft forever
  43: intf15@if44: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master intf16 state UP group default qlen 1000
    link/ether b2:85:44:d3:05:99 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet6 fe80::b085:44ff:fed3:599/64 scope link 
       valid_lft forever preferred_lft forever
  45: vx_26: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master intf16 state UNKNOWN group default qlen 1000
    link/ether 4e:63:dc:70:fd:e0 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::4c63:dcff:fe70:fde0/64 scope link 
       valid_lft forever preferred_lft forever
  ```
  # ![master container](https://github.com/J980419xq/Distrinet/blob/master/images/master.png)  
  >worker: ip a
  ```
  1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
  2: ens33: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 00:0c:29:ae:98:b2 brd ff:ff:ff:ff:ff:ff
    inet 192.168.71.142/24 brd 192.168.71.255 scope global noprefixroute ens33
       valid_lft forever preferred_lft forever
    inet6 fe80::20c:29ff:feae:98b2/64 scope link 
       valid_lft forever preferred_lft forever
  3: docker0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
    link/ether 02:42:5a:e8:15:54 brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
       valid_lft forever preferred_lft forever
  22: admin-br: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 22:7e:11:52:c0:5c brd ff:ff:ff:ff:ff:ff
    inet6 fe80::bc16:11ff:fea9:78a4/64 scope link 
       valid_lft forever preferred_lft forever
  23: intf2@if24: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master admin-br state UP group default qlen 1000
    link/ether e2:94:dc:27:55:9d brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet6 fe80::e094:dcff:fe27:559d/64 scope link 
       valid_lft forever preferred_lft forever
  25: intf4@if26: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master admin-br state UP group default qlen 1000
    link/ether be:16:11:a9:78:a4 brd ff:ff:ff:ff:ff:ff link-netnsid 1
    inet6 fe80::bc16:11ff:fea9:78a4/64 scope link 
       valid_lft forever preferred_lft forever
  27: vx_21: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master admin-br state UNKNOWN group default qlen 1000
    link/ether 22:7e:11:52:c0:5c brd ff:ff:ff:ff:ff:ff
    inet6 fe80::207e:11ff:fe52:c05c/64 scope link 
       valid_lft forever preferred_lft forever
  28: intf10: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 2a:54:21:60:79:c5 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::9030:e2ff:fedb:b323/64 scope link 
       valid_lft forever preferred_lft forever
  29: intf9@if30: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master intf10 state UP group default qlen 1000
    link/ether 92:30:e2:db:b3:23 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet6 fe80::9030:e2ff:fedb:b323/64 scope link 
       valid_lft forever preferred_lft forever
  31: intf12: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 6e:c6:34:19:9e:cc brd ff:ff:ff:ff:ff:ff
    inet6 fe80::6cc6:34ff:fe19:9ecc/64 scope link 
       valid_lft forever preferred_lft forever
  32: intf11@if33: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master intf12 state UP group default qlen 1000
    link/ether 6e:c6:34:19:9e:cc brd ff:ff:ff:ff:ff:ff link-netnsid 1
    inet6 fe80::6cc6:34ff:fe19:9ecc/64 scope link 
       valid_lft forever preferred_lft forever
  34: vintf12@vintf10: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master intf12 state UP group default qlen 1000
    link/ether b2:c1:38:57:4c:ca brd ff:ff:ff:ff:ff:ff
    inet6 fe80::b0c1:38ff:fe57:4cca/64 scope link 
       valid_lft forever preferred_lft forever
  35: vintf10@vintf12: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master intf10 state UP group default qlen 1000
    link/ether 2a:54:21:60:79:c5 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::2854:21ff:fe60:79c5/64 scope link 
       valid_lft forever preferred_lft forever
  36: intf14: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 0e:fd:28:ce:0e:8d brd ff:ff:ff:ff:ff:ff
    inet6 fe80::cfd:28ff:fece:e8d/64 scope link 
       valid_lft forever preferred_lft forever
  37: intf13@if38: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master intf14 state UP group default qlen 1000
    link/ether 0e:fd:28:ce:0e:8d brd ff:ff:ff:ff:ff:ff link-netnsid 1
    inet6 fe80::cfd:28ff:fece:e8d/64 scope link 
       valid_lft forever preferred_lft forever
  39: vx_26: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master intf14 state UNKNOWN group default qlen 1000
    link/ether 86:5e:28:6d:96:ea brd ff:ff:ff:ff:ff:ff
    inet6 fe80::845e:28ff:fe6d:96ea/64 scope link 
       valid_lft forever preferred_lft forever
  ```
  # ![worker container](https://github.com/J980419xq/Distrinet/blob/master/images/worker.png)



