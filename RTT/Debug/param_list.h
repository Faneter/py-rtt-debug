#pragma once

#include <stdint.h>
#include <stdbool.h>

#define MAX_PARAM_COUNT 16 // 最大可监测的数据量

/**
 * @brief 数据类型
 */
typedef enum
{
    DEBUGGER_TYPE_FLOAT = 'f',
    DEBUGGER_TYPE_INT32 = 'i',
    DEBUGGER_TYPE_UINT32 = 'I',
    DEBUGGER_TYPE_INT16 = 'h',
    DEBUGGER_TYPE_UINT16 = 'H',
    DEBUGGER_TYPE_INT8 = 'b',
    DEBUGGER_TYPE_UINT8 = 'B',
} ParamType_t;

// clang-format off
/**
 * @brief 获取数据类型对应的字节数
 */
#define PARAM_TYPE_BYTES(type) \
    (type == DEBUGGER_TYPE_FLOAT || type == DEBUGGER_TYPE_INT32 || type == DEBUGGER_TYPE_UINT32) ? 4 : \
    (type == DEBUGGER_TYPE_INT16 || type == DEBUGGER_TYPE_UINT16)                                ? 2 : \
    (type == DEBUGGER_TYPE_INT8  || type == DEBUGGER_TYPE_UINT8)                                 ? 1 : -1
// clang-format on

/**
 * @brief 承载一个参数的结构体
 *
 * @param name 参数展示名称
 * @param id 参数id
 * @param ptr 要监测的参数
 * @param type 参数类型
 * @param is_monitor 是否要高频上传显示波形
 */
typedef struct __attribute__((packed))
{
    char name[16];
    uint8_t id;
    void *ptr;
    ParamType_t type;
    bool is_monitor;
} Param_t;

// 参数池
extern Param_t param_pool[MAX_PARAM_COUNT];

// 参数池中已注册的参数的数量
extern uint8_t param_count;

/**
 * @brief 将要进行观测的参数进行注册
 * 
 * @param name 为要注册的参数命名
 * @param ptr 要注册的参数的指针
 * @param type 要注册的参数的类型
 * @param is_monitor 是否实时监控该参数
 * @return int 注册后的的参数在参数池中的序列，若为-1则说明参数池已满
 */
int Param_Register(const char *name, void *ptr, ParamType_t type, bool is_monitor);
