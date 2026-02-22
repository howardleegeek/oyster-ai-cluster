# Task B2: 前端 service 文件 .data 解包修复

## 目标
移除所有 API service 文件中错误的 `.data` 二次解包。`gemApi.request()` 已经解包了响应，service 文件再次访问 `.data` 会得到 `undefined`。

## 规则
- `gemApi.get/post/patch/put/delete()` 返回的已经是解包后的数据
- 所有 `const response = await gemApi.xxx(); return response.data;` 改为 `return gemApi.xxx();`
- 或 `return (await gemApi.xxx()).data` 改为 `return gemApi.xxx()`

## 文件清单

### 1. `lumina/services/adminApi.ts`
搜索所有 `response.data` 或 `.data`，改为直接返回 response。

### 2. `lumina/services/walletApi.ts`
同上。

### 3. `lumina/services/orderApi.ts`
同上。

### 4. `lumina/services/referralApi.ts`
同上。

### 5. `lumina/services/rankApi.ts`
同上。

### 6. `lumina/services/marketApi.ts`
同上。

### 7. `lumina/services/vaultApi.ts`
同上。

### 8. `lumina/services/packApi.ts`
同上。

## 修改模式

Before:
```typescript
async listPacks() {
  const response = await gemApi.get<PackListResp>('/packs');
  return response.data;
}
```

After:
```typescript
async listPacks() {
  return gemApi.get<PackListResp>('/packs');
}
```

或者如果是:
```typescript
async listPacks(): Promise<PackListResp> {
  const response = await gemApi.get('/packs');
  return response.data;
}
```

改为:
```typescript
async listPacks(): Promise<PackListResp> {
  return gemApi.get<PackListResp>('/packs');
}
```

**注意**: 不是所有都用 `.data`，只修改确实有 `.data` 访问的。有些可能直接 return 了，那些不用改。

## 验证
1. `cd lumina && grep -rn "\.data" services/ | grep -v "node_modules"` — 确认无残留的 `.data` 访问（metadata、formData 等非 response.data 的除外）
2. TypeScript 编译: `npx tsc --noEmit`
