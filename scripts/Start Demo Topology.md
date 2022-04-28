## The custom topology file is as follows:

**(本例中文件命名为dc_topo.py)**

```python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.link import TCLink
from mininet.util import dumpNodeConnections

class MyTopo(Topo):

    def __init__(self):
        super(MyTopo,self).__init__()
    
        #Marking the number of switch for per level
        L1 = 2;    
        L2 = L1*2
        L3 = L2
    
        #Starting create the switch
        c = []    #core switch
        a = []    #aggregate switch
        e = []    #edge switch
    
        #notice: switch label is a special data structure
        for i in range(L1):
            c_sw = self.addSwitch('c{}'.format(i+1))    #label from 1 to n,not start with 0
            c.append(c_sw)
    
        for i in range(L2):
            a_sw = self.addSwitch('a{}'.format(L1+i+1))
            a.append(a_sw)
    
        for i in range(L3):
            e_sw = self.addSwitch('e{}'.format(L1+L2+i+1))
            e.append(e_sw)
    
        #Starting create the link between switchs
        #first the first level and second level link
        for i in range(L1):
            c_sw = c[i]
            for j in range(L2):
                self.addLink(c_sw,a[j])
    
        #second the second level and third level link
        for i in range(L2):
            self.addLink(a[i],e[i])
            if not i%2:
                self.addLink(a[i],e[i+1])
            else:
                self.addLink(a[i],e[i-1])
    
        #Starting create the host and create link between switchs and hosts
        for i in range(L3):
            for j in range(2):
                hs = self.addHost('h{}'.format(i*2+j+1))
                self.addLink(e[i],hs)



topos = {"mytopo":(lambda:MyTopo())}

```



## Start RYU Contoller on master node

root@master:~# ryu-manager /usr/lib/python3/dist-packages/ryu/app/simple_switch_13.py --verbose

## Start custom topology on client node

sdn@client:~/Distrinet/mininet# python3 bin/dmn --custom=PATH_TO_CUSTOM_TOPO --bastion=MASTER_IP --workers="MASTER_IP,WORKER_1,...." --controller=lxcremote,ip=192.168.0.1 --topo=mytopo
