#include "devtools.h"

#include <stdio.h>

#include "makedevtools.def"

// WIP may never finish
bool MakeDevtoolsNoScript(const char *devtools_file) {
    //PyObject *main = PyImport_AddModule("__main__");
    
    PyObject *globals = PyDict_New();
    PyObject *locals = PyDict_New();
    FILE *f = fopen(devtools_file, "r");
    if (f == NULL) {
        printf(" ERROR | Couldn't find devtools file\n");
        return false;
    }

    PyRun_FileExFlags(f, devtools_file, Py_file_input,
                      globals, locals, true, NULL);


    PyObject *bootstrap = PyDict_GetItemString(locals, "Bootstrap");
    PyObject *func_code = PyObject_GetAttrString(bootstrap, "func_code");
    PyObject *co_consts_tuple = PyObject_GetAttrString(func_code, "co_consts");

    Py_ssize_t size = PyTuple_Size(co_consts_tuple);
    size = 0;
    //PyObject *co_consts = PyList_New(size);

    return true;
}

bool MakeDevtools(const char *devtools_file) {
    int ret = PyRun_SimpleString(devtools_script);
    if (ret == 0) {
        printf(" OK | Wrote devtools.raw\n");
        return true;
    } else {
        printf(" ERROR | Couldn't write devtools.raw\n");
        return false;
    }
}
