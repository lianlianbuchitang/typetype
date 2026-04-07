# 开发文档

## 日志系统使用规范

### 基本使用

项目使用 Python 标准库 `logging` 模块，提供统一的日志输出。推荐方式：

```python
from src.backend.utils.logger import log_debug, log_info, log_warning, log_error

log_debug("调试信息")
log_info("普通信息")
log_warning("警告信息")
log_error("错误信息")
```

或者直接使用标准 `logging` API：

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("调试信息")
logger.info("普通信息")
```

### 日志级别约定

| 级别 | 使用场景 |
|------|----------|
| DEBUG | 开发调试信息，用户通常不需要看到 |
| INFO | 正常运行的关键节点信息（如启动、平台检测结果） |
| WARNING | 不影响运行的异常情况 |
| ERROR | 错误信息，功能出错但程序可以继续运行 |

### 环境变量控制

```bash
# 开启 debug 日志
TYPETYPE_DEBUG=1 uv run python main.py

# 设置特定日志级别
TYPETYPE_LOG_LEVEL=info uv run python main.py
```

### 输出位置

- **控制台**: 带 ANSI 颜色高亮输出
- **日志文件**: `~/.typetype/app.log`，自动轮转（10MB/文件，保留 5 个备份）

### 开发规范

- **禁止** 在正式代码中使用裸 `print()`，统一使用日志 API
- **RinUI/** 第三方库例外，按约定不修改其源码
- 错误信息使用 `log_error()`，不要用 `print()` 直接打栈跟踪
