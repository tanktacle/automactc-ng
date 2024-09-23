"""A module to read what are the LaunchAgents and LaunchDaemons in 
the system.
"""

import logging
import os
import sys
import pwd
import grp
import time
import plistlib
from collections import OrderedDict

# IMPORT STATIC VARIABLES FROM MAIN
from __main__ import (OSVersion, archive, data_writer, forensic_mode,
                      full_prefix, inputdir, no_tarball, outputdir, quiet,
                      startTime)

# IMPORT FUNCTIONS FROM COMMON.FUNCTIONS
from .common.dateutil import parser
from .common.functions import cocoa_time, multiglob, read_bplist, stats2, get_db_column_headers

_modName = __name__.split('_')[-1]
_modVers = '1.0.5'
log = logging.getLogger(_modName)

INVALID_EXTENSIONS = {'.app', '.framework', '.lproj', '.plugin', '.kext', '.osax', '.bundle', '.driver', '.wdgt', '.Office', '.blacklight'}
OUTPUT_BUFFER_CAP = 100000  # cap num entries to keep in output buffer
WORKERS = 5  				# number of parallel threads to run when multithreading
HEADERS = ['mode', 'size', 'owner', 'uid', 'gid', 'mtime', 'atime', 'ctime', 'btime', 'path', 'name', 'sha256', 'md5', 'quarantine', 'wherefrom_1', 'wherefrom_2', 'downloaddate', 'code_signatures']
PLIST_ELEMS = ['RunAtLoad','ProgramArguments', 'Program', 'Sockets']
counter = 0
output = None

# INFO: I removed the system ones because they have a huge output, tweak it in all_agents if you want it
launch_agents = '/Library/LaunchAgents/' # Per-user agents provided by the administrator.
launch_daemons = '/Library/LaunchDaemons/' # System wide daemons provided by the administrator.
u_launch_agents = '~/Library/LaunchAgents' # Per-user agents provided by the user.
s_launch_agents = '/System/Library/LaunchAgents/' # OS X Per-user agents.
s_launch_daemons = '/System/Library/LaunchDaemons/' # OS X System wide daemons.

all_agents = [launch_agents, launch_daemons, u_launch_agents]

file_opts = {}

def _is_valid_file(file):
	"""
	Returns True if file should be included in parse set.
	Omits files with invalid extension (ex. bundles)
	"""
	if file == "":
		return False
	ext = os.path.splitext(file)
	return ext[1] not in INVALID_EXTENSIONS

def group_user(f):

    stat_info = os.stat(f)
    uid = stat_info.st_uid
    gid = stat_info.st_gid

    user = pwd.getpwuid(uid)[0]
    group = grp.getgrgid(gid)[0]
    file_opts[f] = list((user,group))

    # get the date of creation/runtime
    ti_c = os.path.getctime(f)
    ti_m = os.path.getmtime(f)

    c_ti = time.ctime(ti_c)
    m_ti = time.ctime(ti_m)

    file_opts[f].append(c_ti)
    file_opts[f].append(m_ti)

def find_keyes(f):
     with open(f, 'rb') as fp:
        userinfo = plistlib.load(fp)

        for k in userinfo:
            for j in PLIST_ELEMS:
                if k == j:
                    file_opts[f].append(list((k,userinfo[k])))
                 
def module():
    _headers = ['launchitem', 'owner', 'group', 'creation time', 'modified time', 'arguments', 'arguments2', 'arguments3', 'arguments4']
    _output = data_writer(_modName, _headers)

    for k,v in file_opts.items():   
        record = OrderedDict((h, '') for h in _headers)

        if k is not None:
            record['launchitem'] = k
        if v[0] is not None:
            record['owner'] = v[0]
        if v[1] is not None:
            record['group'] = v[1]
        if v[2] is not None:
            record['creation time'] = v[2]
        if v[3] is not None:
            record['modified time'] = v[3]
        if v[4] is not None:
            record['arguments'] = v[4]   
            try:
                if v[5] is not None:
                    record['arguments2'] = v[5]
                if v[6] is not None:
                    record['arguments3'] = v[6]
                if v[7] is not None:
                    record['arguments4'] = v[7]
            except Exception:
                print("Skipping unexisting key for: ", k)
        
        _output.write_record(record)

    _output.flush_record()

if __name__ == "__main__":
    print("This is an AutoMacTC module, and is not meant to be run stand-alone.")
    print("Exiting.")
    sys.exit(0)
else:
    for agent in all_agents:
        if os.path.exists(agent):

            for dirpath, dirnames, filenames in os.walk(agent, topdown=True):

		        # exclude directories and files, must use topdown=True
                file_count = 0
                filepaths = []
                filenames[:] = list(filter(lambda x: _is_valid_file(x), filenames))

                # Convert filenames to full paths
                full_path_fnames = map(lambda fn: os.path.join(agent, fn), filenames)
                filepaths.extend(list(full_path_fnames))
                file_count += len(filenames)

                # get the user and group associated to the plist and add it to the dict
                for f in filepaths:
                    group_user(f)

                    # Look for: RunAtLoad, ProgramArguments, Program, Sockets
                    if sys.version_info[0] < 3:
                        # TODO
                        user_plist = plistlib.readPlist(os.path.join(inputdir, str(user_list + user_output[i])))
                    else:
                        find_keyes(f)

        else:
            print('Skipping as it doesnt exist: ', agent)
            
    module()