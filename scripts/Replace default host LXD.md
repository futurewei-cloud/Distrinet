## Create Custom DC Topology

####  Replace the container of lxd

1. Installing a new package in the vHost image.（Avoid conflicts with the naming of the following

   ```
   root@master:~# ansible all -m raw -a "lxc image ls"
   ```

2. Create a new network that allows the container to connect to the external network（The original network is not connected to the external network by default

   ```
   root@master:~# lxc network create inetbr ipv6.address=none ipv4.address=10.0.10.1/24 ipv4.nat=true
   ```



3. Create a file that describes a new profile that attaches the container to the new network

```
root@server14:/home/sdn# vim profile.conf

config: {}
description: inet  profile
devices:
  eth0:
    name: eth0
    nictype: bridged
    parent: inetbr
    type: nic
  root:
    path: /
    pool: default
    type: disk
name: inet
used_by: []
```


​	4.Create the new profile and edit it with the profile.conf file

```
root@master:~# lxc profile create inet 
root@master:~# lxc profile edit inet < profile.conf
```

## 
#### 
​	5.Create a container with the basic Distrinet ubuntu image, using the new profile

```
root@master:~# lxc launch ubuntu new-ubuntu --profile inet
```



​	6.Access to the container

```
root@master:~# lxc exec new-ubuntu -- bash
```




​	7.Install and configure the software inside the container

```
root@new-ubuntu:~# INSTALL AND CONFIGURE YOUR APPLICATIONS
...
...
root@new-ubuntu:~# exit
```



#### ！！Personalized hosting requires the following

​		The master host is connected to the Internet.



> Any Ubuntu or Debian based container should work with Distrinet, providing that it offers the following:
>
> - It has a listening SSHv2 server that allows root login with key authentication,
> - The root home directory is `/root`,
> - The `telnet` command is installed,
> - Net-tools is installed.
>
> Optionnally the container should have the following packages installed:
>
> - iputils-ping
> - iperf 2

```
root@master:~# lxc launch images:debian/buster debian10 --profile inet
root@master:~# lxc exec debian10 -- bash
root@debian10:~# apt update -y && apt install -y net-tools iputils-ping inetutils-telnet iperf openssh-server
root@debian10:~# exit
```

​	8.Stop the updated container

```
root@master:~# lxc stop new-ubuntu
```

​	9.Publish the new image.

```
root@master:~# lxc publish new-ubuntu --alias new-ubuntu
Container published with fingerprint: 73fa4e3f21dc9acd1bdc76228d39fe1d40880e32c425f78b3c950e8d2010b138
```

​	10.Export the container and check that it is correctly exported in the .tar.gz

```
root@master:~# lxc image export new-ubuntu new-ubuntu
Image exported successfully!

root@master:~# ls new-ubuntu.tar.gz
new-ubuntu.tar.gz
```

​	11.Distribute the new image with Ansible

```
root@ip-10-0-0-247:~# ansible all -m copy -a "src=new-ubuntu.tar.gz dest=new-ubuntu.tar.gz"
10.0.0.247 | SUCCESS => {
    "changed": false,
    "checksum": "0844f55a24b6c712448ab8dea475acfd5ee14a58",
    "dest": "new-ubuntu.tar.gz",
    "gid": 0,
    "group": "root",
    "mode": "0644",
    "owner": "root",
    "path": "new-ubuntu.tar.gz",
    "size": 308497878,
    "state": "file",
    "uid": 0
}
10.0.1.110 | CHANGED => {
    "changed": true,
    "checksum": "0844f55a24b6c712448ab8dea475acfd5ee14a58",
    "dest": "./new-ubuntu.tar.gz",
    "gid": 0,
    "group": "root",
    "md5sum": "06d7e4ee8e3213b234d56a122be070c5",
    "mode": "0644",
    "owner": "root",
    "size": 308497878,
    "src": "/root/.ansible/tmp/ansible-tmp-1587666876.21-5732-35780808233900/source",
    "state": "file",
    "uid": 0
}
```

​	12.Clean the image DB in all hosts (to avoid hash collisions)

```
root@master:~# lxc image delete new-ubuntu
root@master:~# ansible all -m raw -a "lxc image delete ubuntu"
```

​	13.Import the new image in all machines.

```
root@master:~# ansible all -m raw -a "lxc image import new-ubuntu.tar.gz --alias ubuntu --public"
10.0.1.110 | CHANGED | rc=0 >>
Shared connection to 10.0.1.110 closed.

10.0.0.247 | CHANGED | rc=0 >>
Image imported with fingerprint: 73fa4e3f21dc9acd1bdc76228d39fe1d40880e32c425f78b3c950e8d2010b138


root@master:~# ansible all -m raw -a "lxc image ls"
10.0.0.247 | CHANGED | rc=0 >>
+--------+--------------+--------+------------------------------------+--------+----------+------------------------------+
| ALIAS  | FINGERPRINT  | PUBLIC |            DESCRIPTION             |  ARCH  |   SIZE   |         UPLOAD DATE          |
+--------+--------------+--------+------------------------------------+--------+----------+------------------------------+
| switch | 5448ace25988 | yes    | Ubuntu 18.04 LTS server (20190514) | x86_64 | 278.98MB | Apr 20, 2020 at 2:21pm (UTC) |
+--------+--------------+--------+------------------------------------+--------+----------+------------------------------+
| ubuntu | 73fa4e3f21dc | yes    | Ubuntu 18.04 LTS server (20190514) | x86_64 | 294.21MB | Apr 23, 2020 at 6:37pm (UTC) |
+--------+--------------+--------+------------------------------------+--------+----------+------------------------------+

10.0.1.110 | CHANGED | rc=0 >>
+--------+--------------+--------+------------------------------------+--------+----------+------------------------------+
| ALIAS  | FINGERPRINT  | PUBLIC |            DESCRIPTION             |  ARCH  |   SIZE   |         UPLOAD DATE          |
+--------+--------------+--------+------------------------------------+--------+----------+------------------------------+
| switch | 5448ace25988 | yes    | Ubuntu 18.04 LTS server (20190514) | x86_64 | 278.98MB | Apr 20, 2020 at 2:21pm (UTC) |
+--------+--------------+--------+------------------------------------+--------+----------+------------------------------+
| ubuntu | 73fa4e3f21dc | yes    | Ubuntu 18.04 LTS server (20190514) | x86_64 | 294.21MB | Apr 23, 2020 at 6:37pm (UTC) |
+--------+--------------+--------+------------------------------------+--------+----------+------------------------------+
Shared connection to 10.0.1.110 closed.
```



