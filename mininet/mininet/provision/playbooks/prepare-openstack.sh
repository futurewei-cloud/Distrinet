#controller
brctl addbr admin-br &&\
ifconfig admin-br 192.168.0.1/16 &&\
tunctl -t admin  &&\
brctl addif admin-br admin &&\
ifconfig admin 192.168.0.3/16 &&\
ip link set admin-br up &&\
ip link set admin up

ip link delete vx_00 &&\
ip link add vx_00 type vxlan id 00 remote 172.16.50.8 local 172.16.50.3 dstport 4789 &&\
ip link set up vx_00 &&\
brctl addif admin-br vx_00 &&\
ip link set up admin-br
#master
ip link add vx_00 type vxlan id 00 remote 172.16.50.3 local 172.16.50.8 dstport 4789 &&\
ip link set up vx_00 &&\
brctl addif admin-br vx_00 &&\
ip link set up admin-br
