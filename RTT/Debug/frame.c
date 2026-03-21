#include "frame.h"

void Send_Packet(Frame_Cmd_t cmd, uint8_t *payload, uint16_t len)
{
    uint8_t full_pkg[BUFFER_SIZE_UP];
    uint8_t ptr = 0;
    uint8_t check_sum = 0;

    full_pkg[ptr++] = FRAME_HEAD1;
    full_pkg[ptr++] = FRAME_HEAD2;
    full_pkg[ptr++] = cmd;
    full_pkg[ptr++] = len;

    memcpy(full_pkg + ptr, payload, len);
    ptr += len;

    for (size_t i = 2; i < ptr; i++)
    {
        check_sum += full_pkg[i];
    }
    full_pkg[ptr++] = check_sum;

    SEGGER_RTT_Write(0, full_pkg, ptr);
}

void Param_Monitor_Upload()
{
    uint8_t payload[BUFFER_SIZE_UP];
    uint8_t len = 0;

    for (size_t i = 0; i < param_count; i++)
    {
        if (param_pool[i].is_monitor)
        {
            memcpy(&payload[len], param_pool[i].ptr, PARAM_TYPE_BYTES(param_pool[i].type));
            len += PARAM_TYPE_BYTES(param_pool[i].type);
        }
    }

    Send_Packet(CMD_MONITOR, payload, len);
}

void Mapping_Table_Response_Upload()
{
    uint8_t payload[BUFFER_SIZE_UP];
    uint8_t len = 0;

    for (size_t i = 0; i < param_count; i++)
    {
        if (param_pool[i].is_monitor)
        {
            // ID
            memcpy(&payload[len], &param_pool[i].id, 1);
            len += 1;

            // TYPE
            memcpy(&payload[len], &param_pool[i].type, 1);
            len += 1;

            // NAME
            memcpy(&payload[len], param_pool[i].name, strlen(param_pool[i].name));
            len += strlen(param_pool[i].name);

            // // VALUE
            // memcpy(&payload[len], param_pool[i].ptr, PARAM_TYPE_BYTES(param_pool[i].type));
            // len += PARAM_TYPE_BYTES(param_pool[i].type);
        }
    }

    Send_Packet(CMD_MAPPING, payload, len);
}

void Edit_Process(uint8_t *payload, uint8_t len)
{
    uint8_t id = payload[0];
    if (id < param_count)
    {
        memcpy(param_pool[id].ptr, payload + 1, len - 1);
    }
}