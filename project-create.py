#!/usr/bin/env python
# project-create.py
# GusE 2013.01.25 V0.1
"""
Generate new barebones projects
"""
__version__ = "1.1.2"

import getopt
import sys
import os
import subprocess
import traceback
import ConfigParser

__app__ = os.path.basename(__file__)
__author__ = "Gus E"
__copyright__ = "Copyright 2013"
__credits__ = ["Gus E"]
__license__ = "GPL"
__maintainer__ = "Gus E"
__email__ = "gesquive@gmail"
__status__ = "Production"


#--------------------------------------
# Configurable Constants
script_www = 'https://github.com/gesquive/project-create'
script_url = 'https://raw.github.com/gesquive/project-create/master/project-create.py'

FILES = {}

config_author_name_full = "Default Author"
config_author_name_short = "Default"
config_author_email = "default@email.com"

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
    global config_author_name_full, config_author_name_short, config_author_email

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

    config_path = get_config_path()
    if (config_path):
        config = ConfigParser.ConfigParser()
        config.read(config_path)

        config_author_name_full = config.get("Values", "Full_Name").strip()
        config_author_name_short = config.get("Values", "Short_Name").strip()
        config_author_email = config.get("Values", "Email").strip()
    else:
        config_path =  os.path.join(os.path.expanduser('~'),
            '.config', "project-create", "project-create.conf")
        print "No config file exists, please fill in the following values."
        config_author_name_full = raw_input("Full author name: ").strip()
        config_author_name_short = raw_input("Short author name: ").strip()
        config_author_email = raw_input("Author email: ").strip()

        os.makedirs(os.path.dirname(config_path))
        config = ConfigParser.ConfigParser()
        config.add_section("Values")
        config.set("Values", 'Full_Name', config_author_name_full)
        config.set("Values", 'Short_Name', config_author_name_short)
        config.set("Values", 'Email', config_author_email)
        with open(config_path, 'wb') as configfile:
            config.write(configfile)

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
            update(script_url)
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
            description = "This is a generic %(lang)s project." % locals()
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
    global config_author_name_full, config_author_name_short, config_author_email
    from datetime import date
    import stat
    today = date.today()
    date_str = today.strftime("%Y.%m.%d")
    date_year = today.strftime("%Y")

    author_name_full = config_author_name_full
    author_name_short = config_author_name_short
    author_email = config_author_email

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
    global config_author_name_short
    from datetime import date
    import stat
    today = date.today()
    date_str = today.strftime("%Y.%m.%d")

    author_name_short = config_author_name_short

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
    global config_author_name_full, config_author_name_short, config_author_email
    from datetime import date
    import stat
    today = date.today()
    date_str = today.strftime("%Y.%m.%d")
    date_year = today.strftime("%Y")

    author_name_full = config_author_name_full
    author_name_short = config_author_name_short
    author_email = "<" + config_author_email + ">"

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


def get_config_path():
    config_path = None
    project_name = __app__.split('.')[0]
    project_name = "project-create"
    config_name = project_name+".conf"
    locations = [
    os.path.join(os.curdir, config_name),
    os.path.join(os.path.expanduser('~'), '.config', project_name, config_name),
    os.path.join('/etc', project_name, config_name),
    os.environ.get(project_name+"_CONF"),
    ]
    for path in locations:
        if path != None and os.path.exists(path) and os.path.isfile(path):
            return path
    return None


