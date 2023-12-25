import atexit

from mininet.cli import CLI
from mininet.link import Link
from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from router import FRRRouter

net = None

class Topology(Topo):
    def build(self):
        #########################  STEP 1  ###########################
        
        # Build all routers
        self.addNode('r110', cls=FRRRouter, loopback='100.100.1.1/32')
        self.addNode('r120', cls=FRRRouter, loopback='100.100.1.2/32')
        self.addNode('r130', cls=FRRRouter, loopback='100.100.1.3/32')
        self.addNode('r210', cls=FRRRouter, loopback='100.100.2.1/32')
        self.addNode('r310', cls=FRRRouter, loopback='100.100.3.1/32')
        self.addNode('r410', cls=FRRRouter, loopback='100.100.4.1/32')
        
        # Build all hosts
        # Initially, I did not add defaultRoute argument
        # This will later cause problems in Step 2 as hosts will not be able to ping other routers
        self.addHost('h211', ip='10.2.1.1/24', defaultRoute=f'via 10.2.1.254')
        self.addHost('h311', ip='10.3.1.1/24', defaultRoute=f'via 10.3.1.254')
        self.addHost('h411', ip='10.4.1.1/25', defaultRoute=f'via 10.4.1.126')
        self.addHost('h412', ip='10.4.1.129/25', defaultRoute=f'via 10.4.1.254')
        
        # Build all host-router links
        self.addLink('r210', 'h211', intfName1='r210-eth0', params1={'ip':'10.2.1.254/24'})
        self.addLink('r310', 'h311', intfName1='r310-eth0', params1={'ip':'10.3.1.254/24'})
        self.addLink('r410', 'h411', intfName1='r410-eth0', params1={'ip':'10.4.1.126/25'})
        self.addLink('r410', 'h412', intfName1='r410-eth1', params1={'ip':'10.4.1.254/25'})
        
        # Build all router-router links
        self.addLink('r110', 'r120',
        	intfName1='r110-eth1', params1={'ip':'192.168.1.0/31'},
        	intfName2='r120-eth1', params2={'ip':'192.168.1.1/31'})
        self.addLink('r110', 'r210',
        	intfName1='r110-eth2', params1={'ip':'172.17.1.0/31'},
        	intfName2='r210-eth1', params2={'ip':'172.17.1.1/31'})
        self.addLink('r110', 'r410',
        	intfName1='r110-eth3', params1={'ip':'172.17.3.0/31'},
        	intfName2='r410-eth2', params2={'ip':'172.17.3.1/31'})
        self.addLink('r120', 'r130',
        	intfName1='r120-eth2', params1={'ip':'192.168.1.2/31'},
        	intfName2='r130-eth1', params2={'ip':'192.168.1.3/31'})
        self.addLink('r130', 'r310',
        	intfName1='r130-eth2', params1={'ip':'172.17.2.0/31'},
        	intfName2='r310-eth1', params2={'ip':'172.17.2.1/31'})
        self.addLink('r130', 'r410',
        	intfName1='r130-eth3', params1={'ip':'172.17.4.0/31'},
        	intfName2='r410-eth3', params2={'ip':'172.17.4.1/31'})
        pass


def startNetwork():
    info("*** Creating the network\n")
    topology = Topology()

    global net
    net = Mininet(topo=topology, link=Link, autoSetMacs=True)

    info("*** Starting the network\n")
    net.start()
    info("*** Running CLI\n")
    CLI(net)


def stopNetwork():
    if net is not None:
        net.stop()


if __name__ == "__main__":
    # Force cleanup on exit by registering a cleanup function
    atexit.register(stopNetwork)

    # Tell mininet to print useful information
    setLogLevel("info")
    startNetwork()
