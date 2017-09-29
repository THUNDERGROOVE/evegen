#include <Python.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#include "patch.h"
#include "devtools.h"
#include "config.h"
#include "db.h"

bool do_devtools = false;
bool do_patch = false;
char *username = NULL;
char *password = NULL;
char *db = NULL;
char *devtools_in = NULL;

static void print_help() {
    printf("%s - %s\n", PACKAGE, PACKAGE_VERSION);
    printf("    -dev  : outputs devtools.raw\n");
    printf("          : optionally supply <devtools file>\n");
    printf("    -patch: applies patches instead of doing a dry run\n");
    printf("          : supply <username> <password> <db>\n");
}

int main(int argc, char **argv) {
    if (argc == 1) {
        print_help();
        return 0;
    }
    for (int i = 0; i < argc; i++) {
        if (strcmp(argv[i], "-dev") == 0) {
            if (argc > i + 1) {
                char *devtools_name = argv[i + 1];
                if (*devtools_name != '-') {
                    devtools_in = argv[i + 1];
                }
            }
            do_devtools = true;
        }
        if (strcmp(argv[i], "-patch") == 0) {
            if (argc < i + 3) {
                printf("-patch expects <username> <password> <db>\n");
                return 0;
            } else {
                username = argv[i + 1];
                password = argv[i + 2];
                db = argv[i + 3];
            }
            do_patch = true;
        }
        if (strcmp(argv[i], "--help") == 0 ||
            strcmp(argv[i], "-h") == 0) {
            print_help();
            return 0;
        }
    }

    Py_Initialize();

    if (do_patch) {
        std::vector<Patch *> patches = LoadPatches("patches");
        printf(" OK | Loaded %lu patches\n", patches.size());
        DBInit(username, password, db);
        DBCleanLiveupdates();
        printf(" > Applying patches\n");
        for (uint32_t i = 0; i < patches.size(); i++) {
            Patch *p = patches[i];
            printf(" %d/%lu: %s\n", i + 1, patches.size(), p->name);
            DBApplyPatch(p, i);
        }
    }

    if (do_devtools) {
        if (devtools_in != NULL) {
            MakeDevtools(devtools_in);
        } else {
            MakeDevtools("devtools.py");
        }
    }

    return 0;
}