def update(dl_url, force_update=False):
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

    # dl the first 256 bytes and parse it for version number
    try:
        http_stream = urllib.urlopen(dl_url)
        update_file = http_stream.read(256)
        http_stream.close()
    except IOError, (errno, strerror):
        print "Unable to retrieve version data"
        print "Error %s: %s" % (errno, strerror)
        return

    match_regex = re.search(r'__version__ *= *"(\S+)"', update_file)
    if not match_regex:
        print "No version info could be found"
        return
    update_version = match_regex.group(1)

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
        print "Cannot update -- unable to write to %s" % app_path

    dl_path = app_path + ".new"
    backup_path = app_path + ".old"
    try:
        dl_file = open(dl_path, 'w')
        http_stream = urllib.urlopen(dl_url)
        total_size = None
        bytes_so_far = 0
        chunk_size = 8192
        try:
            total_size = int(http_stream.info().getheader('Content-Length').strip())
        except:
            # The header is improper or missing Content-Length, just download
            dl_file.write(http_stream.read())

        while total_size:
            chunk = http_stream.read(chunk_size)
            dl_file.write(chunk)
            bytes_so_far += len(chunk)

            if not chunk:
                break

            percent = float(bytes_so_far) / total_size
            percent = round(percent*100, 2)
            sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" %
                (bytes_so_far, total_size, percent))

            if bytes_so_far >= total_size:
                sys.stdout.write('\n')

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

    try:
        import shutil
        shutil.copymode(backup_path, app_path)
    except:
        os.chmod(app_path, 0755)

    print "New version installed as %s" % app_path
    print "(previous version backed up to %s)" % (backup_path)
    return


# DO NOT MODIFY THE FOLLOWING AUTO-GENERATED SECTION - CHANGES WILL BE OVERWRITTEN
## TEMPLATE FILES

