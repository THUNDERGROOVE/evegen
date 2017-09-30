#ifndef __DEVTOOLS_H__
#define __DEVTOOLS_H__

#include <Python.h>
#include <marshal.h>

bool MakeDevtools(const char *devtools_file);
bool MakeDevtoolsNoScript(const char *devtools_file);

#endif
