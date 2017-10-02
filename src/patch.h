#ifndef __PATCH_H__
#define __PATCH_H__

#include <Python.h>

#include <vector>
#include <uchar.h>

#define LIVEUPDATEMAGIC "$lu1"

// Structure for passing patch info between calls
struct Patch {
    uint32_t class_name_size;
    uint32_t method_name_size;
    uint32_t func_name_size;
    uint32_t type_size;
    uint32_t name_size;
    uint32_t desc_size;
    uint32_t bytecode_size;

    char *class_name;
    char *method_name;
    char *func_name;
    char *type;
    char *name;
    char *desc;
    char *data;
    char *bytecode;
};

struct PatchFile {
    char magic[4];
    uint32_t patch_count;
    Patch *patches;
};

// LoadPatches will load all patches from a given directory
std::vector<Patch *> LoadPatches(const char *patch_dir);

bool DumpRawPatchFile(std::vector<Patch *> patches, const char *filename);
bool LoadRawPatchFile(PatchFile *pf, const char *filename);

#endif
