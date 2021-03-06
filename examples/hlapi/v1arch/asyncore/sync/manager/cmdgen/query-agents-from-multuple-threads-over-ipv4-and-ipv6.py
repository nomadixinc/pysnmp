"""
Query Agents from multiple threads
++++++++++++++++++++++++++++++++++

Send a bunch of SNMP GET requests simultaneously using the following options:

* process 4 GET requests in 3 parallel threads
* with SNMPv1, community 'public' and 
  with SNMPv2c, community 'public' and
* over IPv4/UDP and 
  over IPv6/UDP
* to an Agent at demo.snmplabs.com:161 and
  to an Agent at demo.snmplabs.com:1161 and
  to an Agent at [::1]:161
* for instances of SNMPv2-MIB::sysDescr.0 and
  SNMPv2-MIB::sysLocation.0 MIB objects
* with MIB lookup enabled

Functionally similar to:

| $ snmpget -v1 -c public demo.snmplabs.com SNMPv2-MIB::sysDescr.0 SNMPv2-MIB::sysLocation.0
| $ snmpget -v2c -c public demo.snmplabs.com SNMPv2-MIB::sysDescr.0 SNMPv2-MIB::sysLocation.0
| $ snmpget -v2c -c public demo.snmplabs.com:1161 SNMPv2-MIB::sysDescr.0 SNMPv2-MIB::sysLocation.0
| $ snmpget -v2c -c public '[::1]' SNMPv2-MIB::sysDescr.0 SNMPv2-MIB::sysLocation.0

"""#
from sys import version_info
from threading import Thread
from pysnmp.hlapi.v1arch import *

if version_info[0] == 2:
    from Queue import Queue
else:
    from queue import Queue

# List of targets in the following format:
# ( ( authData, transportTarget, varNames ), ... )
TARGETS = (
    # 1-st target (SNMPv1 over IPv4/UDP)
    (CommunityData('public', mpModel=0),
     UdpTransportTarget(('demo.snmplabs.com', 161)),
     (ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)),
      ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysLocation', 0)))),

    # 2-nd target (SNMPv2c over IPv4/UDP)
    (CommunityData('public'),
     UdpTransportTarget(('demo.snmplabs.com', 161)),
     (ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)),
      ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysLocation', 0)))),

    # 3-nd target (SNMPv2c over IPv4/UDP) - same community and
    # different transport address.
    (CommunityData('public'),
     Udp6TransportTarget(('localhost', 161)),
     (ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysContact', 0)),
      ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0)))),

    # 4-th target (SNMPv2c over IPv4/UDP) - same community and
    # different transport port.
    (CommunityData('public'),
     UdpTransportTarget(('demo.snmplabs.com', 1161)),
     (ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)),
      ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysLocation', 0)))),

    # N-th target
    # ...
)


class Worker(Thread):
    def __init__(self, requests, responses):
        Thread.__init__(self)
        self.snmpDispatcher = SnmpDispatcher()
        self.requests = requests
        self.responses = responses
        self.setDaemon(True)
        self.start()

    def run(self):
        while True:
            authData, transportTarget, varBinds = self.requests.get()

            self.responses.append(
                next(getCmd(self.snmpDispatcher,
                     authData, transportTarget, *varBinds, lookupMib=True))
            )

            if hasattr(self.requests, 'task_done'):  # 2.5+
                self.requests.task_done()


class ThreadPool(object):
    def __init__(self, num_threads):
        self.requests = Queue(num_threads)
        self.responses = []
        for _ in range(num_threads):
            Worker(self.requests, self.responses)

    def addRequest(self, authData, transportTarget, varBinds):
        self.requests.put((authData, transportTarget, varBinds))

    def getResponses(self):
        return self.responses

    def waitCompletion(self):
        if hasattr(self.requests, 'join'):
            self.requests.join()  # 2.5+
        else:
            from time import sleep
            # this is a lame substitute for missing .join()
            # adding an explicit synchronization might be a better solution
            while not self.requests.empty():
                sleep(1)


pool = ThreadPool(3)

# Submit GET requests
for authData, transportTarget, varBinds in TARGETS:
    pool.addRequest(authData, transportTarget, varBinds)

# Wait for responses or errors
pool.waitCompletion()

# Walk through responses
for errorIndication, errorStatus, errorIndex, varBinds in pool.getResponses():

    if errorIndication:
        print(errorIndication)

    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))

    else:
        for varBind in varBinds:
            print(' = '.join([x.prettyPrint() for x in varBind]))
