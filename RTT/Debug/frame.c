#include "frame.h"

static uint8_t payload[BUFFER_SIZE_UP];
static uint8_t full_pkg[BUFFER_SIZE_UP];

void Send_Packet(Frame_Cmd_t cmd, uint8_t *payload, uint16_t len)
{
    uint16_t ptr = 0;
    uint8_t check_sum = 0;

    full_pkg[ptr++] = FRAME_HEAD1;
    full_pkg[ptr++] = FRAME_HEAD2;
    full_pkg[ptr++] = cmd;
    memcpy(full_pkg + ptr, &len, 2);
    ptr += 2;

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
    uint16_t len = 0;

    for (size_t i = 0; i < param_count; i++)
    {
        if (param_pool[i].is_monitor)
        {
            int8_t b_size = PARAM_TYPE_BYTES(param_pool[i].type);
            if (b_size > 0 && (len + b_size < BUFFER_SIZE_UP))
            {
                memcpy(&payload[len], param_pool[i].ptr, b_size);
                len += b_size;
            }
        }
    }

    Send_Packet(CMD_MONITOR, payload, len);
}

void Mapping_Table_Response_Upload()
{
    uint16_t len = 0;

    for (size_t i = 0; i < param_count; i++)
    {
        if (len + 25 > BUFFER_SIZE_UP)
        {
            break;
        }
        // ID
        payload[len++] = param_pool[i].id;

        // TYPE
        payload[len++] = param_pool[i].type;

        // IS_MONITOR
        payload[len++] = param_pool[i].is_monitor;

        // VALUE
        int8_t b_size = PARAM_TYPE_BYTES(param_pool[i].type);
        if (b_size > 0)
        {
            memcpy(&payload[len], param_pool[i].ptr, b_size);
            len += b_size;
        }

        // NAME
        uint8_t name_len = strlen(param_pool[i].name);
        memcpy(&payload[len], param_pool[i].name, name_len);
        len += name_len;
        payload[len++] = '\0'; // 显式添加结束符
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