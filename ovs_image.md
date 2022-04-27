本文档为创建并打包`ovs_image`的`docker`镜像文档的教程。

[toc]

## 含有ovs的docker容器创建

第一部分为新建`docker`容器，并在容器内安装`openvswitch`。

### 1.创建容器

- 新建`docker`容器，使用镜像`ubuntu:18.04`，命名为`ovs`：

```shell
docker run -it --privileged --name ovs ubuntu:18.04
```

此步在虚拟机中完成，此部分其余步骤均在`ovs` `docker`容器中完成。



### 2.下载ovs

- 更新`apt`，安装`git`并下载`openvswitch`：（以下步骤均在容器内）

```shell
apt update
apt install git
git clone https://github.com/openvswitch/ovs.git
```

下载完成后，会在当前目录生成文件夹`/ovs`。



### 3.安装相关依赖

- 安装相关依赖包：

```shell
apt install make gcc python3

# 安装libssl、libcap-ng、unbound
apt install libssl-dev libcap-ng-utils unbound

# 安装autoconf、libtool
apt install autoconf libtool
```

注：安装`unbound`包时可能会出现以下报错：

```shell
Err:1 http://archive.ubuntu.com/ubuntu bionic/universe amd64 libfstrm0 amd64 0.3.0-1build1
  Connection failed [IP: 91.189.91.38 80]
```

此时需要对容器进行换源：

```shell
cp /etc/apt/sources.list /etc/apt/sources.list.backup
rm /etc/apt/sources.list
#阿里云源
echo -e "deb http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse\ndeb http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse\ndeb http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse\ndeb http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse\ndeb http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse\ndeb-src http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse\ndeb-src http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse\ndeb-src http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse\ndeb-src http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse\ndeb-src http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse\n" >> /etc/apt/sources.list
apt update
apt upgrade

#换源后重新安装unbound
apt install unbound
```



### 4.编译安装ovs及初始化

- 编译安装`ovs`：

```shell
cd /ovs
./boot.sh
./configure
make
make install
```

- 初始化`ovs`数据库：

```shell
mkdir -p /usr/local/etc/penvswitch
ovsdb-tool create /usr/local/etc/openvswitch/conf.db vswitchd/vswitch.ovsschema

export PATH=$PATH:/usr/local/share/openvswitch/scripts
ovs-ctl start
ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock \
                     --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
                     --private-key=db:Open_vSwitch,SSL,private_key \
                     --certificate=db:Open_vSwitch,SSL,certificate \
                     --bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert \
                     --pidfile --detach
ovs-vsctl --no-wait init
ovs-vswitchd --pidfile --detach
```

- 安装完成，验证：

```shell
ovs-vsctl --version
ovs-appctl --version
ovs-appctl version
```



## 镜像打包

第二部分为将第一部分创建的容器打包成镜像。



### 1.退出docker容器

目前默认仍在容器中，使用快捷键`ctrl+p ctrl+q`退出容器。



### 2.将容器保存为镜像

```shell
docker commit [-m "提交的描述信息"] [-a "创建者"] 容器名称|容器ID 生成的镜像名[:标签名]

# 注释：
## []为可选项
## -m= : 为镜像添加描述信息
## -a= : 为镜像添加创建者信息
## 容器名称|容器ID : 当前要被打包的容器名称或容器ID
## 生成的镜像名[:标签名] : 指定镜像名称或标签名称

# 本例：
docker commit -m "ovs_image" -a "ycyz" ovs ovs_image
```

执行该命令后，镜像`ovs_image`制作成功，运行如下命令查看所有`docker`镜像：

```shell
docker images
```



### 3. tar压缩文件打包

若需要打包成`tar`压缩文件，运行如下命令：

```shell
# 进入目标目录
cd /home/sdn/Desktop
# 打包tar压缩文件
docker export ovs > ovs_image.tar
```
