#include "patch.h"

#include <marshal.h>
#include <dirent.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include <string>
#include <sstream>
#include <vector>
#include <iterator>

#define STB_C_LEXER_IMPLEMENTATION
#include "stb_c_lexer.h"

// Small template for assiting string spliting
template<typename out>
void split(const std::string &s, char delim, out result) {
    std::stringstream ss;
    ss.str(s);
    std::string item;
    while (std::getline(ss, item, delim)) {
        *(result++) = item;
    }
}

std::vector<std::string> split(const std::string &s, char delim) {
    std::vector<std::string> elems;
    split(s, delim, std::back_inserter(elems));
    return elems;
}

// This parses the liveupdate deco after the liveupdate decorator
static bool ParseLiveupdate(stb_lexer *lex, Patch *p) {
    stb_c_lexer_get_token(lex);
    if (lex->token != '(') {
        printf(" ERROR | Expected '(' in liveupdate but got something else\n");;
        return false;
    }

    std::vector<std::string> args;
    while (true) {
        stb_c_lexer_get_token(lex);
        if (lex->token == CLEX_dqstring) {
            args.push_back(std::string(lex->string));
        }
        if (lex->token == ',') {
            continue;
        }
        if (lex->token == ')') {
            break;
        }
    }

    p->type = strdup(args[0].c_str());
    p->class_name = strdup(args[1].c_str());
    p->method_name = strdup(args[2].c_str());
    return true;
}

// This parses the patchinfo decorator after the patchinfo identifier
static bool ParseInfo(stb_lexer *lex, Patch *p) {
    stb_c_lexer_get_token(lex);
    if (lex->token != '(') {
        printf(" ERROR | Expected '(' in patchinfo but got something else\n");
        return false;
    }
    std::vector<std::string> args;
    while (true) {
        stb_c_lexer_get_token(lex);
        if (lex->token == CLEX_dqstring) {
            args.push_back(std::string(lex->string));
        }
        if (lex->token == ',') {
            continue;
        }
        if (lex->token == ')') {
            break;
        }
    }
    p->func_name = strdup(args[0].c_str());
    p->desc = strdup(args[1].c_str());
    return true;
}

// CreatePatch returns a Patch pointer given a filename to the patch file
Patch *CreatePatch(const char *filename) {
    Patch *p = (Patch *)calloc(1, sizeof(Patch));
    stb_lexer lex;

    FILE *f = fopen(filename, "r");
    fseek(f, 0, SEEK_END);
    size_t size = ftell(f);
    rewind(f);

    char *data = (char *)calloc(size + 1, 1);
    size_t rsize = fread(data, 1, size, f);
    if (rsize != size) {
        printf(" WARN | File read smaller than file size???\n");
    }

    p->data = data;
    p->name = strdup(filename);

    std::string patch(data);
    std::vector<std::string> lines = split(data, '\n');
    std::vector<std::string> decos;

    for (uint32_t i = 0; i < lines.size(); i++) {
        std::string line = lines[i];
        if (line.size() > 1) {
            if (line[0] == '#' &&
                line[1] == '@') {
                decos.push_back(std::string(&line.c_str()[1]));
            }
        }
    }

    if (decos.size() < 2) {
        printf(" ERROR | Patches must contain at least two comment decos\n");
        return NULL;
    }

    bool liveupdate_ok = false;
    bool patchinfo_ok = false;

    for (uint32_t i = 0; i < decos.size(); i++) {
        std::string deco = decos[i];

        stb_c_lexer_init(&lex, deco.c_str(), deco.c_str() + deco.size(),
                         (char *)malloc(0x10000), 0x10000);
        stb_c_lexer_get_token(&lex);

        if (lex.token != '@') {
            printf(" ERROR | Expected '@' but got something else\n");
            return NULL;
        }

        stb_c_lexer_get_token(&lex);

        if (lex.token != CLEX_id) {
            printf(" ERROR | Unexpected token\n");
            return NULL;
        }

        if (strcmp(lex.string, "liveupdate") == 0) {
            if (liveupdate_ok) {
                printf(" WARN | Two liveupdate decos in %s\n", p->name);
            } else {
                liveupdate_ok = ParseLiveupdate(&lex, p);
            }
        } else if (strcmp(lex.string, "patchinfo") == 0) {
            if (patchinfo_ok) {
                printf(" WARN | Two patchinfo decos in %s\n", p->name);
            } else {
                patchinfo_ok = ParseInfo(&lex, p);
            }
        } else {
            printf(" ERROR | Unknown deco type '%s'\n", lex.string);
        }
    }

    if (liveupdate_ok == false ||
        patchinfo_ok == false) {
        printf(" ERROR | Didn't get a valid liveupdate or patchinfo deco\n");
        printf(" liveupdate:%d patchinfo:%d\n", liveupdate_ok, patchinfo_ok);
        return NULL;
    }


    return p;
}

