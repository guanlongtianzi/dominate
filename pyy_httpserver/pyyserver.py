__license__ = '''
This file is part of pyy.

pyy is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

pyy is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General
Public License along with pyy.  If not, see
<http://www.gnu.org/licenses/>.
'''

import os
import sys
import imp
from urllib import unquote_plus
from http import HTTPError


class pyyscript(object):
  def __init__(self, root, fname):
    self.root   = root
    self.fname = os.path.join(self.root, unquote_plus(fname))
    self.mname = os.path.basename(fname).split('.')[0]
    self.dname = os.path.dirname(fname)
    self.mtime = 0
    self.module = None


  def load_module(self):
    if not self.fname.startswith(self.root):
      raise HTTPError(403)

    if not os.path.exists(self.fname):
      raise HTTPError(404)

    if not os.path.isfile(self.fname):
      raise HTTPError(403)
    
    if os.path.getmtime(self.fname) == self.mtime:
      return self.module

    f = open(self.fname, 'U')
    sys.path.append(self.dname) # do we even need this?

    self.module = imp.load_module(self.mname, f, self.fname, ('.py', 'U', 1))
    self.mtime  = os.path.getmtime(self.fname)
    
    sys.path.remove(self.dname)
    return self.module

  def handle(self, handler, req, res, *args):
    m = self.load_module()
    
    h = getattr(m, req.method.lower(),
        getattr(m, 'handle', None))
    
    if not h:
      raise HTTPError(405) # method not allowed
    
    return  h(handler, req, res, *args)

  def handle_error(self, handler, req, res, status, *args):
    m = self.load_module()
    
    h = getattr(m, 'handle_error', None)
    if not h: return
    return  h(handler, req, res, status, *args)



