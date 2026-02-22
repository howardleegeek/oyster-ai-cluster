# GEM Dispatch Plan (S1-S5)

## 1. 全局依赖图 (并行/串行)

```text
S1-ST1 -> S1-ST2 -> S1-ST3 -> S1-ST4 -> S1-ST5
                                  |         |
                                  |         +-> S1-ST6 -> S1-ST7
                                  |
                                  +-------------------------------> S2-ST1

S2-ST1 -> S2-ST2 -> S2-ST3 -> S2-ST5 -> S2-ST6 -> S2-ST7
             |         |
             |         +-> S2-ST4 -+
             +----------------------+

S2-ST7 -> S3-ST1 -> S3-ST2 -> S3-ST3 -> S3-ST4 -> S3-ST7
                                |
                                +-> S3-ST5 -> S3-ST6 -+
                                                        |
                                                        +-> S3-ST7

S3-ST6 -> S4-ST1 -> S4-ST2 -> S4-ST3 -> S4-ST4 -> S4-ST8
             |         |
             |         +-> S4-ST5 -> S4-ST6 -+
             +-----------------> S4-ST7 ------+

S4-ST8 -> S5-ST1 -> S5-ST2
S4-ST8 -> S5-ST3 -> S5-ST4 -> S5-ST5 -> S5-ST6 -> S5-ST7
S5-ST3 -> S5-ST8
S5-ST2 -> S5-ST7
```

## 2. 子任务调度表

