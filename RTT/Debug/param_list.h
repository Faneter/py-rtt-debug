#pragma once

#include <stdint.h>
#include <stdbool.h>

#define MAX_PARAM_COUNT 64 // 最大可监测的数据量

/**
 * @brief 数据类型
 */
typedef enum
{
    TYPE_FLOAT,
    TYPE_INT32,
} ParamType_t;

/**
 * 获取数据类型对应的字节数
 */
#define PARAM_TYPE_BYTES(type) \
    (type == TYPE_FLOAT) ? 4 : \
    (type == TYPE_INT32) ? 4 : -1

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

extern Param_t param_pool[MAX_PARAM_COUNT];
extern uint8_t param_count;

int Param_Register(const char *name, void *ptr, ParamType_t type, bool is_monitor);
