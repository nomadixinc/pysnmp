#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2019, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysnmp/license.html
#
from pysnmp import nextid
from pysnmp.proto import error


class Cache(object):
    __stateReference = nextid.Integer(0xffffff)

    def __init__(self):
        self.__cacheEntries = {}

    def push(self, **securityData):
        stateReference = self.__stateReference()
        self.__cacheEntries[stateReference] = securityData
        return stateReference

    def pop(self, stateReference):
        if stateReference in self.__cacheEntries:
            return self.__cacheEntries.pop(stateReference)

        raise error.ProtocolError(
            'Cache miss for stateReference=%s at '
            '%s' % (stateReference, self))
