# Simulating-Routing-with-Mininet-and-FRRouter
 In this repository, I explore how to set up a network and use routing protocols to ensure reliable delivery of packets between hosts. More specifically, I will use Mininet and FRR to simulate the distribution of routing information between autonomous systems(AS) through BGP.

### Understanding of Technologies used
- Mininet - is a network emulator which creates a network of virtual hosts, switches, controllers, and links. Mininet hosts run standard Linux network software, and its switches support OpenFlow for highly flexible custom routing and Software-Defined Networking.
- FRRouter - is a free and open source Internet routing protocol suite for Linux and Unix platforms. It implements BGP, OSPF, RIP, and other routing protocols.

### Environment Setup

1. Install Ubuntu Virtual Machine on your PC. I recommend using the VirtualBox VM Manager to simplify the process. Refer to this [guide](https://ubuntu.com/tutorials/how-to-run-ubuntu-desktop-on-a-virtual-machine-using-virtualbox#1-overview) for help.

2. Launch Ubuntu virtual machine

3. Clone repository. You may also choose to download this repository in the virtual machine.

4. Run the following commands in the VM terminal.
```
sudo apt-get update
sudo apt-get install mininet openvswitch-testcontroller frr traceroute
-y
sudo systemctl stop openvswitch-testcontroller frr
sudo systemctl disable openvswitch-testcontroller frr
```

### Distributing routing information between Autonomous Systems via BGP

#### Step 1: Building the network topology
Before attmepting to simulate routing procedures, I first need a network to work with. In this repository, I will use the network shown below.
![1](https://github.com/chrus-chong/Simulating-Routing-with-Mininet-and-FRRouter/assets/85006125/22107e5b-d70e-46ad-a332-200253bff1ae)
Refer to the ```build()``` method in ```topology.py``` for the Mininet commands used to build this network.

Run ```sudo python3 topology.py``` to launch the network in Mininet. Here I use ONOS GUI to visualise the network and ensure that it is set up correctly.
![2](https://github.com/chrus-chong/Simulating-Routing-with-Mininet-and-FRRouter/assets/85006125/f226880b-167b-4e83-9ba6-c4bfaee13139)


#### Step 2: Setting up routing protocols
Now that the network topology has been set up, I will write the relevant router configuration files to facilitate routing between the different autonomous systems, as seen from the following figure.
![3](https://github.com/chrus-chong/Simulating-Routing-with-Mininet-and-FRRouter/assets/85006125/6c0de26d-d4ad-46aa-805f-350875578538)

After the config files for each router, I tested the network to ensure that it performs as expected.

First I ran ```pingall``` to check that all hosts and routers can reach one another.
![4](https://github.com/chrus-chong/Simulating-Routing-with-Mininet-and-FRRouter/assets/85006125/852247a9-93f1-4e08-93fd-dc96c3293fa4)

Between different autonomous systems, routers should use BGP to communicate. Within the same autonomus system (AS100), routers should use RIP to communicate. I verified that the appropriate routing protocols were being used with the help of the following commands.
- Ensuring that r110 only uses bgp to communicate with eBGP peers (r210 and r410) from different AS
![5](https://github.com/chrus-chong/Simulating-Routing-with-Mininet-and-FRRouter/assets/85006125/7df5c816-ad28-4871-b0c4-9a4d01655c54)

- Ensure that r110 uses RIP to communicate with peers within the same AS (r120, r130)
![6](https://github.com/chrus-chong/Simulating-Routing-with-Mininet-and-FRRouter/assets/85006125/cb6d8a1f-cdec-49b1-8f4a-70ef0f14d767)

#### Step 3: Failover Configuration
Now, I intend to configure the two links from r410 in a failover configuration where the r410-r110 link is the primary link, and the r410-r130 link is the secondary link. This requires the use of Multi-Exit Discriminator(MED) values which introduces a preferences for routing paths with lower MED value.
![7](https://github.com/chrus-chong/Simulating-Routing-with-Mininet-and-FRRouter/assets/85006125/897621da-a402-40ee-91be-f4d92581cb28)

I verified that this works by tracing the route taken by a packet moving from r410 to r120.
![8](https://github.com/chrus-chong/Simulating-Routing-with-Mininet-and-FRRouter/assets/85006125/58094ede-f68d-4953-b2e6-d815d677e728)

#### Step 4: Load balancing
I also configured the 2 links (R110-R410, R130-R410) in a load balancing configuration. As seen from the diagram below, traffic sent to h411 is routed over the link between r110 and r410, while traffic being sent to h412 is sent over the link between r130 and r410.
![9](https://github.com/chrus-chong/Simulating-Routing-with-Mininet-and-FRRouter/assets/85006125/6dadb8ea-6b61-488d-9395-d7c98feab40f)

To achieve this, I made use of Community Values and Local Preference to influence incoming paths and preferentially select routes with a higher local preference value (See ```frr.conf``` files for R110 R130, R410).

I verified that this works using the ```r120 ip route``` command.
![10](https://github.com/chrus-chong/Simulating-Routing-with-Mininet-and-FRRouter/assets/85006125/8bf3a95b-2f3d-4288-abbc-613aa16a13e5)


Same for R130.\
![11](https://github.com/chrus-chong/Simulating-Routing-with-Mininet-and-FRRouter/assets/85006125/1e337760-ab13-493e-bc4f-b0edab60870a)

During this project, writing routing configuration files taught me more about the commonly used routing protocols such as RIP, iBGP, eBGP . I also learnt to use route attributes such as MED and Local Preference to influence route selection.

### Disclaimer
*I only claim credit for the files in this repository that I have written.*
- *All router configuration files/frr.conf files*
- *topology.py*
