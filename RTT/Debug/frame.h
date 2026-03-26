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
    CMD_SET_ACK,
} Frame_Cmd_t;

/**
 * @brief 发送数据包
 *
 * 数据包格式: `[FRAME_HEAD(2B)][CMD(1B)][PAYLOAD_LEN(2B)][PAYLOAD(xB)][CHECKSUM(1B)]`
 *
 * @param cmd 数据包指令位
 * @param payload 数据包内容
 * @param len `payload`的长度
 */
void Send_Packet(Frame_Cmd_t cmd, uint8_t *payload, uint16_t len);

/**
 * @brief 向主机发送要监控的数据的实时数值
 *
 * `Payload`格式: [VALUE(xB)] * N
 *
 * `N` 指有`N`个需要发送的数据
 */
void Param_Monitor_Upload();

/**
 * @brief 主机向MCU请求数据名与ID的映射包时，所返回的数据包
 *
 * `Payload`格式: `[ID(1B)][TYPE(1B)][IS_MONITOR(1B)][VALUE(xB)][NAME(xB)]` * `N`
 *
 * `N` 指有`N`个需要发送的数据
 */
void Mapping_Table_Response_Upload();

/**
 * @brief 接收到主机向MCU发送的修改命令后，修改数据并应答(`ACK`)
 *
 * @param payload 收到的修改命令
 * 格式: `[ID(1B)][VALUE(xB)]`
 *
 * @param len `payload`长度
 *
 * 应答`ACK`数据包`Payload`格式: `[ID(1B)][VALUE(xB)]`
 */
void Edit_Process(uint8_t *payload, uint8_t len);