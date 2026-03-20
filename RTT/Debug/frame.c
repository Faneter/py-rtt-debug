#include "frame.h"

void Param_Monitor_Upload()
{
    uint8_t send_buf[1024];
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

    SEGGER_RTT_Write(1, send_buf, ptr);
}
