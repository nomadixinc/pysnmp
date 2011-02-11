# SNMPv3 error-indication values.
# Object below could be compared with literals thus are backward-compatible
# with original pysnmperror-indication values.
from string import lower

class ErrorIndication:
    def __init__(self, descr=None):
        self.__value = self.__descr = lower(self.__class__.__name__[0]) + self.__class__.__name__[1:]
        if descr: self.__descr = descr
    def __cmp__(self, other):
        if self is other or isinstance(other, self.__class__):
            return 0
        else:
            return cmp(self.__value, other)
    def __str__(self): return self.__descr

# SNMP message processing errors

class ParseError(ErrorIndication): pass
parseError = ParseError('SNMP message deserialization error')

class UnsupportedMsgProcessingModel(ErrorIndication): pass
unsupportedMsgProcessingModel = UnsupportedMsgProcessingModel('Unknown SNMP message processing model ID encountered')

class UnknownPDUHandler(ErrorIndication): pass
unknownPDUHandler = UnknownPDUHandler('Unhandled PDU type encountered')

class UnsupportedPDUtype(ErrorIndication): pass
unsupportedPDUtype = UnsupportedPDUtype('Unsupported SNMP PDU type encountered')

class RequestTimedOut(ErrorIndication): pass
requestTimedOut = RequestTimedOut('No SNMP response received before timeout')

class EmptyResponse(ErrorIndication): pass
emptyResponse = EmptyResponse('Empty SNMP response message')

class NonReportable(ErrorIndication): pass
nonReportable = NonReportable('Report PDU generation not attempted')

class DataMismatch(ErrorIndication): pass
dataMismatch = DataMismatch('SNMP request/response parameters mismatched')

class EngineIDMispatch(ErrorIndication): pass
engineIDMispatch = EngineIDMispatch('SNMP engine ID mismatch encountered')

class UnknownEngineID(ErrorIndication): pass
unknownEngineID = UnknownEngineID('Unknown SNMP engine ID encountered')

class TooBig(ErrorIndication): pass
tooBig = TooBig('SNMP message will be too big')

class LoopTerminated(ErrorIndication):pass
loopTerminated = LoopTerminated('Infinite SNMP entities talk terminated')

class InvalidMsg(ErrorIndication):pass
invalidMsg = InvalidMsg('Invalid SNMP message header parameters encountered')

# SNMP security modules errors

class UnknownCommunityName(ErrorIndication): pass
unknownCommunityName = UnknownCommunityName('Unknown SNMP community name encountered')

class NoEncryption(ErrorIndication): pass
noEncryption = NoEncryption('No encryption services configured')

class EncryptionError(ErrorIndication): pass
encryptionError = EncryptionError('Ciphering services not available')

class DecryptionError(ErrorIndication): pass
decryptionError = DecryptionError('Ciphering services not available or ciphertext is broken')

class NoAuthentication(ErrorIndication): pass
noAuthentication = NoAuthentication('No authentication services configured')

class AuthenticationError(ErrorIndication): pass
authenticationError = AuthenticationError('Ciphering services not available or bad parameters')

class AuthenticationFailure(ErrorIndication): pass
authenticationFailure = AuthenticationFailure('Authenticator mismatched')

class UnsupportedAuthProtocol(ErrorIndication): pass
unsupportedAuthProtocol = UnsupportedAuthProtocol('Authentication protocol is not supprted')

class UnsupportedPrivProtocol(ErrorIndication): pass
unsupportedPrivProtocol = UnsupportedPrivProtocol('Privacy protocol is not supprted')

class UnknownSecurityName(ErrorIndication): pass
unknownSecurityName = UnknownSecurityName('Unknown SNMP security name encountered')

class UnsupportedSecurityModel(ErrorIndication): pass
unsupportedSecurityModel = UnsupportedSecurityModel('Unsupported SNMP security model')

class UnsupportedSecurityLevel(ErrorIndication): pass
unsupportedSecurityLevel = UnsupportedSecurityLevel('Unsupported SNMP security level')

class NotInTimeWindow(ErrorIndication): pass
notInTimeWindow = NotInTimeWindow('SNMP message timing parameters not in windows of trust')

# SNMP access-control errors

class NoSuchView(ErrorIndication): pass
noSuchView = NoSuchView('No such MIB view currently exists')

class NoAccessEntry(ErrorIndication): pass
noAccessEntry = NoAccessEntry('Access to MIB node denined')

class NoGroupName(ErrorIndication): pass
noGroupName = NoGroupName('No such VACM group configured')

class NoSuchContext(ErrorIndication): pass
noSuchContext = NoSuchContext('SNMP context now found')

class NotInView(ErrorIndication): pass
notInView = NotInView('Requested OID is out of MIB view')

class AccessAllowed(ErrorIndication): pass
accessAllowed = AccessAllowed()

class OtherError(ErrorIndication): pass
otherError = OtherError('Unspecified SNMP engine error occurred')

# SNMP Apps errors

class OidNotIncreasing(ErrorIndication): pass
oidNotIncreasing = OidNotIncreasing('OIDs are not increasing')
