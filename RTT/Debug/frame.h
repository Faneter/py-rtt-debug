#pragma once

#include "param_list.h"
#include "string.h"
#include "SEGGER_RTT.h"

#define FRAME_HEAD1 0x5A
#define FRAME_HEAD2 0xA5

typedef enum
{
    CMD_MONITOR = 1,
    CMD_MAPPING,
    CMD_REQ_MAP,
    CMD_SET_VAL,
} Frame_Cmd_t;

void Param_Monitor_Upload();
void Mapping_Table_Response_Upload();
void Edit_Process(uint8_t *payload, uint8_t len);