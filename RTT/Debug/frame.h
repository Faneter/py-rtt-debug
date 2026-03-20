#pragma once

#include "param_list.h"
#include "string.h"
#include "SEGGER_RTT.h"

#define FRAME_HEAD1 0x5A
#define FRAME_HEAD2 0xA5

typedef enum
{
    PARAM_MONITOR = 0,
    MAPPING_TABLE_RESPONSE,
    MAPPING_TABLE_REQUEST,
    EDIT,
} Payload_Type_t;

void Param_Monitor_Upload();
void Mapping_Table_Response_Upload();
