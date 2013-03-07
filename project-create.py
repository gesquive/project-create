#!/usr/bin/env python
# project-create.py
# GusE 2013.01.25 V0.1
"""
Generate new barebones projects
"""

import getopt
import sys
import os
import subprocess
import traceback

__app__ = os.path.basename(__file__)
__author__ = "Gus E"
__copyright__ = "Copyright 2013"
__credits__ = ["Gus E"]
__license__ = "GPL"
__version__ = "1.0.5"
__maintainer__ = "Gus E"
__email__ = ""
__status__ = "Production"

info_file_path = 'https://raw.github.com/gesquive/project-create/master/project-create.info'

#--------------------------------------
# Configurable Constants
AUTHOR_NAME_FULL = "Gus E"
AUTHOR_NAME_SHORT = "GusE"
# I'm just obfuscating my email a little bit to protect against spam bots
# Run "python -c "import re; print "email@address.com".encode('base64')" to get a obfuscated value
AUTHOR_EMAIL = "Z2VzcXVpdmVAZ21haWwuY28="
if not "@" in AUTHOR_EMAIL:
    __email__ = AUTHOR_EMAIL.decode("base64")
    AUTHOR_EMAIL = __email__

FILES = {}

verbose = False
debug = False

def usage():
    usage = \
"""Usage: %s [options] project_name
    Generates a new project
Options and arguments:
  -l --lang <language>              What type of project to generate. See
                                        language list below.
                                        (default: python)
  -d --dir <dir_path>               The path to create the project in.
                                        (default: './project_name')
  -s --desc <description>           The description of the project.
  -o --overwrite                    Force an overwrite of an existing project.
  -u --update                       Checks server for an update, replaces
                                        the current version if there is a
                                        newer version available.
  -h --help                         Prints this message.
  -v --verbose                      Writes all messages to console.

  -- Languages ---------------------------------------------------------------
  Python script                     python, py
  C source                          c
  C++ source                        cpp, cplusplus, c++
  Shell script                      sh, shell

    v%s
""" % (__app__, __version__)

    print usage


def main():
    global verbose, debug

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvul:d:s:o", \
        ["help", "verbose", "update", "lang=", "dir=", "desc=", "overwrite"])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)

    verbose = False
    debug = False

    lang = 'python'
    dir = None
    project_name = None
    description = None
    overwrite = False

    for o, a in opts:
        if o in ("-h", "--help"):
            # Print out help and exit
            usage()
            sys.exit()
        elif o in ("-dd", "--debug"):
            debug = True
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-u", "--update"):
            update(info_file_path)
            sys.exit(0)
        elif o in ("-l", "--lang"):
            a = a.lower()
            if a in ("python", "py"):
                lang = "python"
            elif a in ("c"):
                lang = "c"
            elif a in ("cpp", "cplusplus", "c++"):
                lang = "c++"
            elif a in ("sh", "shell"):
                lang = "shell"
        elif o in ("-d", "--dir"):
            dir = a
        elif o in ("-s", "--desc"):
            description = a
        elif o in ("-o", "--overwrite"):
            overwrite = True

    # Save filter
    if len(args) == 1:
        project_name = args[0]
        if not dir:
            dir = os.path.join('.', project_name)
        if not description:
            description = "This is a generic %(lang)s project." % locals
    elif len(args) != 1:
        print "Error: No project_name spcified."
        usage()
        sys.exit(2)

    print "Checking directory '%(dir)s'" % locals()
    temp_dir = None
    try:
        temp_dir = check_dir(dir, overwrite)
    except Exception, e:
        print e
    except KeyboardInterrupt:
        print ''
        sys.exit()
    if not temp_dir:
        sys.exit(2)
    else:
        dir = temp_dir

    try:
        if lang == "python":
            sys.stdout.write("Generating a default python project...".ljust(75))
            sys.stdout.flush()
            generate_python(project_name, dir, description)
            print "Done!"
        elif lang == "c++":
            sys.stdout.write("Generating a default C++ project...".ljust(75))
            sys.stdout.flush()
            generate_cplusplus(project_name, dir, description)
            print "Done!"
        elif lang == "shell":
            sys.stdout.write("Generating a default shell project...".ljust(75))
            sys.stdout.flush()
            generate_shell(project_name, dir, description)
            print "Done!"

    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception, e:
        print traceback.format_exc()


