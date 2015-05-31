# SNMP engine
import os
import sys
import tempfile
from pysnmp.proto.rfc3412 import MsgAndPduDispatcher
from pysnmp.proto.mpmod.rfc2576 import SnmpV1MessageProcessingModel, \
     SnmpV2cMessageProcessingModel
from pysnmp.proto.mpmod.rfc3412 import SnmpV3MessageProcessingModel
from pysnmp.proto.secmod.rfc2576 import SnmpV1SecurityModel, \
     SnmpV2cSecurityModel
from pysnmp.proto.secmod.rfc3414 import SnmpUSMSecurityModel
from pysnmp.proto.acmod import rfc3415, void
from pysnmp.entity import observer
from pysnmp import debug
from pysnmp import error

class SnmpEngine:
    def __init__(self, snmpEngineID=None, maxMessageSize=65507,
                 msgAndPduDsp=None):
        self.cache = {}
        
        self.observer = observer.MetaObserver()

        if msgAndPduDsp is None:
            self.msgAndPduDsp = MsgAndPduDispatcher()
        else:
            self.msgAndPduDsp = msgAndPduDsp
        self.messageProcessingSubsystems = {
            SnmpV1MessageProcessingModel.messageProcessingModelID:
            SnmpV1MessageProcessingModel(),
            SnmpV2cMessageProcessingModel.messageProcessingModelID:
            SnmpV2cMessageProcessingModel(),
            SnmpV3MessageProcessingModel.messageProcessingModelID:
            SnmpV3MessageProcessingModel()
        }
        self.securityModels = {
            SnmpV1SecurityModel.securityModelID: SnmpV1SecurityModel(),
            SnmpV2cSecurityModel.securityModelID: SnmpV2cSecurityModel(),
            SnmpUSMSecurityModel.securityModelID: SnmpUSMSecurityModel()
        }
        self.accessControlModel = {
            void.Vacm.accessModelID: void.Vacm(),
            rfc3415.Vacm.accessModelID: rfc3415.Vacm()
        }
        
        self.transportDispatcher = None
        
        if self.msgAndPduDsp.mibInstrumController is None:
            raise error.PySnmpError(
                'MIB instrumentation does not yet exist'
            )
        snmpEngineMaxMessageSize, = self.msgAndPduDsp.mibInstrumController.mibBuilder.importSymbols('__SNMP-FRAMEWORK-MIB', 'snmpEngineMaxMessageSize')
        snmpEngineMaxMessageSize.syntax = snmpEngineMaxMessageSize.syntax.clone(maxMessageSize)
        snmpEngineBoots, = self.msgAndPduDsp.mibInstrumController.mibBuilder.importSymbols('__SNMP-FRAMEWORK-MIB', 'snmpEngineBoots')
        snmpEngineBoots.syntax = snmpEngineBoots.syntax + 1        
        origSnmpEngineID, = self.msgAndPduDsp.mibInstrumController.mibBuilder.importSymbols('__SNMP-FRAMEWORK-MIB', 'snmpEngineID')

        if snmpEngineID is None:
            self.snmpEngineID = origSnmpEngineID.syntax
        else:
            origSnmpEngineID.syntax = origSnmpEngineID.syntax.clone(snmpEngineID)
            self.snmpEngineID = origSnmpEngineID.syntax

            debug.logger & debug.flagApp and debug.logger('SnmpEngine: using custom SNMP Engine ID: %s' % self.snmpEngineID.prettyPrint())

            # Attempt to make some of snmp Engine settings persistent.
            # This should probably be generalized as a non-volatile MIB store.

            persistentPath = os.path.join(tempfile.gettempdir(), '__pysnmp', self.snmpEngineID.prettyPrint())

            debug.logger & debug.flagApp and debug.logger('SnmpEngine: using persistent directory: %s' % persistentPath)

            if not os.path.exists(persistentPath):
                try:
                    os.makedirs(persistentPath)
                except OSError:
                    return

            f = os.path.join(persistentPath, 'boots')
            try:
                snmpEngineBoots.syntax = snmpEngineBoots.syntax.clone(open(f).read())
            except:
                pass

            try:
                snmpEngineBoots.syntax = snmpEngineBoots.syntax + 1
            except:
                snmpEngineBoots.syntax = snmpEngineBoots.syntax.clone(1)

            try:
                fd, fn = tempfile.mkstemp(dir=persistentPath)
                os.write(fd, snmpEngineBoots.syntax.prettyPrint())
                os.close(fd)
                os.rename(fn, f)
            except:
                debug.logger & debug.flagApp and debug.logger('SnmpEngine: could not stored SNMP Engine Boots: %s' % sys.exc_info()[1])
            else:
                debug.logger & debug.flagApp and debug.logger('SnmpEngine: stored SNMP Engine Boots: %s' % snmpEngineBoots.syntax.prettyPrint())

    # Transport dispatcher bindings
    
    def __receiveMessageCbFun(
        self,
        transportDispatcher,
        transportDomain,
        transportAddress,
        wholeMsg
        ):
        self.msgAndPduDsp.receiveMessage(
            self, transportDomain, transportAddress, wholeMsg
        )

    def __receiveTimerTickCbFun(self, timeNow):
        self.msgAndPduDsp.receiveTimerTick(self, timeNow)
        for mpHandler in self.messageProcessingSubsystems.values():
            mpHandler.receiveTimerTick(self, timeNow)
        for smHandler in self.securityModels.values():
            smHandler.receiveTimerTick(self, timeNow)

    def registerTransportDispatcher(self, transportDispatcher, recvId=None):
        if self.transportDispatcher is not None and \
                self.transportDispatcher is not transportDispatcher:
            raise error.PySnmpError(
                'Transport dispatcher already registered'
            )
        transportDispatcher.registerRecvCbFun(
            self.__receiveMessageCbFun, recvId
        )
        if self.transportDispatcher is None:
            transportDispatcher.registerTimerCbFun(
                self.__receiveTimerTickCbFun
            )
            self.transportDispatcher = transportDispatcher

    def unregisterTransportDispatcher(self, recvId=None):
        if self.transportDispatcher is None:
            raise error.PySnmpError(
                'Transport dispatcher not registered'
            )
        self.transportDispatcher.unregisterRecvCbFun(recvId)
        self.transportDispatcher.unregisterTimerCbFun()
        self.transportDispatcher = None

    def getMibBuilder(self):
        return self.msgAndPduDsp.mibInstrumController.mibBuilder

    # User app may attach opaque objects to SNMP Engine
    def setUserContext(self, **kwargs):
        self.cache.update(
            dict([('__%s' % k, kwargs[k]) for k in kwargs])
        )

    def getUserContext(self, arg):
        return self.cache.get('__%s' % arg)

    def delUserContext(self, arg):
        try:
            del self.cache['__%s' % arg]
        except KeyError:
            pass

