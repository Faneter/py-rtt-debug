#include "frame.h"

void Param_Monitor_Upload()
{
    uint8_t send_buf[BUFFER_SIZE_UP];
    uint8_t ptr = 0;
    uint8_t check_sum = 0;

    send_buf[ptr++] = FRAME_HEAD1;
    send_buf[ptr++] = FRAME_HEAD2;
    send_buf[ptr++] = PARAM_MONITOR;

    uint8_t len_idx = ptr++;

    uint8_t data_len = 0;

    for (size_t i = 0; i < param_count; i++)
    {
        if (param_pool[i].is_monitor)
        {
            memcpy(&send_buf[ptr], param_pool[i].ptr, PARAM_TYPE_BYTES(param_pool[i].type));
            ptr += PARAM_TYPE_BYTES(param_pool[i].type);
            data_len += PARAM_TYPE_BYTES(param_pool[i].type);
        }
    }

    send_buf[len_idx] = data_len;

    for (size_t i = 2; i < ptr; i++)
    {
        check_sum += send_buf[i];
    }
    send_buf[ptr++] = check_sum;

    SEGGER_RTT_Write(0, send_buf, ptr);
}

void Mapping_Table_Response_Upload()
{
    uint8_t send_buf[BUFFER_SIZE_UP];
    uint8_t ptr = 0;
    uint8_t check_sum = 0;

    send_buf[ptr++] = FRAME_HEAD1;
    send_buf[ptr++] = FRAME_HEAD2;
    send_buf[ptr++] = MAPPING_TABLE_RESPONSE;

    uint8_t len_idx = ptr++;

    uint8_t data_len = 0;

    for (size_t i = 0; i < param_count; i++)
    {
        if (param_pool[i].is_monitor)
        {
            // ID
            memcpy(&send_buf[ptr], &param_pool[i].id, 1);
            ptr += 1;
            data_len += 1;

            // TYPE
            memcpy(&send_buf[ptr], &param_pool[i].type, 1);
            ptr += 1;
            data_len += 1;

            // NAME
            memcpy(&send_buf[ptr], param_pool[i].name, strlen(param_pool[i].name));
            ptr += strlen(param_pool[i].name);
            data_len += strlen(param_pool[i].name);

            // // VALUE
            // memcpy(&send_buf[ptr], param_pool[i].ptr, PARAM_TYPE_BYTES(param_pool[i].type));
            // ptr += PARAM_TYPE_BYTES(param_pool[i].type);
            // data_len += PARAM_TYPE_BYTES(param_pool[i].type);
        }
    }

    send_buf[len_idx] = data_len;

    for (size_t i = 2; i < ptr; i++)
    {
        check_sum += send_buf[i];
    }
    send_buf[ptr++] = check_sum;

    SEGGER_RTT_Write(0, send_buf, ptr);
}
