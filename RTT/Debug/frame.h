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

/**
 * @brief 发送数据包
 *
 * 数据包格式：[FRAME_HEAD(2B)][CMD(1B)][PAYLOAD_LEN(1B)][PAYLOAD][CHECKSUM(1B)]
 *
 * @param cmd 数据包指令位
 * @param payload 数据包内容
 * @param len `payload`的长度
 */
void Send_Packet(Frame_Cmd_t cmd, uint8_t *payload, uint8_t len);

void Param_Monitor_Upload();
void Mapping_Table_Response_Upload();
void Edit_Process(uint8_t *payload, uint8_t len);