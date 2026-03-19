# TypeType 功能路线图

> 更新时间：2026-03-19
>
> 本文档记录 TypeType 客户端当前完成状态与后续功能规划。

---

## 一、已完成

| 阶段 | 内容 | 状态 |
|------|------|------|
| CharStat 实体 | `src/backend/models/char_stats.py` — 字符级统计 (char, char_count, error_char_count, total_ms, min_ms, max_ms, last_seen) | ✅ |
| ScoreData 实体 | `src/backend/models/score_data.py` — 会话级成绩 | ✅ |
| TypingService 集成 | `handleCommittedText` 合并循环：char_stats 累积 + prefix_sum 更新 + 着色，单次遍历完成 | ✅ |
| Bridge 合并 | 原 Backend 合并到 Bridge，key_listener 由 Bridge 持有，QML 统一走 appBridge | ✅ |
| 目录结构 | 领域实体统一到 `models/`，删除 `typing/` 目录 | ✅ |

### CharStat 实体设计

```python
@dataclass
class CharStat:
    char: str               # 字符（主键）
    char_count: int         # 字符上屏次数
    error_char_count: int   # 错误字符次数
    total_ms: float         # 累计耗时（毫秒）
    min_ms: float           # 最快按键
    max_ms: float           # 最慢按键
    last_seen: str          # 最近一次出现时间

    def accumulate(keystroke_ms, is_error) -> None
    def merge(other: CharStat) -> None
    @property avg_ms -> float
    @property error_rate -> float
```

### 同步特性

- `char_count` 系字段取 max（本地全量值直接覆盖远端）
- `min_ms` / `max_ms` 取极值
- `last_seen` 取最新
- 聚合数据天然无冲突 —— 不存在"本地说 100 次、远端说 200 次"的矛盾

---

## 二、本地持久化

```
Phase 2: 本地 SQLite 持久化
```

### 2.1 本地表结构

```sql
CREATE TABLE char_stats (
    char              TEXT PRIMARY KEY,
    char_count        INTEGER NOT NULL DEFAULT 0,
    error_char_count  INTEGER NOT NULL DEFAULT 0,
    total_ms          REAL NOT NULL DEFAULT 0.0,
    min_ms            REAL NOT NULL DEFAULT 0.0,
    max_ms            REAL NOT NULL DEFAULT 0.0,
    last_seen         TEXT NOT NULL DEFAULT '',

    last_synced_at    TEXT,             -- 上次同步成功时间
    is_dirty          INTEGER DEFAULT 1 -- 1=有变更未同步
);
```

### 2.2 Port 层

```python
from abc import ABC, abstractmethod

class CharStatsRepository(ABC):
    @abstractmethod
    def get(self, char: str) -> CharStat | None: ...

    @abstractmethod
    def save(self, stat: CharStat) -> None: ...

    @abstractmethod
    def get_all_dirty(self) -> list[CharStat]: ...

    @abstractmethod
    def mark_synced(self, chars: list[str], synced_at: str) -> None: ...
```

### 2.3 Integration 实现

```python
class SqliteCharStatsRepository(CharStatsRepository):
    """本地 SQLite 实现"""

class NoopCharStatsRepository(CharStatsRepository):
    """占位实现，无持久化时不影响打字功能"""
```

---

## 三、CharStatsService

```
Phase 3: CharStatsService — 管理内存缓存 + 持久化调度
```

```python
class CharStatsService:
    def __init__(self, repository: CharStatsRepository):
        self._repo = repository
        self._cache: dict[str, CharStat] = {}

    def accumulate(self, char: str, keystroke_ms: float, is_error: bool) -> None:
        """累积一次字符结果（从 TypingService 调用）"""

    def flush(self) -> None:
        """持久化缓存到本地（打完一篇文章后调用）"""

    def get_weakest_chars(self, n: int) -> list[CharStat]:
        """获取最弱的 n 个字符（按 error_rate 排序）"""

    def get_all(self) -> dict[str, CharStat]:
        """获取全部统计"""
```

集成点：`TypingService.typingEnded` → 触发 `CharStatsService.flush()`

---

## 四、远端同步（Spring Boot）

```
Phase 4: 远端同步（与 spring-boot-backend-design.md 配合）
```

### 4.1 API 设计

```yaml
POST   /api/v1/sync/char-stats    # 批量上传本地变更
GET    /api/v1/sync/char-stats    # 拉取远端变更（since 参数）
```

### 4.2 MySQL 表结构

```sql
CREATE TABLE user_char_stats (
    user_id         VARCHAR(64),
    char            VARCHAR(4),
    char_count      INT,
    error_char_count INT,
    total_ms        DOUBLE,
    min_ms          DOUBLE,
    max_ms          DOUBLE,
    last_seen       DATETIME,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, char)
);
```

### 4.3 同步策略（混合方案）

```
启动时：pull 远端数据到本地
打完文章：push dirty 数据
关闭应用：push dirty 数据兜底
```

### 4.4 Port 层

```python
class SyncRepository(ABC):
    @abstractmethod
    def push_char_stats(self, stats: list[CharStat]) -> None: ...

    @abstractmethod
    def pull_char_stats(self, since: datetime) -> list[CharStat]: ...
```

### 4.5 边界情况

| 场景 | 处理方式 |
|------|----------|
| 首次登录新设备 | pull 全量远端数据到本地 |
| 离线打字一周后上线 | 批量 push 积压的 dirty 数据 |
| 多设备同时打字 | 本地值即最新全量，直接覆盖远端 |
| 同步中途断网 | 下次重试，is_dirty = 1 的数据会再次上传 |
| 用户注销 | 清本地数据，下次登录触发 pull |

---

## 五、UI 功能

```
Phase 5: QML UI — 显示薄弱字、推荐练习
```

### 5.1 薄弱字看板

- 显示 `error_rate` 最高的前 10 个字符
- 每个字符展示：输入次数、错误率、平均耗时

### 5.2 推荐练习

- 根据薄弱字生成随机练习文本
- 权重算法：`weight = error_rate * log(char_count + 1)`（兼顾错误率和练习量）

### 5.3 进度追踪

- 展示单字符的 `error_rate` 变化曲线（随时间/随 session）

---

## 六、后续探索

| 方向 | 说明 | 优先级 |
|------|------|--------|
| 混淆对统计 | 记录哪些字符经常互换（如 "的"↔"得"） | 中 |
| 跨词频分层 | 按 pinyin / 部首 / 词频分组统计 | 低 |
| 智能推荐 | 根据薄弱点动态调整练习难度 | 低 |
| 社交功能 | 好友对比、对战模式 | 待定 |

---

## 七、目录结构

```
src/backend/
├── models/
│   ├── score_data.py       # 会话级成绩实体
│   ├── char_stats.py       # 字符级统计实体（新增）
│   └── dto/
│       └── score_dto.py    # 成绩 DTO
├── domain/
│   ├── typing_service.py   # 打字服务（含 char_stats 累积逻辑）
│   ├── text_load_service.py
│   └── auth_service.py
├── application/
│   └── usecases/
│       └── score_usecase.py
├── integration/
│   └── ...                 # 现有实现
└── ...
```
