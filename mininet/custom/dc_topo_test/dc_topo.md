## Create Custom DC Topology
####  Establish Topology In Mininet
1.  Start Controller
    ```
    root@server03:~/ryu/ryu/app# ryu-manager simple_switch_stp_13.py
    ```
2. Establish Topology
    ```
    root@server03:~/mininet/custom# sudo mn --custom ./dc_topo.py --topo=mytopo --controller=remote
    ```
####  Establish Topology In Distrinet
1.  Start Controller
    ```
    root@server14:/home/sdn# ryu-manager /usr/lib/python3/dist-packages/ryu/app/simple_switch_stp_13.py --verbose
    ```
    ![avatar](./fig/dc_topo_controller_start_in_distrinet.png)
2. Establish Topology
    ```
    sdn@server13:~/Distrinet/mininet$ python3 bin/dmn --custom=/home/sdn/Distrinet/mininet/custom/dc_topo.py --bastion=172.16.50.34 --workers="172.16.50.34,172.16.50.35" --controller=lxcremote,ip=192.168.0.1 --topo=mytopo
    ```
     ![avatar](./fig/dc_topo_topo_establish_in_distrinet.png)
## Simple Performance Test
#### Test In Mininet
1. Pingall Test
    ![avatar](./fig/dc_topo_pingall_test_in_mininet.jpg)
2. Topo Check
    ![avatar](./fig/dc_topo_topo_check_in_mininet.jpg)
    ![avatar](./fig/dc_topo.jpg)
3. End to end bandwidth test
    ![avatar](./fig/dc_topo_e2e_bw_test.jpg)
#### Test In Distrinet
1. Pingall Test
    ![avatar](./fig/dc_topo_pingall_test_in_distrinet.png)
2. Topo Check
    ![avatar](./fig/dc_topo_topo_check_in_distrinet.jpg)
    ![avatar](./fig/dc_topo_lxc_ls_in_distrinet.png)
3. End to end bandwidth test
    ![avatar](./fig/dc_topo_e2e_bw_test_in_distrinet.png)
    Distrinet下的e2e带宽比默认mininet的带宽还要高
