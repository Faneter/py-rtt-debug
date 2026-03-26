#pragma once

#include <param_list.h>

/**
 * @brief 从主机读取数据并解析出数据包
 */
void Download_Processor();

/**
 * @brief 根据解析出的数据包执行对应操作
 *
 * @param cmd 数据包指令
 * @param payload 数据包内容
 * @param len `payload`长度
 */
void Handle_Debug_Command(uint8_t cmd, uint8_t *payload, uint8_t len);

/**
 * @brief 用于循环执行的函数，其中包括了对主机数据的接收，和需要监控的数据的上传
 */
void Loop_Process();
