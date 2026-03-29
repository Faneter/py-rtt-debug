# py-rtt-debug

一个基于`RTT`的单片机调试助手。

## 接收端使用方法

0. 环境要求

已安装`Python`和`J-Link`驱动。

1. 克隆项目

```bash
git clone "https://github.com/Faneter/py-rtt-debug.git"
```

2. 创建虚拟环境并进入（可选）

```bash
python -m venv .venv
./venv/Scripts/activate
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

3. 运行

```bash
python main.py
```

4. 打包为二进制可执行文件（可选）

```bash
pyinstaller --onefile --noconsole display.py
pyinstaller --onefile --add-data "style.tcss;." main.py
```

## 单片机端使用方法

1. 将`RTT`文件夹导入进项目。

2. 在需要使用的文件中，添加头文件

```c
#include <debugger.h>
```

3. 对需要调试的变量，调用`Param_Register`函数。

```c
static float foo = 0.0f;
Param_Register("Foo", &foo, TYPE_FLOAT, true);

static uint8_t bar = 0;
Param_Register("Bar", &bar, TYPE_UINT8, false);
```

4. 在主循环或定时器回调函数中，按照自身需求，重复调用`Loop_Process`函数

```c
Loop_Process();
```
