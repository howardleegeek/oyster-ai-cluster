## 目标
实现限流器，控制每日发帖量和发送频率，支持高峰时段调度

## 约束
- 纯逻辑模块，无 DB 依赖
- 时区: UTC+8 (北京时间)
- 高峰时段: 8-10, 20-23 (北京时间)
- **注意**: S04 不直接调用 queue，由 S03 传入 count

## 接口定义
```python
from zoneinfo import ZoneInfo

class RateLimiter:
    # 北京时区常量
    _BEIJING_TZ = ZoneInfo('Asia/Shanghai')
    
    # 高峰时段 (小时, 北京时间)
    _PEAK_HOURS = [(8, 10), (20, 23)]
    
    def __init__(
        self, 
        *,
        daily_post_cap: int = 120,
        daily_reply_cap: int = 50,
        min_delay: float = 75.0,
        max_delay: float = 240.0,
        peak_delay_multiplier: float = 1.5
    ) -> None:
        """
        Args:
            daily_post_cap: 每日最大发帖数 (默认 120)
            daily_reply_cap: 每日最大回复数 (默认 50)
            min_delay: 最小延迟秒数 (默认 75)
            max_delay: 最大延迟秒数 (默认 240)
            peak_delay_multiplier: 高峰时段延迟倍率 (默认 1.5x)
        """

    def check_daily_cap(
        self, 
        *, 
        current_posts: int, 
        current_replies: int,
        is_reply: bool
    ) -> bool:
        """
        检查是否超过日上限
        
        Args:
            current_posts: 当前已发帖数
            current_replies: 当前已回复数
            is_reply: 是否为回复操作
        
        Returns:
            True = 可以发，False = 超限
        """

    def get_delay(self) -> float:
        """
        返回随机延迟秒数
        
        高峰时段延迟 = base_delay * peak_delay_multiplier
        
        Returns:
            延迟秒数 (范围: [min_delay, max_delay] 或高峰时段倍增)
        """

    def is_peak_hour(self) -> bool:
        """
        当前是否为高峰时段 (北京时间 8-10, 20-23)
        
        Returns:
            True = 高峰时段，False = 非高峰
        """

    def get_next_peak_time(self) -> str:
        """
        返回下一个高峰时段开始的 ISO 时间字符串
        
        用于调度（例如：当前 11 点，下一个高峰是 20 点）
        
        Returns:
            ISO 格式的时间字符串 (北京时间)
        """

    def get_next_off_peak_time(self) -> str:
        """
        返回下一个非高峰时段开始的 ISO 时间字符串
        
        Returns:
            ISO 格式的时间字符串 (北京时间)
        """
```

## 验收标准

### 功能测试 (tests/test_rate_limiter.py)
- [ ] `pytest tests/test_rate_limiter.py -v` 全绿
- [ ] check_daily_cap(0, 0, False) 返回 True
- [ ] check_daily_cap(119, 0, False) 返回 True
- [ ] check_daily_cap(120, 0, False) 返回 False (超限)
- [ ] check_daily_cap(0, 49, True) 返回 True
- [ ] check_daily_cap(0, 50, True) 返回 False (超限)
- [ ] get_delay() 返回 [min_delay, max_delay] 范围内的 float
- [ ] 高峰时段 get_delay() 返回值 * peak_delay_multiplier

### 时段测试 (tests/test_rate_limiter_timing.py)
- [ ] is_peak_hour() 在 08:00-09:59 北京时间返回 True
- [ ] is_peak_hour() 在 20:00-22:59 北京时间返回 True
- [ ] is_peak_hour() 在 07:59 北京时间返回 False
- [ ] is_peak_hour() 在 10:00 北京时间返回 False
- [ ] get_next_peak_time() 返回的未来时间在高峰时段内

### 边界测试 (tests/test_rate_limiter_edge.py)
- [ ] current_posts 传入负数时当作 0 处理
- [ ] current_replies 传入负数时当作 0 处理
- [ ] min_delay > max_delay 时使用 min_delay

### Mock 策略
```python
# RateLimiter 是纯逻辑，不需要 mock
# 直接实例化测试即可
def test_daily_cap():
    limiter = RateLimiter(daily_post_cap=10, daily_reply_cap=5)
    
    assert limiter.check_daily_cap(current_posts=0, current_replies=0, is_reply=False) is True
    assert limiter.check_daily_cap(current_posts=10, current_replies=0, is_reply=False) is False
```

## 不要做
- 不导入 BlueskyQueue (无 DB 依赖)
- 不导入 BlueskyClient
- 不实现 worker 逻辑

## SHARED_CONTEXT
见 specs/SHARED_CONTEXT.md