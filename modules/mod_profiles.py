"""A module for finding what other profiles and groups are in the system aside from 
the main ones:
_*.plist services and groups, daemon, root and nobody default plists
"""

import logging
import os
import plistlib
import sys
from collections import OrderedDict

# IMPORT STATIC VARIABLES FROM MAIN
from __main__ import (data_writer, inputdir)

# IMPORT FUNCTIONS FROM COMMON.FUNCTIONS
from .common.functions import cocoa_time, multiglob, read_bplist, stats2, get_db_column_headers, finditem

_modName = __name__.split('_')[-1]
_modVers = '1.0.5'
log = logging.getLogger(_modName)

def module():

    user_list = '/private/var/db/dslocal/nodes/Default/users/'
    user_output = []

    _headers = ['uid', 'gid', 'name', 'realname', 'dsAttrTypeStandard:NetworkUser', 'dsAttrTypeStandard:OIDCProvider']
    _output = data_writer(_modName, _headers)

    # get all the users that are not the default ones by parsing them 
    for u in os.listdir(user_list):
        if not u.startswith("_"):
            user_output.append(u)

    for i in range(len(user_output)):
        open_plist = user_list + user_output[i]
        user_plist = []

        if sys.version_info[0] < 3:
            # TODO
            user_plist = plistlib.readPlist(os.path.join(inputdir, str(user_list + user_output[i])))
        else:
            with open(os.path.join(inputdir, open_plist), 'rb') as fp:
                userinfo = plistlib.load(fp)

                record = OrderedDict((h, '') for h in _headers)

                if "uid" in userinfo:
                    record['uid'] = userinfo['uid']
                if 'gid' in userinfo:
                    record['gid'] = userinfo['gid']
                if "name" in userinfo:
                    record['name'] = userinfo["name"]
                if "realname" in userinfo:
                    record['real name'] = userinfo["realname"]
                if 'dsAttrTypeStandard:NetworkUser' in userinfo:
                    record['NetworkUser'] = userinfo['dsAttrTypeStandard:NetworkUser']
                if 'dsAttrTypeStandard:OIDCProvider' in userinfo:
                    record['OIDCProvider'] = userinfo['dsAttrTypeStandard:OIDCProvider']

                _output.write_record(record)

    _output.flush_record()

if __name__ == "__main__":
    print("This is an AutoMacTC module, and is not meant to be run stand-alone.")
    print("Exiting.")
    sys.exit(0)
else:
    module()