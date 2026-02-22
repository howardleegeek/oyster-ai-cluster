# Task B1: gemApi.ts 添加 put() 方法

## 目标
在前端 API 客户端添加缺失的 `put()` 方法。

## 文件
- `lumina/services/gemApi.ts`

## 具体改动

找到现有的 HTTP 方法定义（约第 281-320 行），在 `patch()` 方法之后、`delete()` 之前添加 `put()` 方法：

```typescript
async put<T>(
  endpoint: string,
  data?: Record<string, unknown>,
  options?: { requireAuth?: boolean }
): Promise<T> {
  return request<T>(endpoint, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: data ? JSON.stringify(data) : undefined,
  }, options?.requireAuth ?? true);
},
```

## 验证
1. TypeScript 编译无错误: `cd lumina && npx tsc --noEmit`
2. grep 确认 put 方法存在: `grep -n "put<T>" services/gemApi.ts`