def check_dir(dir_path, overwrite=False):
    """
    Will check for the directory and create it if needed.
    Returns the name of the path determined
    This method will just throw any os errors encountered.
    """
    import shutil
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    else:
        if not overwrite:
            print "Directory '%s' exists!" % os.path.basename(os.path.abspath(dir_path))
            prompt = "Overwrite previous project files? [y/n]: "
            overwrite = raw_input(prompt).lower().startswith('y')
        if not overwrite:
            raise OSError(2, "Project already exists", dir_path)
    if not os.path.isdir(dir_path):
        raise OSError(2, 'Path is already a file', dir_path)
    return os.path.abspath(dir_path)


def generate_python(project_name, project_path, project_description):
    from datetime import date
    import stat
    today = date.today()
    date_str = today.strftime("%Y.%m.%d")
    date_year = today.strftime("%Y")

    author_name_full = AUTHOR_NAME_FULL
    author_name_short = AUTHOR_NAME_SHORT
    author_email = AUTHOR_EMAIL

    src = FILES["python.py"].decode("base64")
    try:
        src = src % locals()
    except KeyError, e:
        print "ERROR: The key %s found in '%s' was not assigned." % (str(e), "python.py")

    src_path = os.path.join(project_path, project_name + ".py")
    src_file = open(src_path, 'w')
    src_file.write(src)
    src_file.flush()
    src_file.close()

    os.chmod(src_path, 0755)


def generate_shell(project_name, project_path, project_description):
    from datetime import date
    import stat
    today = date.today()
    date_str = today.strftime("%Y.%m.%d")

    author_name_short = AUTHOR_NAME_SHORT

    src = FILES["shell.sh"].decode("base64")
    try:
        src = src % locals()
    except KeyError, e:
        print "ERROR: The key %s found in '%s' was not assigned." % (str(e), "shell.sh")

    src_path = os.path.join(project_path, project_name + ".sh")
    src_file = open(src_path, 'w')
    src_file.write(src)
    src_file.flush()
    src_file.close()

    os.chmod(src_path, 0755)


def generate_cplusplus(project_name, project_path, project_description):
    from datetime import date
    import stat
    today = date.today()
    date_str = today.strftime("%Y.%m.%d")
    date_year = today.strftime("%Y")

    author_name_full = AUTHOR_NAME_FULL
    author_name_short = AUTHOR_NAME_SHORT
    author_email = "<" + AUTHOR_EMAIL + ">"

    makefile = FILES["cpp_make.mk"].decode("base64")
    try:
        makefile = makefile % locals()
    except KeyError, e:
        print "ERROR: The key %s found in '%s' was not assigned." % (str(e), "cpp_make.mk")

    src = FILES["cpp_main.cpp"].decode("base64")
    try:
        src = src % locals()
    except KeyError, e:
        print "ERROR: The key %s found in '%s' was not assigned." % (str(e), "cpp_main.cpp")

    src_path = os.path.join(project_path, "main.cpp")
    src_file = open(src_path, 'w')
    src_file.write(src)
    src_file.flush()
    src_file.close()
    make_path = os.path.join(project_path, "makefile")
    make_file = open(make_path, 'w')
    make_file.write(makefile)
    make_file.flush()
    make_file.close()


