#include "param_list.h"

#include "string.h"
#include <log.h>

Param_t param_pool[MAX_PARAM_COUNT] = {};
uint8_t param_count = 0;

int Param_Register(const char *name, void *ptr, ParamType_t type, bool is_monitor)
{
    if (param_count >= MAX_PARAM_COUNT)
    {
        LOG_ERROR("The param_pool exceeds its max limit %d.", MAX_PARAM_COUNT);
        return -1;
    }

    Param_t *p = &(param_pool[param_count]);
    strncpy(p->name, name, 16 - 1);
    p->name[15] = '\0';

    p->ptr = ptr;
    p->type = type;
    p->is_monitor = is_monitor;
    p->id = param_count;

    param_count++;

    return p->id;
}