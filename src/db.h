#ifndef __DB_H__
#define __DB_H__

#include "patch.h"

bool DBInit(const char *username, const char *password, const char *db);
bool DBApplyPatch(Patch *p, int id);
bool DBCleanLiveupdates();

#endif
