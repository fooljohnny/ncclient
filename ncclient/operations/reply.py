# Copyright 2009 Shikhar Bhushan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from xml.etree import cElementTree as ET

from ncclient.content import multiqualify as _
from ncclient.content import unqualify as __

import logging
logger = logging.getLogger('ncclient.operations.reply')

class RPCReply:
    
    def __init__(self, raw):
        self._raw = raw
        self._parsed = False
        self._errors = []
    
    def __repr__(self):
        return self._raw
    
    def parse(self):
        root = ET.fromstring(self._raw) # <rpc-reply> element
        
        # per rfc 4741 an <ok/> tag is sent when there are no errors or warnings
        oktags = _('ok')
        for oktag in oktags:
            if root.find(oktag) is not None:
                logger.debug('found %s' % oktag)
                self._parsed = True
                return
        
        # create RPCError objects from <rpc-error> elements
        errtags = _('rpc-error')
        for errtag in errtags:
            for err in root.getiterator(errtag): # a particular <rpc-error>
                d = {}
                for err_detail in err.getchildren(): # <error-type> etc..
                    d[__(err_detail)] = err_detail.text
                self._errors.append(RPCError(d))
            if self._errors:
                break
        self._parsed = True
    
    @property
    def raw(self):
        return self._raw
    
    @property
    def ok(self):
        if not self._parsed: self.parse()
        return not bool(self._errors) # empty list = false
    
    @property
    def errors(self):
        'List of RPCError objects. Will be empty if no <rpc-error> elements in reply.'
        if not self._parsed: self.parse()
        return self._errors


class RPCError(Exception): # raise it if you like
    
    def __init__(self, err_dict):
        self._dict = err_dict
        if self.message is not None:
            Exception.__init__(self, self.message)
        else:
            Exception.__init__(self)
    
    @property
    def raw(self):
        return self._element.tostring()
    
    @property
    def type(self):
        return self.get('error-type', None)
    
    @property
    def severity(self):
        return self.get('error-severity', None)
    
    @property
    def tag(self):
        return self.get('error-tag', None)
    
    @property
    def path(self):
        return self.get('error-path', None)
    
    @property
    def message(self):
        return self.get('error-message', None)
    
    @property
    def info(self):
        return self.get('error-info', None)

    ## dictionary interface
    
    __getitem__ = lambda self, key: self._dict.__getitem__(key)
    
    __iter__ = lambda self: self._dict.__iter__()
    
    __contains__ = lambda self, key: self._dict.__contains__(key)
    
    keys = lambda self: self._dict.keys()
    
    get = lambda self, key, default: self._dict.get(key, default)
        
    iteritems = lambda self: self._dict.iteritems()
    
    iterkeys = lambda self: self._dict.iterkeys()
    
    itervalues = lambda self: self._dict.itervalues()
    
    values = lambda self: self._dict.values()
    
    items = lambda self: self._dict.items()
    
    __repr__ = lambda self: repr(self._dict)