#pragma once

#include <param_list.h>

void Download_Processor();
void Handle_Debug_Command(uint8_t cmd, uint8_t *payload, uint8_t len);

void Loop_Process();
