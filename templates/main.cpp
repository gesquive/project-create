/*
 * %(project_name)s
 * Copyright (C) %(author_name_full)s %(date_year)s <%(author_email)s>
 *
 * %(project_name)s is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * %(project_name)s is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include <signal.h>
#include <cctype>

#define AUTHOR "%(author_name_full)s (%(author_email)s)"
#define VERSION "0.1"

const char* app_name;

inline void PrintUsage() {
    printf(
"Usage: %%s [options] forced_arg optional_arg\n"
"    %(project_description)s\n"
"Options and arguments:\n"
"  forced_arg                      A forced argument\n"
"  optional_arg                    An option argument\n"
"  -s --switch <value>             A switch with a value\n"
"  -h --help                       Prints this message.\n"
"  -v --verbose                    Writes all messages to console.\n\n"
"    v%%s\n", app_name, VERSION);
}

void SigHandler(int sig) {
    printf("\nGoodbye.\n");
    exit(0);
}

int main(int argc, char* argv[]) {
    signal(SIGINT, &SigHandler);

    app_name = basename(argv[0]);

    bool verbose = false;
    char *switch_value = NULL;

    int c;
    int option_index = 0;

    static struct option long_options[] = {
        //{const char* name, int has_arg, int* flag, int val },
        {"help", 0, 0, 'h'},
        {"verbose", 0, 0, 'v'},
        {"switch", 1, 0, 's'},
        {0, 0, 0, 0}
    };

    do {
        c = getopt_long(argc, argv, "hvs:", long_options, &option_index);
        switch (c) {
        case 'v':
            verbose = true;
            break;
        case 'h':
            PrintUsage();
            exit(0);
            break;
        case 's':
            // Validate the switch value here
            switch_value = new char[strlen(optarg)+1];
            strcpy(switch_value, optarg);
            break;
        case ':':
            if (optopt) {
                printf("Missing an argument for flag '-%%c'\n", optopt);
            } else {
                printf("Missing an argument for flag  \"--%%s\"\n",
                       argv[optind-1]);
            }
            PrintUsage();
            exit(2);
            break;
        case '?':
            if (optopt) {
                printf("Unrecognized flag '-%%c'\n", optopt);
            } else {
                printf("Unrecognized flag \"--%%s\"\n", argv[optind-1]);
            }
            PrintUsage();
            exit(2);
            break;
        case -1:
            break;
        default:
            printf("--%%d not completed\n", c);
            break;
        }
    } while (c != -1);

    char *forced_arg = NULL;
    char *optional_arg = NULL;

    int nonoptc = argc - optind;
    if (nonoptc >= 1 && nonoptc <= 2) {
        // Validate the forced argument here
        forced_arg = new char[strlen(argv[optind])+1];
        strcpy(forced_arg, argv[optind]);

        if (++optind < argc) {
            // Validate the optional argument here
            optional_arg = new char[strlen(argv[optind])+1];
            strcpy(optional_arg, argv[optind]);
        }
    } else {
        printf("Incorrect number of arguments.\n");
        PrintUsage();
        exit(2);
    }

    //TODO: Run actual code here
    printf("Hello World!\n");

    if (verbose) {
        printf("End of code.\n");
    }

    exit(0);
}
