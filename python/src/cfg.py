#    EVE-Central.com Contribtastic
#    Copyright (C) 2005-2010 Yann Ramin
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License (in file COPYING) for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


from sys import argv

from evec_upload.config import Config
config = Config()

if len(argv) == 3:
    k = argv[1]
    v = argv[2]
    print "OLD %s: %s" % (k, config.config_obj.get(k, None),)
    config[k] = v
elif len(argv) == 2:
    k = argv[1]
    print "%s: %s" % (k, config.config_obj.get(k,None),)
elif len(argv) == 1:
    for k in config.config_obj.keys():
        print "%s: %s" % (k, config[k],)
else:
    raise USAGE


