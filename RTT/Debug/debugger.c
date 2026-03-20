#include "debugger.h"

#include "frame.h"
#include <SEGGER_RTT.h>

void Download_Processor()
{
    static uint8_t state = 0;
    static uint8_t cmd, len, count, check_sum;
    static uint8_t payload[64]; // 足够容纳 ID + Float 或请求包

    uint8_t ch;

    // 循环读取 RTT 缓冲区中所有可用字节
    while (SEGGER_RTT_HasKey())
    {
        SEGGER_RTT_Read(0, &ch, 1);

        switch (state)
        {
        case 0: // 找帧头 1
            if (ch == FRAME_HEAD1)
                state = 1;
            break;

        case 1: // 找帧头 2
            if (ch == FRAME_HEAD2)
                state = 2;
            else
                state = 0;
            break;

        case 2: // 读取 CMD
            cmd = ch;
            check_sum = ch; // 开始计算校验和
            state = 3;
            break;

        case 3: // 读取 Payload 长度
            len = ch;
            check_sum += ch;
            count = 0;
            if (len == 0)
                state = 5; // 无数据包直接跳到校验
            else
                state = 4;
            break;

        case 4: // 读取 Payload 数据
            payload[count++] = ch;
            check_sum += ch;
            if (count >= len)
                state = 5;
            break;

        case 5: // 校验
            if (ch == check_sum)
            {
                // 校验通过，执行命令分发
                Handle_Debug_Command(cmd, payload, len);
            }
            state = 0; // 重置状态机
            break;

        default:
            state = 0;
            break;
        }
    }
}

void Handle_Debug_Command(uint8_t cmd, uint8_t *payload, uint8_t len)
{
    switch (cmd)
    {
    case MAPPING_TABLE_REQUEST:
        Mapping_Table_Response_Upload();
        break;

    case EDIT:
        Edit_Process(payload, len);
        break;

    default:
        break;
    }
}

void Loop_Process()
{
    Param_Monitor_Upload();
    Download_Processor();
}