def update(info_file_path, force_update=False):
    """
    Attempts to download the update url in order to find if an update is needed.
    If an update is needed, the current script is backed up and the update is
    saved in its place.
    """
    import urllib
    import re
    from subprocess import call
    def compare_versions(vA, vB):
        """
        Compares two version number strings
        @param vA: first version string to compare
        @param vB: second version string to compare
        @author <a href="http_stream://sebthom.de/136-comparing-version-numbers-in-jython-pytho/">Sebastian Thomschke</a>
        @return negative if vA < vB, zero if vA == vB, positive if vA > vB.
        """
        if vA == vB: return 0

        def num(s):
            if s.isdigit(): return int(s)
            return s

        seqA = map(num, re.findall('\d+|\w+', vA.replace('-SNAPSHOT', '')))
        seqB = map(num, re.findall('\d+|\w+', vB.replace('-SNAPSHOT', '')))

        # this is to ensure that 1.0 == 1.0.0 in cmp(..)
        lenA, lenB = len(seqA), len(seqB)
        for i in range(lenA, lenB): seqA += (0,)
        for i in range(lenB, lenA): seqB += (0,)

        rc = cmp(seqA, seqB)

        if rc == 0:
            if vA.endswith('-SNAPSHOT'): return -1
            if vB.endswith('-SNAPSHOT'): return 1
        return rc

    # dl the info file and parse it for version and dl path
    try:
        http_stream = urllib.urlopen(info_file_path)
        update_file = http_stream.read()
        http_stream.close()
    except IOError, (errno, strerror):
        print "Unable to retrieve version data"
        print "Error %s: %s" % (errno, strerror)
        return

    match_regex = re.search(r'version: (\S+)', update_file)
    if not match_regex:
        print "No version info could be found"
        return
    update_version  =  match_regex.group(1)
    match_regex = re.search(r'from: (\S+)', update_file)
    if not match_regex:
        print "No update location was specified"
        return
    dl_url = match_regex.group(1)

    if not update_version:
        print "Unable to parse version data"
        return

    if force_update:
        print "Forcing update, downloading version %s..." \
            % update_version
    else:
        cmp_result = compare_versions(__version__, update_version)
        if cmp_result < 0:
            print "Newer version %s available, downloading..." % update_version
        elif cmp_result > 0:
            print "Local version %s newer then available %s, not updating." \
                % (__version__, update_version)
            return
        else:
            print "You already have the latest version."
            return

    # dl, backup, and save the updated script
    app_path = os.path.realpath(sys.argv[0])

    if not os.access(app_path, os.W_OK):
        print "Cannot update --  unable to write to %s" % app_path

    dl_path = app_path + ".new"
    backup_path = app_path + ".old"
    try:
        dl_file = open(dl_path, 'w')
        http_stream = urllib.urlopen(dl_url)
        dl_file.write(http_stream.read())
        http_stream.close()
        dl_file.close()
    except IOError, (errno, strerror):
        print "Download failed"
        print "Error %s: %s" % (errno, strerror)
        return

    try:
        os.rename(app_path, backup_path)
    except OSError, (errno, strerror):
        print "Unable to rename %s to %s: (%d) %s" \
            % (app_path, backup_path, errno, strerror)
        return

    try:
        os.rename(dl_path, app_path)
    except OSError, (errno, strerror):
        print "Unable to rename %s to %s: (%d) %s" \
            % (dl_path, app_path, errno, strerror)
        return

    os.chmod(app_path, 0755)

    print "New version installed as %s" % app_path
    print "(previous version backed up to %s)" % (backup_path)
    return


