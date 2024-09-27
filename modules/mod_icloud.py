"""A module intended to find additional user accounts in the device which could have
been added for further persistence and compromise.
"""

import logging
import os
import sys
import re
from collections import OrderedDict

# IMPORT STATIC VARIABLES FROM MAIN
from __main__ import (OSVersion, archive, data_writer, forensic_mode,
                      full_prefix, inputdir, no_tarball, outputdir, quiet,
                      startTime)

# IMPORT FUNCTIONS FROM COMMON.FUNCTIONS
from .common.dateutil import parser
from .common.functions import cocoa_time, multiglob, read_bplist, stats2, get_db_column_headers

_modName = __name__.split('_')[-1]
_modVers = '1.0.0'
log = logging.getLogger(_modName)

def module():   

    account_list = '~/Library/Application Support/iCloud/Accounts/'
    regex = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")

    _headers = ['account mail']
    _output = data_writer(_modName, _headers)

    if os.path.exists(os.path.expanduser(account_list)):
        for dirpath, dirnames, filenames in os.walk(os.path.expanduser(account_list), topdown=True):
            # if we find mail addresses, list them as associated iCloud accounts
            for file in filenames:
                if re.fullmatch(regex, file):
                    record = OrderedDict((h, '') for h in _headers)

                    record['account mail'] = file

                    _output.write_record(record)

    else:
        print("No associated email accounts for iCloud")

    _output.flush_record()

if __name__ == "__main__":
    print("This is an AutoMacTC module, and is not meant to be run stand-alone.")
    print("Exiting.")
    sys.exit(0)
else:
    module()