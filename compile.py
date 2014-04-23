#!/usr/bin/env python
# compile.py
# GusE 2014.04.20 V0.1
"""
Utility script that compresses the virtual files into the production script
"""
__version__ = "1.0"

import getopt
import sys
import os
import subprocess
import traceback
import logging
import logging.handlers
import tempfile
import argparse

__app__ = os.path.basename(__file__)
__author__ = "Gus E"
__copyright__ = "Copyright 2014"
__credits__ = ["Gus E"]
__license__ = "GPL"
__maintainer__ = "Gus E"
__email__ = "gesquive@gmail"
__status__ = "Beta"

#--------------------------------------
# Configurable Constants
SCRIPT = 'project-create.py'
# SCRIPT = 'tmp'
DICT_NAME = 'FILES'
SCRIPT_SECTION = 'TEMPLATE FILES DEFS'

verbose = False
debug = False

def main():
    global verbose, debug

    parser = argparse.ArgumentParser(add_help=False,
        description="Utility script that compresses gitignore files into the production script.",
        epilog="%(__app__)s v%(__version__)s\n" % globals())

    group = parser.add_argument_group("Options")
    group.add_argument("-h", "--help", action="help",
        help="Show this help message and exit.")
    group.add_argument("-v", "--verbose", action="store_true", dest="verbose",
        help="Writes all messages to console.")
    group.add_argument("-D", "--debug", action="store_true", dest="debug",
        help=argparse.SUPPRESS)
    group.add_argument("-V", "--version", action="version",
                    version="%(__app__)s v%(__version__)s" % globals())

    args = parser.parse_args()
    verbose = args.verbose
    debug = args.debug

    dict_name = DICT_NAME
    section_name = SCRIPT_SECTION

    import glob
    import re
    try:
        # Here is where the magic happens
        script_file = open(SCRIPT, 'r')
        script = script_file.read()
        script_file.close()

        for filename in glob.glob("templates/*"):
            name = os.path.basename(filename)
            c_file = open(filename, 'r')
            contents = c_file.read()
            contents = contents.encode('base64').replace('\n', '')

            repl = '%(dict_name)s[\'%(name)s\'] = \'%(contents)s\'' % locals()
            line_regex = re.compile(r"%s\['%s'\].*$" % (DICT_NAME, re.escape(name)), re.MULTILINE)
            # print line_regex.search(script)
            (script, num_subs) = line_regex.subn(repl, script)
            if not num_subs: #Then an entry for the Dictionary doesn't exist
                # Attempt to add in the correct section
                sect_regex = re.compile(r"## %(section_name)s(?P<code>.*)\n"
                    "## %(section_name)s END" % locals(), re.MULTILINE|re.DOTALL)
                sect_repl = "## %(section_name)s\g<code>%(repl)s\n\n## %(section_name)s END" \
                    % locals()
                # print sect_regex.search(script)
                (script, num_subs) = sect_regex.subn(sect_repl, script)
                if not num_subs: # Then we can't find the correct section to insert
                    # Just append to the end of the file
                    script += repl + '\n'

        script_file = open(SCRIPT, 'w')
        script_file.seek(0)
        script_file.truncate()
        script_file.write(script)
        script_file.close()

    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception, e:
        print traceback.format_exc()


if __name__ == '__main__':
    main()
