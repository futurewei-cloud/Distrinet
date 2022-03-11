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