#include <stdint.h>

typedef enum
{
    TYPE_FLOAT,
    TYPE_INT32,
} ParamType_t;

typedef struct
{
    const char *name;
    uint8_t id;
    void *ptr;
    ParamType_t type;
    /* data */
} Param_t;