FILES['cpp_main.cpp']='''LyoKICogJShwcm9qZWN0X25hbWUpcwogKiBDb3B5cmlnaHQgwqkgJShhdXRob3JfbmFtZV9mdWxsKXMgJShkYXRlX3llYXIpcyAlKGF1dGhvcl9lbWFpbClzCiAqCiAqICUocHJvamVjdF9uYW1lKXMgaXMgZnJlZSBzb2Z0d2FyZTogeW91IGNhbiByZWRpc3RyaWJ1dGUgaXQgYW5kL29yIG1vZGlmeSBpdAogKiB1bmRlciB0aGUgdGVybXMgb2YgdGhlIEdOVSBHZW5lcmFsIFB1YmxpYyBMaWNlbnNlIGFzIHB1Ymxpc2hlZCBieSB0aGUKICogRnJlZSBTb2Z0d2FyZSBGb3VuZGF0aW9uLCBlaXRoZXIgdmVyc2lvbiAzIG9mIHRoZSBMaWNlbnNlLCBvcgogKiAoYXQgeW91ciBvcHRpb24pIGFueSBsYXRlciB2ZXJzaW9uLgogKgogKiAlKHByb2plY3RfbmFtZSlzIGlzIGRpc3RyaWJ1dGVkIGluIHRoZSBob3BlIHRoYXQgaXQgd2lsbCBiZSB1c2VmdWwsIGJ1dAogKiBXSVRIT1VUIEFOWSBXQVJSQU5UWTsgd2l0aG91dCBldmVuIHRoZSBpbXBsaWVkIHdhcnJhbnR5IG9mCiAqIE1FUkNIQU5UQUJJTElUWSBvciBGSVRORVNTIEZPUiBBIFBBUlRJQ1VMQVIgUFVSUE9TRS4KICogU2VlIHRoZSBHTlUgR2VuZXJhbCBQdWJsaWMgTGljZW5zZSBmb3IgbW9yZSBkZXRhaWxzLgogKgogKiBZb3Ugc2hvdWxkIGhhdmUgcmVjZWl2ZWQgYSBjb3B5IG9mIHRoZSBHTlUgR2VuZXJhbCBQdWJsaWMgTGljZW5zZSBhbG9uZwogKiB3aXRoIHRoaXMgcHJvZ3JhbS4gIElmIG5vdCwgc2VlIDxodHRwOi8vd3d3LmdudS5vcmcvbGljZW5zZXMvPi4KICovCgojaW5jbHVkZSA8c3RkaW8uaD4KI2luY2x1ZGUgPHN0ZGxpYi5oPgojaW5jbHVkZSA8c3RyaW5nLmg+CiNpbmNsdWRlIDx1bmlzdGQuaD4KI2luY2x1ZGUgPGdldG9wdC5oPgojaW5jbHVkZSA8c2lnbmFsLmg+CiNpbmNsdWRlIDxjY3R5cGU+CgojZGVmaW5lIEFVVEhPUiAiJShhdXRob3JfbmFtZV9mdWxsKXMgJShhdXRob3JfZW1haWwpcyIKI2RlZmluZSBWRVJTSU9OICIwLjEiCgpjb25zdCBjaGFyKiBhcHBfbmFtZTsKCmlubGluZSB2b2lkIFByaW50VXNhZ2UoKSB7CiAgICBwcmludGYoCiJVc2FnZTogJSVzIFtvcHRpb25zXSBmb3JjZWRfYXJnIG9wdGlvbmFsX2FyZ1xuIgoiICAgICUocHJvamVjdF9kZXNjcmlwdGlvbilzXG4iCiJPcHRpb25zIGFuZCBhcmd1bWVudHM6XG4iCiIgIGZvcmNlZF9hcmcgICAgICAgICAgICAgICAgICAgICAgQSBmb3JjZWQgYXJndW1lbnRcbiIKIiAgb3B0aW9uYWxfYXJnICAgICAgICAgICAgICAgICAgICBBbiBvcHRpb24gYXJndW1lbnRcbiIKIiAgLXMgLS1zd2l0Y2ggPHZhbHVlPiAgICAgICAgICAgICBBIHN3aXRjaCB3aXRoIGEgdmFsdWVcbiIKIiAgLWggLS1oZWxwICAgICAgICAgICAgICAgICAgICAgICBQcmludHMgdGhpcyBtZXNzYWdlLlxuIgoiICAtdiAtLXZlcmJvc2UgICAgICAgICAgICAgICAgICAgIFdyaXRlcyBhbGwgbWVzc2FnZXMgdG8gY29uc29sZS5cblxuIgoiICAgIHYlJXNcbiIsIGFwcF9uYW1lLCBWRVJTSU9OKTsKfQoKdm9pZCBTaWdIYW5kbGVyKGludCBzaWcpIHsKICAgIHByaW50ZigiXG5Hb29kYnllLlxuIik7CiAgICBleGl0KDApOwp9CgppbnQgbWFpbihpbnQgYXJnYywgY2hhciogYXJndltdKSB7CiAgICBzaWduYWwoU0lHSU5ULCAmU2lnSGFuZGxlcik7CgogICAgYXBwX25hbWUgPSBiYXNlbmFtZShhcmd2WzBdKTsKCiAgICBib29sIHZlcmJvc2UgPSBmYWxzZTsKICAgIGNoYXIgKnN3aXRjaF92YWx1ZSA9IE5VTEw7CgogICAgaW50IGM7CiAgICBpbnQgb3B0aW9uX2luZGV4ID0gMDsKCiAgICBzdGF0aWMgc3RydWN0IG9wdGlvbiBsb25nX29wdGlvbnNbXSA9IHsKICAgICAgICAvL3tjb25zdCBjaGFyKiBuYW1lLCBpbnQgaGFzX2FyZywgaW50KiBmbGFnLCBpbnQgdmFsIH0sCiAgICAgICAgeyJoZWxwIiwgMCwgMCwgJ2gnfSwKICAgICAgICB7InZlcmJvc2UiLCAwLCAwLCAndid9LAogICAgICAgIHsic3dpdGNoIiwgMSwgMCwgJ3MnfSwKICAgICAgICB7MCwgMCwgMCwgMH0KICAgIH07CgogICAgZG8gewogICAgICAgIGMgPSBnZXRvcHRfbG9uZyhhcmdjLCBhcmd2LCAiaHZzOiIsIGxvbmdfb3B0aW9ucywgJm9wdGlvbl9pbmRleCk7CiAgICAgICAgc3dpdGNoIChjKSB7CiAgICAgICAgY2FzZSAndic6CiAgICAgICAgICAgIHZlcmJvc2UgPSB0cnVlOwogICAgICAgICAgICBicmVhazsKICAgICAgICBjYXNlICdoJzoKICAgICAgICAgICAgUHJpbnRVc2FnZSgpOwogICAgICAgICAgICBleGl0KDApOwogICAgICAgICAgICBicmVhazsKICAgICAgICBjYXNlICdzJzoKICAgICAgICAgICAgLy8gVmFsaWRhdGUgdGhlIHN3aXRjaCB2YWx1ZSBoZXJlCiAgICAgICAgICAgIHN3aXRjaF92YWx1ZSA9IG5ldyBjaGFyW3N0cmxlbihvcHRhcmcpKzFdOwogICAgICAgICAgICBzdHJjcHkoc3dpdGNoX3ZhbHVlLCBvcHRhcmcpOwogICAgICAgICAgICBicmVhazsKICAgICAgICBjYXNlICc6JzoKICAgICAgICAgICAgaWYgKG9wdG9wdCkgewogICAgICAgICAgICAgICAgcHJpbnRmKCJNaXNzaW5nIGFuIGFyZ3VtZW50IGZvciBmbGFnICctJSVjJ1xuIiwgb3B0b3B0KTsKICAgICAgICAgICAgfSBlbHNlIHsKICAgICAgICAgICAgICAgIHByaW50ZigiTWlzc2luZyBhbiBhcmd1bWVudCBmb3IgZmxhZyAgXCItLSUlc1wiXG4iLAogICAgICAgICAgICAgICAgICAgICAgIGFyZ3Zbb3B0aW5kLTFdKTsKICAgICAgICAgICAgfQogICAgICAgICAgICBQcmludFVzYWdlKCk7CiAgICAgICAgICAgIGV4aXQoMik7CiAgICAgICAgICAgIGJyZWFrOwogICAgICAgIGNhc2UgJz8nOgogICAgICAgICAgICBpZiAob3B0b3B0KSB7CiAgICAgICAgICAgICAgICBwcmludGYoIlVucmVjb2duaXplZCBmbGFnICctJSVjJ1xuIiwgb3B0b3B0KTsKICAgICAgICAgICAgfSBlbHNlIHsKICAgICAgICAgICAgICAgIHByaW50ZigiVW5yZWNvZ25pemVkIGZsYWcgXCItLSUlc1wiXG4iLCBhcmd2W29wdGluZC0xXSk7CiAgICAgICAgICAgIH0KICAgICAgICAgICAgUHJpbnRVc2FnZSgpOwogICAgICAgICAgICBleGl0KDIpOwogICAgICAgICAgICBicmVhazsKICAgICAgICBjYXNlIC0xOgogICAgICAgICAgICBicmVhazsKICAgICAgICBkZWZhdWx0OgogICAgICAgICAgICBwcmludGYoIi0tJSVkIG5vdCBjb21wbGV0ZWRcbiIsIGMpOwogICAgICAgICAgICBicmVhazsKICAgICAgICB9CiAgICB9IHdoaWxlIChjICE9IC0xKTsKCiAgICBjaGFyICpmb3JjZWRfYXJnID0gTlVMTDsKICAgIGNoYXIgKm9wdGlvbmFsX2FyZyA9IE5VTEw7CgogICAgaW50IG5vbm9wdGMgPSBhcmdjIC0gb3B0aW5kOwogICAgaWYgKG5vbm9wdGMgPj0gMSAmJiBub25vcHRjIDw9IDIpIHsKICAgICAgICAvLyBWYWxpZGF0ZSB0aGUgZm9yY2VkIGFyZ3VtZW50IGhlcmUKICAgICAgICBmb3JjZWRfYXJnID0gbmV3IGNoYXJbc3RybGVuKGFyZ3Zbb3B0aW5kXSkrMV07CiAgICAgICAgc3RyY3B5KGZvcmNlZF9hcmcsIGFyZ3Zbb3B0aW5kXSk7CgogICAgICAgIGlmICgrK29wdGluZCA8IGFyZ2MpIHsKICAgICAgICAgICAgLy8gVmFsaWRhdGUgdGhlIG9wdGlvbmFsIGFyZ3VtZW50IGhlcmUKICAgICAgICAgICAgb3B0aW9uYWxfYXJnID0gbmV3IGNoYXJbc3RybGVuKGFyZ3Zbb3B0aW5kXSkrMV07CiAgICAgICAgICAgIHN0cmNweShvcHRpb25hbF9hcmcsIGFyZ3Zbb3B0aW5kXSk7CiAgICAgICAgfQogICAgfSBlbHNlIHsKICAgICAgICBwcmludGYoIkluY29ycmVjdCBudW1iZXIgb2YgYXJndW1lbnRzLlxuIik7CiAgICAgICAgUHJpbnRVc2FnZSgpOwogICAgICAgIGV4aXQoMik7CiAgICB9CgogICAgLy9UT0RPOiBSdW4gYWN0dWFsIGNvZGUgaGVyZQogICAgcHJpbnRmKCJIZWxsbyBXb3JsZCFcbiIpOwoKICAgIGlmICh2ZXJib3NlKSB7CiAgICAgICAgcHJpbnRmKCJFbmQgb2YgY29kZS5cbiIpOwogICAgfQoKICAgIGV4aXQoMCk7Cn0K'''
FILES['cpp_make.mk']='''Q0M9Z2NjCkVYVD0uY3BwCkVYRT0lKHByb2plY3RfbmFtZSlzCkNGTEFHUz0tV2FsbCAtZzAgLU8zCklOQ0xVREVTPQpMRkxBR1M9CkxJQlM9LWxzdGRjKysKClNSQ1M9JChzdHJpcCAkKHNoZWxsIGZpbmQgKiQoRVhUKSAtdHlwZSBmKSkKT0JKUz0kKFNSQ1M6JChFWFQpPS5vKQoKLlBIT05ZOiBkZXBlbmQgY2xlYW4gaW5zdGFsbAoKYWxsOiAkKFNSQ1MpICQoRVhFKQoJQGVjaG8gJChFWEUpIGhhcyBiZWVuIGNvbXBpbGVkCgpkZWJ1ZzogQ0ZMQUdTKz0gLURERUJVRyAtZzMgLU8wCmRlYnVnOgoJQGVjaG8gIkNvbXBpbGluZyBEZWJ1ZyBWZXJzaW9uLi4uIgpkZWJ1ZzogYWxsCgokKEVYRSk6ICQoT0JKUykKCUBlY2hvIENvbXBpbGluZyBleGVjdXRhYmxlLi4uCgkkKENDKSAkKE9CSlMpICQoTEZMQUdTKSAkKExJQlMpIC1vICQoRVhFKQoKJChFWFQpLm86CgkkKENDKSAkKENGTEFHUykgJChJTkNMVURFUykgLWMgJDwgLW8gJEAKCmNsZWFuOgoJcm0gLXJmICoubyAqfiAkKEVYRSkKCmluc3RhbGw6CgljcCAkKEVYRSkgL3Vzci9sb2NhbC9iaW4KCmRlcGVuZDogZGVwCgpkZXA6ICQoU1JDUykKCW1ha2VkZXBlbmQgJChJTkNMVURFUykgJF4KCiMgRE8gTk9UIERFTEVURSBUSElTIExJTkUgLS0gbWFrZSBkZXBlbmQgbmVlZHMgaXQK'''
FILES['python.py']='''IyEvdXNyL2Jpbi9lbnYgcHl0aG9uCiMgJShwcm9qZWN0X25hbWUpcy5weQojICUoYXV0aG9yX25hbWVfc2hvcnQpcyAlKGRhdGVfc3RyKXMgVjAuMQoiIiIKJShwcm9qZWN0X2Rlc2NyaXB0aW9uKXMKIiIiCgppbXBvcnQgZ2V0b3B0CmltcG9ydCBzeXMKaW1wb3J0IG9zCmltcG9ydCBzdWJwcm9jZXNzCmltcG9ydCB0cmFjZWJhY2sKaW1wb3J0IGxvZ2dpbmcKaW1wb3J0IGxvZ2dpbmcuaGFuZGxlcnMKCl9fYXBwX18gPSBvcy5wYXRoLmJhc2VuYW1lKF9fZmlsZV9fKQpfX2F1dGhvcl9fID0gIiUoYXV0aG9yX25hbWVfZnVsbClzIgpfX2NvcHlyaWdodF9fID0gIkNvcHlyaWdodCAlKGRhdGVfeWVhcilzIgpfX2NyZWRpdHNfXyA9IFsiJShhdXRob3JfbmFtZV9mdWxsKXMiXQpfX2xpY2Vuc2VfXyA9ICJHUEwiCl9fdmVyc2lvbl9fID0gIjAuMSIKX19tYWludGFpbmVyX18gPSAiJShhdXRob3JfbmFtZV9mdWxsKXMiCl9fZW1haWxfXyA9ICIlKGF1dGhvcl9lbWFpbClzIgpfX3N0YXR1c19fID0gIkJldGEiCgoKIy0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiMgQ29uZmlndXJhYmxlIENvbnN0YW50cwpMT0dfRklMRSA9ICcvdmFyL2xvZy8nICsgb3MucGF0aC5zcGxpdGV4dChfX2FwcF9fKVswXSArICcubG9nJwpMT0dfU0laRSA9IDEwMjQqMTAyNCoyMDAKCnZlcmJvc2UgPSBGYWxzZQpkZWJ1ZyA9IEZhbHNlCgpsb2dnZXIgPSBsb2dnaW5nLmdldExvZ2dlcihfX2FwcF9fKQoKZGVmIHVzYWdlKCk6CiAgICB1c2FnZSA9IFwKIiIiVXNhZ2U6ICUlcyBbb3B0aW9uc10gZm9yY2VkX2FyZwogICAgJShwcm9qZWN0X2Rlc2NyaXB0aW9uKXMKT3B0aW9ucyBhbmQgYXJndW1lbnRzOgogIC1oIC0taGVscCAgICAgICAgICAgICAgICAgICAgICAgICBQcmludHMgdGhpcyBtZXNzYWdlLgogIC12IC0tdmVyYm9zZSAgICAgICAgICAgICAgICAgICAgICBXcml0ZXMgYWxsIG1lc3NhZ2VzIHRvIGNvbnNvbGUuCgogICAgdiUlcwoiIiIgJSUgKF9fYXBwX18sIF9fdmVyc2lvbl9fKQoKICAgIHByaW50IHVzYWdlCgoKZGVmIG1haW4oKToKICAgIGdsb2JhbCB2ZXJib3NlLCBkZWJ1ZwoKICAgIHRyeToKICAgICAgICBvcHRzLCBhcmdzID0gZ2V0b3B0LmdldG9wdChzeXMuYXJndlsxOl0sICJodiIsIFwKICAgICAgICBbImhlbHAiLCAidmVyYm9zZSIsICJkZWJ1ZyJdKQogICAgZXhjZXB0IGdldG9wdC5HZXRvcHRFcnJvciwgZXJyOgogICAgICAgIHByaW50IHN0cihlcnIpCiAgICAgICAgcHJpbnQgdXNhZ2UoKQogICAgICAgIHN5cy5leGl0KDIpCgogICAgdmVyYm9zZSA9IEZhbHNlCiAgICBkZWJ1ZyA9IEZhbHNlCiAgICBmb3JjZWRfYXJnID0gTm9uZQoKICAgICMgU2F2ZSBmb3JjZWQgYXJnCiAgICBpZiBsZW4oYXJncykgPiAwOgogICAgICAgIGZvcmNlZF9hcmcgPSBhcmdzWzBdCiAgICBlbGlmIGxlbihhcmdzKSA+IDE6CiAgICAgICAgdXNhZ2UoKQogICAgICAgIHN5cy5leGl0KDIpCgogICAgZm9yIG8sIGEgaW4gb3B0czoKICAgICAgICBpZiBvIGluICgiLWgiLCAiLS1oZWxwIik6CiAgICAgICAgICAgICMgUHJpbnQgb3V0IGhlbHAgYW5kIGV4aXQKICAgICAgICAgICAgdXNhZ2UoKQogICAgICAgICAgICBzeXMuZXhpdCgpCiAgICAgICAgZWxpZiBvIGluICgiLWRkIiwgIi0tZGVidWciKToKICAgICAgICAgICAgZGVidWcgPSBUcnVlCiAgICAgICAgZWxpZiBvIGluICgiLXYiLCAiLS12ZXJib3NlIik6CiAgICAgICAgICAgIHZlcmJvc2UgPSBUcnVlCgogICAgbG9nX2ZpbGUgPSBMT0dfRklMRQogICAgaWYgbm90IG9zLmFjY2Vzcyhsb2dfZmlsZSwgb3MuV19PSyk6CiAgICAgICAgcHJpbnQgIkNhbm5vdCB3cml0ZSB0byAnJSUobG9nX2ZpbGUpcycuXG5FeGl0aW5nLiIgJSUgbG9jYWxzKCkKICAgICAgICBzeXMuZXhpdCgyKQogICAgZmlsZV9oYW5kbGVyID0gbG9nZ2luZy5oYW5kbGVycy5Sb3RhdGluZ0ZpbGVIYW5kbGVyKGxvZ19maWxlLAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIG1heEJ5dGVzPUxPR19TSVpFLCBiYWNrdXBDb3VudD05KQogICAgZmlsZV9mb3JtYXRlciA9IGxvZ2dpbmcuRm9ybWF0dGVyKCclJShhc2N0aW1lKXMsJSUobGV2ZWxuYW1lKXMsJSUodGhyZWFkKWQsJSUobWVzc2FnZSlzJykKICAgIGZpbGVfaGFuZGxlci5zZXRGb3JtYXR0ZXIoZmlsZV9mb3JtYXRlcikKICAgIGxvZ2dlci5hZGRIYW5kbGVyKGZpbGVfaGFuZGxlcikKCiAgICBpZiB2ZXJib3NlOgogICAgICAgIGNvbnNvbGVfaGFuZGxlciA9IGxvZ2dpbmcuU3RyZWFtSGFuZGxlcihzeXMuc3Rkb3V0KQogICAgICAgIGNvbnNvbGVfZm9ybWF0dGVyID0gbG9nZ2luZy5Gb3JtYXR0ZXIoIlslJShhc2N0aW1lKXNdICUlKGxldmVsbmFtZSktNS41czogJSUobWVzc2FnZSlzIikKICAgICAgICBjb25zb2xlX2hhbmRsZXIuc2V0Rm9ybWF0dGVyKGNvbnNvbGVfZm9ybWF0dGVyKQogICAgICAgIGxvZ2dlci5hZGRIYW5kbGVyKGNvbnNvbGVfaGFuZGxlcikKCiAgICBsb2dnZXIuc2V0TGV2ZWwobG9nZ2luZy5ERUJVRykKCiAgICB0cnk6CiAgICAgICAgIyBETyBTT01FVEhJTkcKICAgICAgICBkb19zb21ldGhpbmcoKQogICAgZXhjZXB0IChLZXlib2FyZEludGVycnVwdCwgU3lzdGVtRXhpdCk6CiAgICAgICAgcGFzcwogICAgZXhjZXB0IEV4Y2VwdGlvbiwgZToKICAgICAgICBwcmludCB0cmFjZWJhY2suZm9ybWF0X2V4YygpCgoKZGVmIGRvX3NvbWV0aGluZygpOgogICAgcHJpbnQgIkhlbGxvIFdvcmxkISIKCmlmIF9fbmFtZV9fID09ICdfX21haW5fXyc6CiAgICBtYWluKCkK'''
FILES['shell.sh']='''IyEvYmluL2Jhc2gKIyAlKHByb2plY3RfbmFtZSlzLnNoCiMgJShhdXRob3JfbmFtZV9zaG9ydClzICUoZGF0ZV9zdHIpcyBWMC4xCiMKIyAlKHByb2plY3RfZGVzY3JpcHRpb24pcwoKZWNobyAiSGVsbG8gV29ybGQhIgo='''

## TEMPLATE FILES END


if __name__ == '__main__':
    main()
