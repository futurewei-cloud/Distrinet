from xml.dom.expatbuilder import theDOMImplementation
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.link import TCLink
from mininet.util import dumpNodeConnections

# Standard fattree topology:
# Fat tree is a switch centric topology. Support to expand the number of paths while expanding horizontally; All switches are common devices with the same number of ports, which reduces the network construction cost.
# Specifically, the fattree structure is divided into three layers: core layer (core switch), aggregation layer (aggregation switch) and access layer (edge switch). A K-ary fattree can be summarized into five features:
# 1. Each switch has K ports;
# 2. The core layer is the top layer, with a total of (K/2) ^2 switches;
# 3. There are K pods in total, and each pod is composed of K switches. The aggregation layer and access layer account for K/2 switches respectively;
# 4. Each switch in the access layer can accommodate K/2 servers. thus, the K-ary fattree has a total of K pods, each pod can accommodate K*K/4 servers, and all pods can accommodate K*K*K/4 servers;
# 5. There are K paths between any two pods.
# In other words, there are (K/2)^2+K^2 switches and (K^3)/4 servers in the K-ary fattree topology
# The relationship between the value of K in the fattree topology and the number of switches and servers is summarized as follows:
# ---------------------------------------------------------------------------------------------------------
# Value of K            |   2   |   4   |   6   |   8   |   10  |   12  |   14  |   16  |   32  |   64
# Number of switches    |   5   |   20  |   45  |   80  |   125 |   180 |   245 |   320 |   1280|   5120
# Number of servers     |   2   |   16  |   54  |   128 |   250 |   432 |   686 |   1024|   8192|   65536
# ---------------------------------------------------------------------------------------------------------
# Custom fattree topology:
# To enable this script to support a larger topology, we add an additional parameter S to control the number of servers that each edge switch can connect to.
# In this case, there are (K/2)^2+K^2 switches and (K/2)*K*S servers in the K-ary custom topology (the valus of S in standard fattree topology is K//2).
# The relationship between the value of K, the value of S and the number of switches and servers is summarized as follows:
# ---------------------------------------------------------------------------------------------------------
# Value of K            |   2   |   4   |   6   |   8   |   10  |   12  |   14  |   16  |   32  |   64
# Number of switches    |   5   |   20  |   45  |   80  |   125 |   180 |   245 |   320 |   1280|   5120
# Number of servers     |   2S  |   8S  |   18S |   32S |   50S |   72S |   98S |   128S|   512S|   2048S
# ---------------------------------------------------------------------------------------------------------

class MyTopo(Topo):

    def __init__(self):
        super(MyTopo, self).__init__()

        # K setting
        K = 12

        # S setting
        S = K//2


        # Marking the number of switch for per level
        pod = K
        L1 = (pod//2)**2
        L2 = pod*pod//2
        L3 = L2

        # Starting create the switch
        c = []  # core switch
        a = []  # aggregate switch
        e = []  # edge switch

        # notice: switch label is a special data structure
        for i in range(L1):
            # label from 1 to n,not start with 0
            c_sw = self.addSwitch('c{}'.format(i+1))
            c.append(c_sw)

        for i in range(L2):
            a_sw = self.addSwitch('a{}'.format(L1+i+1))
            a.append(a_sw)

        for i in range(L3):
            e_sw = self.addSwitch('e{}'.format(L1+L2+i+1))
            e.append(e_sw)

        # Starting create the link between switchs
        # first the L1 level and L2 level link
        for i in range(L1):
            c_sw = c[i]
            start = i % (pod//2)
            for j in range(pod):
                self.addLink(c_sw, a[start+j*(pod//2)])

        # second the L2 level and L3 level link
        for i in range(L2):
            group = i//(pod//2)
            for j in range(pod//2):
                self.addLink(a[i], e[group*(pod//2)+j])

        # Starting create the host and create link between switchs and hosts
        for i in range(L3):
            for j in range(S):
                hs = self.addHost('h{}'.format(i*S+j+1))
                self.addLink(e[i], hs)


topos = {"mytopo": (lambda: MyTopo())}
