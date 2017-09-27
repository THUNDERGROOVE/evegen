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

static void eat_spaces(std::string s, int *i) {
    while (s[*i] == ' ' || s[*i] == '\r' || s[*i] == '\n') {
        (*i)++;
    }
}

static std::string eat_ident(std::string s, int *i) {
    int start = *i;
    while (isalpha(s[*i])) {
        (*i)++;
    }
    return std::string(s.c_str()+start, *i - start);
}

// TODO: Error prone
static std::string eat_quote_str(std::string s, int *i) {
    if (s[*i] != '"') {
        printf(" ERROR | Start quote not found at start of eat_quote_str\n");
        printf("       | Got '%c' at %d\n", s[*i], *i);
        exit(-1);
        return std::string("");
    }

    (*i)++;


    int start = *i;
    while (s[*i] != '"') {
        (*i)++;
    }

    std::string out(s.c_str() + start, *i - start);
    if (s[*i] != '"') {
        printf(" ERROR | End quote not found at start of eat_quote_str\n");
        return std::string("");
    }
    (*i)++;

    return out;
}

// Parses a statement like ("something", "else", "and")
static std::vector<std::string> parse_arguments(std::string s, int *i, bool *ok) {
    std::vector<std::string> out;

    eat_spaces(s, i);
    if (s[*i] != '(') {
        printf(" ERROR | Expected a '('\n");
        *ok = false;
        return out;
    }
    (*i)++;

    while (s[*i] != ')') {
        std::string n = eat_quote_str(s, i);
        out.push_back(n);
        eat_spaces(s, i);
        if (s[*i] == ',') {
            (*i)++;
        }
        eat_spaces(s, i);
    }
    (*i)++;

    return out;
}

static void print_additional_info(int i) {
    printf(" Error occured at %d\n", i);
}

Patch *CreatePatch(const char *filename) {
    Patch *p = (Patch *)calloc(1, sizeof(Patch));

    FILE *f = fopen(filename, "r");
    fseek(f, 0, SEEK_END);
    size_t size = ftell(f);
    rewind(f);

    char *data = (char *)calloc(size + 1, 1);
    size_t rsize = fread(data, 1, size, f);
    if (rsize != size) {
        printf(" WARN | File read smaller than file size???\n");
    }

    std::string patch(data);
    std::vector<std::string> lines = split(data, '\n');
    std::string deco = lines[0];
    int i = 0;
    eat_spaces(deco, &i);
    if (deco[i] != '#') {
        printf(" ERROR | First line of a patch must contain a comment\n");
        print_additional_info(i);
        return NULL;
    }
    i++;
    eat_spaces(deco, &i);
    if (deco[i] != '@') {
        printf(" ERROR | Comment must begin with '@'\n");
        print_additional_info(i);
        return NULL;
    }
    i++;

    std::string t = eat_ident(deco, &i);
    if (t != "liveupdate") {
        printf(" ERROR | Unknown patch type: %s\n", t.c_str());
        return NULL;
    }

    bool ok = true;
    std::vector<std::string> args = parse_arguments(deco, &i, &ok);
    if (!ok) {
        return NULL;
    }

    if (args.size() != 3) {
        printf(" ERROR | liveupdate deco expects 3 arguments\n");
        return NULL;
    }

    p->data = data;
    p->name = strdup(filename);
    p->type = strdup(args[0].c_str());
    p->class_name = strdup(args[1].c_str());
    p->method_name = strdup(args[2].c_str());


    // TODO: This is beyond dangerous LOL
    p->func_name = strdup(split(split(lines[1], ' ')[1], '(')[0].c_str());

    return p;
}

bool PreProcessPatch(Patch *p) {
    //PyObject *code = Py_CompileStringFlags(p->data, p->name, Py_file_input, NULL);
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