FILES['cpp_main.cpp']='''LyoKICogJShwcm9qZWN0X25hbWUpcwogKiBDb3B5cmlnaHQgqSAlKGF1dGhvcl9uYW1lX2Z1bGwpcyAlKGRhdGVfeWVhcilzICUoYXV0aG9yX2VtYWlsKXMKICoKICogJShwcm9qZWN0X25hbWUpcyBpcyBmcmVlIHNvZnR3YXJlOiB5b3UgY2FuIHJlZGlzdHJpYnV0ZSBpdCBhbmQvb3IgbW9kaWZ5IGl0CiAqIHVuZGVyIHRoZSB0ZXJtcyBvZiB0aGUgR05VIEdlbmVyYWwgUHVibGljIExpY2Vuc2UgYXMgcHVibGlzaGVkIGJ5IHRoZQogKiBGcmVlIFNvZnR3YXJlIEZvdW5kYXRpb24sIGVpdGhlciB2ZXJzaW9uIDMgb2YgdGhlIExpY2Vuc2UsIG9yCiAqIChhdCB5b3VyIG9wdGlvbikgYW55IGxhdGVyIHZlcnNpb24uCiAqCiAqICUocHJvamVjdF9uYW1lKXMgaXMgZGlzdHJpYnV0ZWQgaW4gdGhlIGhvcGUgdGhhdCBpdCB3aWxsIGJlIHVzZWZ1bCwgYnV0CiAqIFdJVEhPVVQgQU5ZIFdBUlJBTlRZOyB3aXRob3V0IGV2ZW4gdGhlIGltcGxpZWQgd2FycmFudHkgb2YKICogTUVSQ0hBTlRBQklMSVRZIG9yIEZJVE5FU1MgRk9SIEEgUEFSVElDVUxBUiBQVVJQT1NFLgogKiBTZWUgdGhlIEdOVSBHZW5lcmFsIFB1YmxpYyBMaWNlbnNlIGZvciBtb3JlIGRldGFpbHMuCiAqCiAqIFlvdSBzaG91bGQgaGF2ZSByZWNlaXZlZCBhIGNvcHkgb2YgdGhlIEdOVSBHZW5lcmFsIFB1YmxpYyBMaWNlbnNlIGFsb25nCiAqIHdpdGggdGhpcyBwcm9ncmFtLiAgSWYgbm90LCBzZWUgPGh0dHA6Ly93d3cuZ251Lm9yZy9saWNlbnNlcy8+LgogKi8KCiNpbmNsdWRlIDxzdGRpby5oPgojaW5jbHVkZSA8c3RkbGliLmg+CiNpbmNsdWRlIDxzdHJpbmcuaD4KI2luY2x1ZGUgPHVuaXN0ZC5oPgojaW5jbHVkZSA8Z2V0b3B0Lmg+CiNpbmNsdWRlIDxzaWduYWwuaD4KI2luY2x1ZGUgPGNjdHlwZT4KCiNkZWZpbmUgQVVUSE9SICIlKGF1dGhvcl9uYW1lX2Z1bGwpcyAlKGF1dGhvcl9lbWFpbClzIgojZGVmaW5lIFZFUlNJT04gIjAuMSIKCmNvbnN0IGNoYXIqIGFwcF9uYW1lOwoKaW5saW5lIHZvaWQgUHJpbnRVc2FnZSgpIHsKICAgIHByaW50ZigKIlVzYWdlOiAlJXMgW29wdGlvbnNdIGZvcmNlZF9hcmcgb3B0aW9uYWxfYXJnXG4iCiIgICAgJShwcm9qZWN0X2Rlc2NyaXB0aW9uKXNcbiIKIk9wdGlvbnMgYW5kIGFyZ3VtZW50czpcbiIKIiAgZm9yY2VkX2FyZyAgICAgICAgICAgICAgICAgICAgICBBIGZvcmNlZCBhcmd1bWVudFxuIgoiICBvcHRpb25hbF9hcmcgICAgICAgICAgICAgICAgICAgIEFuIG9wdGlvbiBhcmd1bWVudFxuIgoiICAtcyAtLXN3aXRjaCA8dmFsdWU+ICAgICAgICAgICAgIEEgc3dpdGNoIHdpdGggYSB2YWx1ZVxuIgoiICAtaCAtLWhlbHAgICAgICAgICAgICAgICAgICAgICAgIFByaW50cyB0aGlzIG1lc3NhZ2UuXG4iCiIgIC12IC0tdmVyYm9zZSAgICAgICAgICAgICAgICAgICAgV3JpdGVzIGFsbCBtZXNzYWdlcyB0byBjb25zb2xlLlxuXG4iCiIgICAgdiUlc1xuIiwgYXBwX25hbWUsIFZFUlNJT04pOwp9Cgp2b2lkIFNpZ0hhbmRsZXIoaW50IHNpZykgewogICAgcHJpbnRmKCJcbkdvb2RieWUuXG4iKTsKICAgIGV4aXQoMCk7Cn0KCmludCBtYWluKGludCBhcmdjLCBjaGFyKiBhcmd2W10pIHsKICAgIHNpZ25hbChTSUdJTlQsICZTaWdIYW5kbGVyKTsKCiAgICBhcHBfbmFtZSA9IGJhc2VuYW1lKGFyZ3ZbMF0pOwoKICAgIGJvb2wgdmVyYm9zZSA9IGZhbHNlOwogICAgY2hhciAqc3dpdGNoX3ZhbHVlID0gTlVMTDsKCiAgICBpbnQgYzsKICAgIGludCBvcHRpb25faW5kZXggPSAwOwoKICAgIHN0YXRpYyBzdHJ1Y3Qgb3B0aW9uIGxvbmdfb3B0aW9uc1tdID0gewogICAgICAgIC8ve2NvbnN0IGNoYXIqIG5hbWUsIGludCBoYXNfYXJnLCBpbnQqIGZsYWcsIGludCB2YWwgfSwKICAgICAgICB7ImhlbHAiLCAwLCAwLCAnaCd9LAogICAgICAgIHsidmVyYm9zZSIsIDAsIDAsICd2J30sCiAgICAgICAgeyJzd2l0Y2giLCAxLCAwLCAncyd9LAogICAgICAgIHswLCAwLCAwLCAwfQogICAgfTsKCiAgICBkbyB7CiAgICAgICAgYyA9IGdldG9wdF9sb25nKGFyZ2MsIGFyZ3YsICJodnM6IiwgbG9uZ19vcHRpb25zLCAmb3B0aW9uX2luZGV4KTsKICAgICAgICBzd2l0Y2ggKGMpIHsKICAgICAgICBjYXNlICd2JzoKICAgICAgICAgICAgdmVyYm9zZSA9IHRydWU7CiAgICAgICAgICAgIGJyZWFrOwogICAgICAgIGNhc2UgJ2gnOgogICAgICAgICAgICBQcmludFVzYWdlKCk7CiAgICAgICAgICAgIGV4aXQoMCk7CiAgICAgICAgICAgIGJyZWFrOwogICAgICAgIGNhc2UgJ3MnOgogICAgICAgICAgICAvLyBWYWxpZGF0ZSB0aGUgc3dpdGNoIHZhbHVlIGhlcmUKICAgICAgICAgICAgc3dpdGNoX3ZhbHVlID0gbmV3IGNoYXJbc3RybGVuKG9wdGFyZykrMV07CiAgICAgICAgICAgIHN0cmNweShzd2l0Y2hfdmFsdWUsIG9wdGFyZyk7CiAgICAgICAgICAgIGJyZWFrOwogICAgICAgIGNhc2UgJzonOgogICAgICAgICAgICBpZiAob3B0b3B0KSB7CiAgICAgICAgICAgICAgICBwcmludGYoIk1pc3NpbmcgYW4gYXJndW1lbnQgZm9yIGZsYWcgJy0lJWMnXG4iLCBvcHRvcHQpOwogICAgICAgICAgICB9IGVsc2UgewogICAgICAgICAgICAgICAgcHJpbnRmKCJNaXNzaW5nIGFuIGFyZ3VtZW50IGZvciBmbGFnICBcIi0tJSVzXCJcbiIsCiAgICAgICAgICAgICAgICAgICAgICAgYXJndltvcHRpbmQtMV0pOwogICAgICAgICAgICB9CiAgICAgICAgICAgIFByaW50VXNhZ2UoKTsKICAgICAgICAgICAgZXhpdCgyKTsKICAgICAgICAgICAgYnJlYWs7CiAgICAgICAgY2FzZSAnPyc6CiAgICAgICAgICAgIGlmIChvcHRvcHQpIHsKICAgICAgICAgICAgICAgIHByaW50ZigiVW5yZWNvZ25pemVkIGZsYWcgJy0lJWMnXG4iLCBvcHRvcHQpOwogICAgICAgICAgICB9IGVsc2UgewogICAgICAgICAgICAgICAgcHJpbnRmKCJVbnJlY29nbml6ZWQgZmxhZyBcIi0tJSVzXCJcbiIsIGFyZ3Zbb3B0aW5kLTFdKTsKICAgICAgICAgICAgfQogICAgICAgICAgICBQcmludFVzYWdlKCk7CiAgICAgICAgICAgIGV4aXQoMik7CiAgICAgICAgICAgIGJyZWFrOwogICAgICAgIGNhc2UgLTE6CiAgICAgICAgICAgIGJyZWFrOwogICAgICAgIGRlZmF1bHQ6CiAgICAgICAgICAgIHByaW50ZigiLS0lJWQgbm90IGNvbXBsZXRlZFxuIiwgYyk7CiAgICAgICAgICAgIGJyZWFrOwogICAgICAgIH0KICAgIH0gd2hpbGUgKGMgIT0gLTEpOwoKICAgIGNoYXIgKmZvcmNlZF9hcmcgPSBOVUxMOwogICAgY2hhciAqb3B0aW9uYWxfYXJnID0gTlVMTDsKCiAgICBpbnQgbm9ub3B0YyA9IGFyZ2MgLSBvcHRpbmQ7CiAgICBpZiAobm9ub3B0YyA+PSAxICYmIG5vbm9wdGMgPD0gMikgewogICAgICAgIC8vIFZhbGlkYXRlIHRoZSBmb3JjZWQgYXJndW1lbnQgaGVyZQogICAgICAgIGZvcmNlZF9hcmcgPSBuZXcgY2hhcltzdHJsZW4oYXJndltvcHRpbmRdKSsxXTsKICAgICAgICBzdHJjcHkoZm9yY2VkX2FyZywgYXJndltvcHRpbmRdKTsKCiAgICAgICAgaWYgKCsrb3B0aW5kIDwgYXJnYykgewogICAgICAgICAgICAvLyBWYWxpZGF0ZSB0aGUgb3B0aW9uYWwgYXJndW1lbnQgaGVyZQogICAgICAgICAgICBvcHRpb25hbF9hcmcgPSBuZXcgY2hhcltzdHJsZW4oYXJndltvcHRpbmRdKSsxXTsKICAgICAgICAgICAgc3RyY3B5KG9wdGlvbmFsX2FyZywgYXJndltvcHRpbmRdKTsKICAgICAgICB9CiAgICB9IGVsc2UgewogICAgICAgIHByaW50ZigiSW5jb3JyZWN0IG51bWJlciBvZiBhcmd1bWVudHMuXG4iKTsKICAgICAgICBQcmludFVzYWdlKCk7CiAgICAgICAgZXhpdCgyKTsKICAgIH0KCiAgICAvL1RPRE86IFJ1biBhY3R1YWwgY29kZSBoZXJlCiAgICBwcmludGYoIkhlbGxvIFdvcmxkIVxuIik7CgogICAgaWYgKHZlcmJvc2UpIHsKICAgICAgICBwcmludGYoIkVuZCBvZiBjb2RlLlxuIik7CiAgICB9CgogICAgZXhpdCgwKTsKfQo='''
FILES['cpp_make.mk']='''Q0M9Z2NjCkVYVD0uY3BwCkVYRT0lKHByb2plY3RfbmFtZSlzCkNGTEFHUz0tV2FsbCAtZzAgLU8zCklOQ0xVREVTPQpMRkxBR1M9CkxJQlM9LWxzdGRjKysKClNSQ1M9JChzdHJpcCAkKHNoZWxsIGZpbmQgKiQoRVhUKSAtdHlwZSBmKSkKT0JKUz0kKFNSQ1M6JChFWFQpPS5vKQoKLlBIT05ZOiBkZXBlbmQgY2xlYW4gaW5zdGFsbAoKYWxsOiAkKFNSQ1MpICQoRVhFKQoJQGVjaG8gJChFWEUpIGhhcyBiZWVuIGNvbXBpbGVkCgpkZWJ1ZzogQ0ZMQUdTKz0gLURERUJVRyAtZzMgLU8wCmRlYnVnOgoJQGVjaG8gIkNvbXBpbGluZyBEZWJ1ZyBWZXJzaW9uLi4uIgpkZWJ1ZzogYWxsCgokKEVYRSk6ICQoT0JKUykKCUBlY2hvIENvbXBpbGluZyBleGVjdXRhYmxlLi4uCgkkKENDKSAkKE9CSlMpICQoTEZMQUdTKSAkKExJQlMpIC1vICQoRVhFKQoKJChFWFQpLm86CgkkKENDKSAkKENGTEFHUykgJChJTkNMVURFUykgLWMgJDwgLW8gJEAKCmNsZWFuOgoJcm0gLXJmICoubyAqfiAkKEVYRSkKCmluc3RhbGw6CgljcCAkKEVYRSkgL3Vzci9sb2NhbC9iaW4KCmRlcGVuZDogZGVwCgpkZXA6ICQoU1JDUykKCW1ha2VkZXBlbmQgJChJTkNMVURFUykgJF4KCiMgRE8gTk9UIERFTEVURSBUSElTIExJTkUgLS0gbWFrZSBkZXBlbmQgbmVlZHMgaXQK'''
FILES['python.py']='''IyEvdXNyL2Jpbi9lbnYgcHl0aG9uCiMgJShwcm9qZWN0X25hbWUpcy5weQojICUoYXV0aG9yX25hbWVfc2hvcnQpcyAlKGRhdGVfc3RyKXMgVjAuMQoiIiIKJShwcm9qZWN0X2Rlc2NyaXB0aW9uKXMKIiIiCgppbXBvcnQgZ2V0b3B0CmltcG9ydCBzeXMKaW1wb3J0IG9zCmltcG9ydCBzdWJwcm9jZXNzCmltcG9ydCB0cmFjZWJhY2sKaW1wb3J0IGxvZ2dpbmcKaW1wb3J0IGxvZ2dpbmcuaGFuZGxlcnMKCl9fYXBwX18gPSBvcy5wYXRoLmJhc2VuYW1lKF9fZmlsZV9fKQpfX2F1dGhvcl9fID0gIiUoYXV0aG9yX25hbWVfZnVsbClzIgpfX2NvcHlyaWdodF9fID0gIkNvcHlyaWdodCAlKGRhdGVfeWVhcilzIgpfX2NyZWRpdHNfXyA9IFsiJShhdXRob3JfbmFtZV9mdWxsKXMiXQpfX2xpY2Vuc2VfXyA9ICJHUEwiCl9fdmVyc2lvbl9fID0gIjAuMSIKX19tYWludGFpbmVyX18gPSAiJShhdXRob3JfbmFtZV9mdWxsKXMiCl9fZW1haWxfXyA9ICIlKGF1dGhvcl9lbWFpbClzIgpfX3N0YXR1c19fID0gIkJldGEiCgoKIy0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiMgQ29uZmlndXJhYmxlIENvbnN0YW50cwpMT0dfRklMRSA9ICcvdmFyL2xvZy8nICsgb3MucGF0aC5zcGxpdGV4dChfX2FwcF9fKVswXSArICcubG9nJwpMT0dfU0laRSA9IDEwMjQqMTAyNCoyMDAKCnZlcmJvc2UgPSBGYWxzZQpkZWJ1ZyA9IEZhbHNlCgpsb2dnZXIgPSBsb2dnaW5nLmdldExvZ2dlcihfX2FwcF9fKQoKZGVmIHVzYWdlKCk6CiAgICB1c2FnZSA9IFwKIiIiVXNhZ2U6ICUlcyBbb3B0aW9uc10gZm9yY2VkX2FyZwogICAgJShwcm9qZWN0X2Rlc2NyaXB0aW9uKXMKT3B0aW9ucyBhbmQgYXJndW1lbnRzOgogIC1oIC0taGVscCAgICAgICAgICAgICAgICAgICAgICAgICBQcmludHMgdGhpcyBtZXNzYWdlLgogIC12IC0tdmVyYm9zZSAgICAgICAgICAgICAgICAgICAgICBXcml0ZXMgYWxsIG1lc3NhZ2VzIHRvIGNvbnNvbGUuCgogICAgdiUlcwoiIiIgJSUgKF9fYXBwX18sIF9fdmVyc2lvbl9fKQoKICAgIHByaW50IHVzYWdlCgoKZGVmIG1haW4oKToKICAgIGdsb2JhbCB2ZXJib3NlLCBkZWJ1ZwoKICAgIHRyeToKICAgICAgICBvcHRzLCBhcmdzID0gZ2V0b3B0LmdldG9wdChzeXMuYXJndlsxOl0sICJodiIsIFwKICAgICAgICBbImhlbHAiLCAidmVyYm9zZSIsICJkZWJ1ZyJdKQogICAgZXhjZXB0IGdldG9wdC5HZXRvcHRFcnJvciwgZXJyOgogICAgICAgIHByaW50IHN0cihlcnIpCiAgICAgICAgc3lzLmV4aXQoMikKCiAgICB2ZXJib3NlID0gRmFsc2UKICAgIGRlYnVnID0gRmFsc2UKICAgIGZvcmNlZF9hcmcgPSBOb25lCgogICAgIyBTYXZlIGZvcmNlZCBhcmcKICAgIGlmIGxlbihhcmdzKSA+IDA6CiAgICAgICAgZm9yY2VkX2FyZyA9IGFyZ3NbMF0KICAgIGVsaWYgbGVuKGFyZ3MpID4gMToKICAgICAgICB1c2FnZSgpCiAgICAgICAgc3lzLmV4aXQoMikKCiAgICBmb3IgbywgYSBpbiBvcHRzOgogICAgICAgIGlmIG8gaW4gKCItaCIsICItLWhlbHAiKToKICAgICAgICAgICAgIyBQcmludCBvdXQgaGVscCBhbmQgZXhpdAogICAgICAgICAgICB1c2FnZSgpCiAgICAgICAgICAgIHN5cy5leGl0KCkKICAgICAgICBlbGlmIG8gaW4gKCItZGQiLCAiLS1kZWJ1ZyIpOgogICAgICAgICAgICBkZWJ1ZyA9IFRydWUKICAgICAgICBlbGlmIG8gaW4gKCItdiIsICItLXZlcmJvc2UiKToKICAgICAgICAgICAgdmVyYm9zZSA9IFRydWUKCiAgICBsb2dfZmlsZSA9IExPR19GSUxFCiAgICBpZiBub3Qgb3MuYWNjZXNzKGxvZ19maWxlLCBvcy5XX09LKToKICAgICAgICBwcmludCAiQ2Fubm90IHdyaXRlIHRvICclJShsb2dfZmlsZSlzJy5cbkV4aXRpbmcuIiAlJSBsb2NhbHMoKQogICAgICAgIHN5cy5leGl0KDIpCiAgICBoYW5kbGUgPSBsb2dnaW5nLmhhbmRsZXJzLlJvdGF0aW5nRmlsZUhhbmRsZXIobG9nX2ZpbGUsCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgbWF4Qnl0ZXM9TE9HX1NJWkUsIGJhY2t1cENvdW50PTkpCiAgICBmb3JtYXQgPSBsb2dnaW5nLkZvcm1hdHRlcignJSUoYXNjdGltZSlzLCUlKGxldmVsbmFtZSlzLCUlKHRocmVhZClkLCUlKG1lc3NhZ2UpcycpCiAgICBoYW5kbGUuc2V0Rm9ybWF0dGVyKGZvcm1hdCkKICAgIGxvZ2dlci5hZGRIYW5kbGVyKGhhbmRsZSkKICAgIGxvZ2dlci5zZXRMZXZlbChsb2dnaW5nLkRFQlVHKQoKICAgIHRyeToKICAgICAgICAjIERPIFNPTUVUSElORwogICAgICAgIGRvX3NvbWV0aGluZygpCiAgICBleGNlcHQgKEtleWJvYXJkSW50ZXJydXB0LCBTeXN0ZW1FeGl0KToKICAgICAgICBwYXNzCiAgICBleGNlcHQgRXhjZXB0aW9uLCBlOgogICAgICAgIHByaW50IHRyYWNlYmFjay5mb3JtYXRfZXhjKCkKCgpkZWYgZG9fc29tZXRoaW5nKCk6CiAgICBwcmludCAiSGVsbG8gV29ybGQhIgoKaWYgX19uYW1lX18gPT0gJ19fbWFpbl9fJzoKICAgIG1haW4oKQo='''
FILES['shell.sh']='''IyEvYmluL2Jhc2gKIyAlKHByb2plY3RfbmFtZSlzLnNoCiMgJShhdXRob3JfbmFtZV9zaG9ydClzICUoZGF0ZV9zdHIpcyBWMC4xCiMKIyAlKHByb2plY3RfZGVzY3JpcHRpb24pcwoKZWNobyAiSGVsbG8gV29ybGQhIgo='''


if __name__ == '__main__':
    main()