// PreProceessPatch does the bytecode compilation for the given patch
bool PreProcessPatch(Patch *p) {
    PyErr_Clear();
    PyObject *code = PyImport_AddModule("__main__");
    int ret = PyRun_SimpleString(p->data);
    if (ret != 0) {
        printf(" ERROR | Some kind of error while parsing the patch\n");
        return false;
    }
    if (code == NULL) {
        PyObject *type, *value, *traceback;
        PyErr_Fetch(&type, &value, &traceback);
        printf(" ERROR | Failed to compile patch\n");
        printf("       | %s\n", PyString_AsString(value));
        return false;
    }

    PyObject *func = PyObject_GetAttrString(code, p->func_name);
    if (func == NULL) {
        PyObject *type, *value, *traceback;
        PyErr_Fetch(&type, &value, &traceback);
        printf(" ERROR | Unable to get function object from compiled code\n");
        printf("       | %s\n", PyString_AsString(value));
        return false;
    }
    PyObject *bytecode = PyObject_GetAttrString(func, "func_code");
    if (bytecode == NULL) {
        PyObject *type, *value, *traceback;
        PyErr_Fetch(&type, &value, &traceback);
        printf(" ERROR | Object didn't return an object with func_code\n");
        printf("       | %s\n", PyString_AsString(value));
        return false;
    }

    PyObject *bytecode_str = PyMarshal_WriteObjectToString(bytecode,
                                                           Py_MARSHAL_VERSION);

    PyString_AsStringAndSize(bytecode_str, &p->bytecode, (Py_ssize_t *)&p->bytecode_size);

    return true;
}

// LoadPatches returns a list of valid patches given a directory
std::vector<Patch *> LoadPatches(const char *patch_dir) {
    DIR *dir = opendir(patch_dir);
    dirent *pent = NULL;
    std::vector<Patch *> patches;

    while ((pent = readdir(dir))) {
        if (pent->d_name[0] == '.') {
            continue;
        }

        char *filename = (char *)calloc(256, 1);
        strcpy(filename, patch_dir);
        strcat(filename, "/");
        strcat(filename, pent->d_name);

        if (pent->d_type == DT_REG) {
            Patch *p = CreatePatch(filename);
            if (p != NULL) {
                if (PreProcessPatch(p)) {
                    patches.push_back(p);
                }
            }
        }
    }
    return patches;
}

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-result"

bool LoadRawPatchFile(PatchFile *pf, const char *filename) {
    FILE *f = fopen(filename, "rb");
    fread(pf->magic,       sizeof(char),     4, f);
    fread(&pf->patch_count, sizeof(uint32_t), 1, f);

    pf->patches = (Patch *)calloc(sizeof(Patch), pf->patch_count);

    for (uint32_t i = 0; i < pf->patch_count; i++) {
        Patch *p = &pf->patches[i];
        fread(p, sizeof(uint32_t), 7, f);

        p->class_name = (char *)calloc(1, p->class_name_size + 1);
        p->func_name = (char *)calloc(1, p->func_name_size + 1);
        p->method_name = (char *)calloc(1, p->method_name_size + 1);
        p->type = (char *)calloc(1, p->type_size + 1);
        p->name = (char *)calloc(1, p->name_size + 1);
        p->desc = (char *)calloc(1, p->desc_size + 1);
        p->bytecode = (char *)calloc(1, p->bytecode_size + 1);

        fread(p->class_name,  sizeof(char), p->class_name_size, f);
        fread(p->method_name, sizeof(char), p->method_name_size, f);
        fread(p->func_name,   sizeof(char), p->func_name_size, f);
        fread(p->type,        sizeof(char), p->type_size, f);
        fread(p->name,        sizeof(char), p->name_size, f);
        fread(p->desc,        sizeof(char), p->desc_size, f);
        fread(p->bytecode,    sizeof(char), p->bytecode_size, f);
    }
    return true;
}

bool DumpRawPatchFile(std::vector<Patch *> patches, const char *filename) {
    FILE *f = fopen(filename, "wb");
    if (f == NULL) {
        return false;
    }

    uint32_t c = patches.size();

    fwrite(LIVEUPDATEMAGIC, strlen(LIVEUPDATEMAGIC), 1, f);
    fwrite(&c, sizeof(uint32_t), 1, f);

    for (uint32_t i = 0; i < c; i++) {
        Patch *p = patches[i];

        p->class_name_size = strlen(p->class_name);
        p->method_name_size = strlen(p->method_name);
        p->func_name_size = strlen(p->func_name);
        p->type_size = strlen(p->type);
        p->name_size = strlen(p->name);
        p->desc_size = strlen(p->desc);

        // Write the first 7 entries containing the sizes of all of the strings
        fwrite(p,              sizeof(uint32_t), 7, f);
        fwrite(p->class_name,  sizeof(char), p->class_name_size, f);
        fwrite(p->method_name, sizeof(char), p->method_name_size, f);
        fwrite(p->func_name,   sizeof(char), p->func_name_size, f);
        fwrite(p->type,        sizeof(char), p->type_size, f);
        fwrite(p->name,        sizeof(char), p->name_size, f);
        fwrite(p->desc,        sizeof(char), p->desc_size, f);
        fwrite(p->bytecode,    sizeof(char), p->bytecode_size, f);
    }

    return true;
}

#pragma GCC diagnostic pop
