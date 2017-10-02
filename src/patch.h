#ifndef __PATCH_H__
#define __PATCH_H__

#include <Python.h>

#include <vector>
#include <uchar.h>

// Structure for passing patch info between calls
struct Patch {
    char *class_name;
    char *method_name;
    char *func_name;
    char *type;
    char *name;
    char *desc;
    char *data;
    char *bytecode;
    size_t bytecode_size;
};

// LoadPatches will load all patches from a given directory
std::vector<Patch *> LoadPatches(const char *patch_dir);

#endif
