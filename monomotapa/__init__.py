#!/usr/bin/env python
"""
Copyright (C) 2014, Paul Munday.

PO Box 28228, Portland, OR, USA 97228
paul at paulmunday.net

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

There should also be a copy of the GPL in src/license.md that should be accessib
le  by going to <a href ="/license">/license<a> on this site.

As originally distributed this program will be able to display its own source co
de, which may count as conveying under the terms of the GPL v3. You should there
fore make sure the copy of the GPL (i.e. src/license.md) is left in place.

You are also free to remove this section from the code as long as any modified c
opy you distribute (including a copy that is unchanged except for removal of thi
s feature) is also licensed under the GPL version 3 (or later versions).

None of this means you have to license your own content this way, only the origi
nal source code and any modifications, or any subsequent additions that have bee
n explicitly licensed under the GPL version 3 or later. 

You are therefore free to add templates and style sheets under your own terms th
ough I would be happy if you chose to license them in the same way. 
"""
from flask import Flask
import sys
app = Flask(__name__)

from monomotapa import views
from monomotapa.config import Config, ConfigError

# The name of the file not the path
# It look for it in CWD, the apps main dir, /etc/monomatapa /etc in that order
CONFIG_FILE = 'config.json'

CONFIG = Config(CONFIG_FILE)

if 'debug' in CONFIG.config:
    app.debug = CONFIG.config['debug']
else:
    app.debug = False

try:
    app.config['enable_unit_tests'] = CONFIG.config['enable_unit_tests']
except KeyError:
    app.config['enable_unit_tests'] = False
