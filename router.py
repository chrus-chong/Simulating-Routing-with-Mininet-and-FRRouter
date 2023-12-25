from contextlib import contextmanager
from os import getcwd

from mininet.node import Node


class Router(Node):
    def __init__(self, *args, **kwargs):
        super(Router, self).__init__(*args, inNamespace=True, **kwargs)

    @contextmanager
    def routerContext(self):
        working_dir = getcwd()
        self.cmd("cd %s" % self.name)
        yield
        self.cmd("cd %s" % working_dir)

    def config(self, **params):
        super(Router, self).config(**params)
        self.cmd("sysctl net.ipv4.ip_forward=1")
        if "loopback" in params:
            self.loopback = params["loopback"]
            self.cmd(f'ip addr add {params["loopback"]} dev lo')

    def terminate(self):
        self.cmd("sysctl net.ipv4.ip_forward=0")
        super(Router, self).terminate()

    def addHost(self, ip, interface):
        self.setHostRoute(ip, interface)


class FRRRouter(Router):
    def __init__(self, name, **params):
        if "privateDirs" not in params:
            params["privateDirs"] = [
                "/etc/frr",
                "/var/run/frr",
            ]
        params["ip"] = None
        super(FRRRouter, self).__init__(name, **params)

    def config(self, **params):
        super(FRRRouter, self).config(**params)

        with self.routerContext():
            self.cmd("install -m 640 -o frr -g frr frr.conf /etc/frr")
            self.cmd(f'echo "hostname {self.name}" > /etc/frr/vtysh.conf')
            self.cmd("/usr/lib/frr/zebra -f /etc/frr/frr.conf --log file:./zebra.log --log-level debugging -d")
            self.cmd("/usr/lib/frr/ripd -f /etc/frr/frr.conf --log file:./ripd.log --log-level debugging -d")
            self.cmd("/usr/lib/frr/bgpd -f /etc/frr/frr.conf --log file:./bgpd.log --log-level debugging -d")

    def terminate(self):
        with self.routerContext():
            self.cmd("kill -9 `cat /var/run/frr/zebra.pid`")
            self.cmd("kill -9 `cat /var/run/frr/ripd.pid`")
            self.cmd("kill -9 `cat /var/run/frr/bgpd.pid`")

        super(FRRRouter, self).terminate()


class BIRDRouter(Router):
    def __init__(self, name, **params):
        if "privateDirs" not in params:
            params["privateDirs"] = [
                "/etc/bird",
                "/var/run/bird",
            ]
        params["ip"] = None
        super(BIRDRouter, self).__init__(name, **params)

    def config(self, **params):
        super(BIRDRouter, self).config(**params)

        self.cmd("install -m 640 -o bird -g bird ../lib/constants.conf /etc/bird")
        self.cmd("install -m 640 -o bird -g bird ../lib/filters.conf /etc/bird")

        with self.routerContext():
            self.cmd("install -m 640 -o bird -g bird bird.conf /etc/bird")
            self.cmd("bird -D bird.log -u bird -g bird")

    def terminate(self):
        with self.routerContext():
            self.cmd("birdc down")

        super(BIRDRouter, self).terminate()