| ID | 类型 | 依赖 | 推荐节点 | 预估 Token 消耗 | 并行建议 |
|---|---|---|---|---:|---|
| S1-ST1 | Backend model | 无 | Mac-2 | 6k-10k | 可与 S1-ST6 前置 UI 准备并行 |
| S1-ST2 | Backend model/schema | S1-ST1 | Mac-2 | 12k-18k | 与 S1-ST3 前期 schema 草稿并行 |
| S1-ST3 | Backend repo/cache | S1-ST2 | Mac-2 | 18k-26k | 与 S1-ST7 API client stub 并行 |
| S1-ST4 | Backend service | S1-ST3 | Mac-2 | 22k-32k | 建议独占执行 |
| S1-ST5 | Backend API | S1-ST4 | Mac-2 | 14k-22k | 与 S1-ST6 并行（mock API） |
| S1-ST6 | Frontend auth core | S1-ST5 | Mac-1 | 20k-30k | 可与 S1-ST7 并行 |
| S1-ST7 | Frontend navbar/profile | S1-ST5 | Mac-1 | 12k-18k | 与 S1-ST6 并行 |
| S2-ST1 | Backend model/schema | S1-ST5 | Mac-2 | 14k-20k | 与 S2-ST6 UI mock 并行 |
| S2-ST2 | Backend repo | S2-ST1 | Mac-2 | 20k-30k | 与 S2-ST4 部分并行 |
| S2-ST3 | Backend engine | S2-ST2 | Mac-2 | 28k-40k | 建议独占执行 |
| S2-ST4 | Backend payment | S2-ST2 | GCP | 24k-36k | 与 S2-ST3 并行（接口契约固定后） |
| S2-ST5 | Backend API | S2-ST3,S2-ST4 | Mac-2 | 16k-24k | 与 S2-ST7 并行 |
| S2-ST6 | Frontend pack flow | S2-ST5 | Mac-1 | 22k-34k | 与 S2-ST7 并行 |
| S2-ST7 | Frontend vault | S2-ST5 | Mac-1 | 14k-22k | 与 S2-ST6 并行 |
| S3-ST1 | Backend model/schema | S2-ST7 | Mac-2 | 14k-20k | 与 S3-ST7 UI scaffold 并行 |
| S3-ST2 | Backend repo txn | S3-ST1 | Mac-2 | 22k-34k | 与 S3-ST5 并行 |
| S3-ST3 | Backend service | S3-ST2 | Mac-2 | 24k-36k | 与 S3-ST4 并行准备 |
| S3-ST4 | Backend API | S3-ST3 | Mac-2 | 16k-24k | 与 S3-ST6 并行 |
| S3-ST5 | Backend buyback core | S3-ST2 | GCP | 20k-32k | 与 S3-ST3 并行 |
| S3-ST6 | Backend buyback API | S3-ST5 | Mac-2 | 12k-18k | 与 S3-ST4 并行 |
| S3-ST7 | Frontend market/buyback | S3-ST4,S3-ST6 | Mac-1 | 24k-36k | 建议独占执行 |
| S4-ST1 | Backend model/schema | S3-ST6 | Mac-2 | 12k-18k | 与 S4-ST8 UI预制并行 |
| S4-ST2 | Backend repo/ledger | S4-ST1 | Mac-2 | 18k-28k | 与 S4-ST7 并行 |
| S4-ST3 | Backend payment svc | S4-ST2 | GCP | 24k-36k | 与 S4-ST5 并行 |
| S4-ST4 | Backend wallet API | S4-ST3 | Mac-2 | 14k-20k | 与 S4-ST8 并行 |
| S4-ST5 | Backend redemption core | S4-ST2 | Mac-2 | 24k-36k | 与 S4-ST3 并行 |
| S4-ST6 | Backend redemption API | S4-ST5 | Mac-2 | 14k-22k | 与 S4-ST7 并行 |
| S4-ST7 | Backend referral | S4-ST2 | Mac-2 | 16k-24k | 与 S4-ST6 并行 |
| S4-ST8 | Frontend wallet/redeem/ref | S4-ST4,S4-ST6,S4-ST7 | Mac-1 | 26k-40k | 建议独占执行 |
| S5-ST1 | Backend rank core | S4-ST8 | Mac-2 | 14k-20k | 与 S5-ST3 并行 |
| S5-ST2 | API + FE leaderboard | S5-ST1 | Mac-1 | 16k-24k | 与 S5-ST4 并行 |
| S5-ST3 | Backend admin auth | S4-ST8 | Mac-2 | 18k-28k | 与 S5-ST1 并行 |
| S5-ST4 | Backend admin nft | S5-ST3 | Mac-2 | 20k-30k | 与 S5-ST5 并行 |
| S5-ST5 | Backend admin pack | S5-ST3 | GCP | 22k-34k | 与 S5-ST4 并行 |
| S5-ST6 | Backend admin ops | S5-ST4,S5-ST5 | Mac-2 | 20k-32k | 与 S5-ST7 并行 |
| S5-ST7 | Frontend admin panel | S5-ST2,S5-ST6 | Mac-1 | 26k-40k | 建议独占执行 |
| S5-ST8 | Launch hardening | S5-ST3 | GCP | 18k-28k | 与 S5-ST6 并行（最后合流） |

## 3. Sprint 内并行策略

### Sprint 1
- 串行主链: `ST1 -> ST2 -> ST3 -> ST4 -> ST5`
- 并行支线: `ST6` 与 `ST7` 在 `ST5` 接口冻结后并行。

### Sprint 2
- 并行窗口 A: `ST2` 与 `ST4`。
- 并行窗口 B: `ST6` 与 `ST7`。
- `ST3`（抽卡引擎）必须单独审查后再并入。

### Sprint 3
- 并行窗口 A: `ST2` 与 `ST5`。
- 并行窗口 B: `ST4` 与 `ST6`。
- `ST7` 在市场与回购 API 合流后执行。

### Sprint 4
- 并行窗口 A: `ST3`（支付）与 `ST5`（兑换核心）。
- 并行窗口 B: `ST6` 与 `ST7`。
- `ST8` 为前端整合终点。

### Sprint 5
- 并行窗口 A: `ST1`（rank）与 `ST3`（admin auth）。
- 并行窗口 B: `ST4` 与 `ST5`。
- 终局合流: `ST6 + ST7 + ST8` 后执行发布检查。

## 4. GLM 执行节奏建议
- 每个节点一次只接 1 个“复杂”任务。
- 每个任务完成后必须跑对应 subtask 的 3+ pytest。
- 跨节点共享统一 API 契约（以本批 refined spec 为准），避免并行冲突。
