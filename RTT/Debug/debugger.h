#pragma once

#include <param_list.h>

Param_t param_pool[MAX_PARAM_COUNT] = {};
uint8_t param_count = 0;

void Param_Monitor_Upload(void)
{
    for (size_t i = 0; i < param_count; i++)
    {
        if (param_pool[i].is_monitor) {
            LOG_DEBUG("Monitoring Param ID:%d, value:%f", param_pool[i].id, *((float *)(param_pool[i].ptr)));
        }
    }
}
