### project-create

Creates barebone projects for different languages
```
Usage: project-create [options]

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
```


#### Notes

If you make changes to any of the templates, you will need to run compile.py to encode them and update the script.


#### Installation Instructions

Run the following command:
```
SDIR=/usr/local/bin/; wget https://raw.github.com/gesquive/project-create/master/project-create.py -O ${SDIR}/project-create && chmod +x ${SDIR}/project-create
```

Change the value of `SDIR` to change the destination directory.
