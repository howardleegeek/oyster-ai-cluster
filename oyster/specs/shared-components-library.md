# Shared Components Library (配件库) for 13 AI Agent + Web3 Projects

**Date:** 2026-02-18 (GitHub snapshot via `gh api`)  
**Goal:** Build a thin, reusable integration layer over best-in-class open-source tools so 13 projects stop rebuilding the same wallet/agent/DeFi/infra logic.

---

## Step 1) Open-source research: reusable AI Agent + Web3 components

### 1.1 Agent frameworks with reusable components

| Repo | Stars | License | Reusable components (what you can reuse now) |
|---|---:|---|---|
| [coinbase/agentkit](https://github.com/coinbase/agentkit) | 1,097 | Apache-2.0 | Agent wallet abstractions, onchain action/tool layer, wallet providers, framework extensions (LangChain/OpenAI/MCP), project scaffolding (`create-onchain-agent`). |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | 24,821 | MIT | Stateful graph runtime, durable checkpoints (`sqlite/postgres`), prebuilt agent nodes, JS/Python SDKs, human-in-loop control points. |
| [fetchai/uAgents](https://github.com/fetchai/uAgents) | 1,545 | Apache-2.0 | Agent runtime (Python), scheduler/event decorators, message protocols, agent identity/address model, decentralized agent communication primitives. |
| [elizaOS/eliza](https://github.com/elizaOS/eliza) | 17,534 | MIT | Plugin-based multi-agent runtime, agent orchestration, tool/plugin ecosystem, built-in integration points (Discord/Telegram/model providers). |
| [autonomys/auto-sdk](https://github.com/autonomys/auto-sdk) | 12 | MIT | Modular packages (`auto-wallet`, `auto-consensus`, `auto-agents`, `auto-dag-data`, `auto-mcp-servers`) for wallet/consensus/data layers. |
| [coinbase/agentic-wallet-skills](https://github.com/coinbase/agentic-wallet-skills) | 44 | MIT | Prebuilt wallet-related MCP/skills patterns to speed up agent tool wiring. |

### 1.2 Web3 / DeFi building blocks

| Repo | Stars | License | Reusable components |
|---|---:|---|---|
| [scaffold-eth/scaffold-eth-2](https://github.com/scaffold-eth/scaffold-eth-2) | 1,978 | MIT | Dapp starter architecture, wagmi-based custom hooks, reusable web3 UI components, local faucet/burner-wallet dev workflow. |
| [thirdweb-dev/js](https://github.com/thirdweb-dev/js) | 626 | Apache-2.0 | Unified multi-chain SDK, in-app wallet APIs, `engine` tx execution client, `insight` indexed data client, `vault-sdk` secure key APIs, React/UI adapters. |
| [wevm/wagmi](https://github.com/wevm/wagmi) *(requested as `wagmi-dev/wagmi`)* | 6,661 | MIT | Wallet connectors + React/Vue/Solid/core primitives for Ethereum account state, contract reads/writes, transaction lifecycle hooks. |
| [Uniswap/sdk-core](https://github.com/Uniswap/sdk-core) | 135 | MIT | Core AMM math/data primitives (Token, CurrencyAmount, Fraction, Price, Percent). Note: repo points to newer [Uniswap/sdks](https://github.com/Uniswap/sdks). |
| [aave/aave-v3-core](https://github.com/aave/aave-v3-core) | 1,076 | BUSL-1.1 (README marks deprecated) | Lending protocol core contracts/ABIs and risk primitives; best consumed as protocol interface target (avoid forking internals). |
| [safe-global/safe-core-sdk](https://github.com/safe-global/safe-core-sdk) | 308 | MIT | Smart account/account-abstraction kits (`protocol-kit`, `api-kit`, `relay-kit`) for multisig policy wallets and sponsored txs (ERC-4337). |
| [coinbase/cdp-sdk](https://github.com/coinbase/cdp-sdk) | 147 | MIT | Custodied wallet lifecycle APIs (EVM+Solana), signing/transaction operations, managed private key workflow. |

### 1.3 Shared infrastructure, messaging, and key management

| Repo | Stars | License | Reusable components |
|---|---:|---|---|
| [nats-io/nats-server](https://github.com/nats-io/nats-server) | 19,168 | Apache-2.0 | High-throughput pub/sub, request-reply, JetStream persistence, durable consumers, event-driven service communication backbone. |
| [hashicorp/vault](https://github.com/hashicorp/vault) | 35,054 | BUSL-1.1 (v1.15+) | Secret storage, dynamic credentials, transit signing/encryption, key rotation policies, lease/revocation model for agent keys. |
| [LIT-Protocol/agent-wallet](https://github.com/LIT-Protocol/agent-wallet) | 51 | License not clearly exposed via GitHub API | Policy-constrained agent wallet architecture, tool registry model, prebuilt ERC20/uniswap/sign tools; README contains deprecation notice. |
| [LIT-Protocol/js-sdk](https://github.com/LIT-Protocol/js-sdk) | 158 | MIT | PKP/wrapped key primitives, access-control conditions, auth helpers, cryptographic and wallet-adjacent modules. |
| [tkhq/go-sdk](https://github.com/tkhq/go-sdk) | 14 | Apache-2.0 | Turnkey programmatic key operations (Go) for custody-style signing flows. |

### 1.4 Practical shortlist to standardize on

- **Agent orchestration default:** `langgraph`
- **Agent runtime adapters:** `eliza` (social/community agents), `uAgents` (decentralized messaging scenarios)
- **Wallet + tx stack:** `cdp-sdk` + `safe-core-sdk` (+ optional Lit adapter)
- **Onchain IO:** `viem/wagmi` as default contract/RPC integration layer
- **DeFi primitives:** `Uniswap sdk-core` (or new `Uniswap/sdks`) + Aave protocol interfaces
- **Infra:** `NATS` for event bus, `Vault` for secrets/signing key lifecycle
- **UI/rapid integration:** `thirdweb` + `scaffold-eth-2` patterns where frontend-heavy

---

## Step 2) Component reuse map across the 13 projects

### 2.1 Project set

- **Infrastructure:** `agent-wallet-sdk`, `zkml-verification`, `decentral-inference`, `agent-identity`
- **Apps:** `stablecoin-yield`, `trading-agent`, `treasury-manager`, `nl-defi-bot`, `prediction-market`
- **Verticals:** `nft-floor-agent`, `mev-agent`, `dao-governance`, `crosschain-bridge`

### 2.2 High-reuse components (needed by 3+ projects)

| Shared component | Projects using it | Reuse count |
|---|---|---:|
| Wallet management (create/sign/send) | agent-wallet-sdk, agent-identity, decentral-inference, stablecoin-yield, trading-agent, treasury-manager, nl-defi-bot, prediction-market, nft-floor-agent, mev-agent, dao-governance, crosschain-bridge | 12 |
| LLM inference gateway | decentral-inference, stablecoin-yield, trading-agent, treasury-manager, nl-defi-bot, prediction-market, nft-floor-agent, mev-agent, dao-governance, crosschain-bridge | 10 |
| On-chain data reading | agent-wallet-sdk, zkml-verification, agent-identity, stablecoin-yield, trading-agent, treasury-manager, nl-defi-bot, prediction-market, nft-floor-agent, mev-agent, dao-governance, crosschain-bridge | 12 |
| Transaction execution pipeline | agent-wallet-sdk, agent-identity, stablecoin-yield, trading-agent, treasury-manager, nl-defi-bot, prediction-market, nft-floor-agent, mev-agent, dao-governance, crosschain-bridge | 11 |
| Price feeds (cross-chain) | stablecoin-yield, trading-agent, treasury-manager, nl-defi-bot, prediction-market, nft-floor-agent, mev-agent, crosschain-bridge | 8 |
| DEX interaction (swap/liquidity) | stablecoin-yield, trading-agent, treasury-manager, nl-defi-bot, mev-agent, crosschain-bridge | 6 |
| Notification/alerting | agent-wallet-sdk, decentral-inference, stablecoin-yield, trading-agent, treasury-manager, nl-defi-bot, prediction-market, nft-floor-agent, mev-agent, dao-governance, crosschain-bridge | 11 |
| Monitoring/logging/tracing | all 13 projects | 13 |
| Key management + rotation | agent-wallet-sdk, agent-identity, decentral-inference, stablecoin-yield, trading-agent, treasury-manager, nl-defi-bot, prediction-market, nft-floor-agent, mev-agent, dao-governance, crosschain-bridge | 12 |
| Rate limiting + circuit breaker | all 13 projects | 13 |
| Backtesting/simulation | stablecoin-yield, trading-agent, nl-defi-bot, prediction-market, nft-floor-agent, mev-agent | 6 |
| Natural language intent parsing | stablecoin-yield, trading-agent, treasury-manager, nl-defi-bot, prediction-market, dao-governance | 6 |

**Conclusion:** these 12 modules should be first-class shared packages; they cover nearly every project.

---

## Step 3) Component library design (buildable, thin integration layer)

## 3.1 Package name + monorepo structure

**Proposed monorepo name:** `oyster-agent-components`  
**NPM scope:** `@oyster/*`  
**Build system:** `pnpm workspaces + turborepo` (TypeScript-first), with optional Python sidecar only for heavy backtesting.

```text
oyster-agent-components/
  package.json
  pnpm-workspace.yaml
  turbo.json
  tsconfig.base.json
  packages/
    core-types/                (@oyster/core-types)
    config/                    (@oyster/config)
    observability/             (@oyster/observability)
    resilience/                (@oyster/resilience)
    messaging-nats/            (@oyster/messaging-nats)

    keyring/                   (@oyster/keyring)
    wallet-core/               (@oyster/wallet-core)
    wallet-provider-cdp/       (@oyster/wallet-provider-cdp)
    wallet-provider-safe/      (@oyster/wallet-provider-safe)
    wallet-provider-lit/       (@oyster/wallet-provider-lit)

    chain-reader/              (@oyster/chain-reader)
    tx-executor/               (@oyster/tx-executor)
    price-feeds/               (@oyster/price-feeds)
    dex-uniswap/               (@oyster/dex-uniswap)
    lending-aave/              (@oyster/lending-aave)

    llm-gateway/               (@oyster/llm-gateway)
    intent-parser/             (@oyster/intent-parser)
    agent-runtime-langgraph/   (@oyster/agent-runtime-langgraph)
    agent-runtime-eliza/       (@oyster/agent-runtime-eliza)
    agent-runtime-uagents/     (@oyster/agent-runtime-uagents)

    identity/                  (@oyster/identity)
    notifier/                  (@oyster/notifier)
    backtest/                  (@oyster/backtest)

    presets/                   (@oyster/presets)  // opinionated bundles per project type
  examples/
    trading-agent/
    treasury-manager/
    dao-governance/
```

## 3.2 Wrap/extend vs build-from-scratch

| Capability | Wrap / Extend existing OSS | Build in-house (thin layer only) |
|---|---|---|
| Agent orchestration | `langgraph` | Graph templates for trading/treasury/governance workflows |
| Social/multi-agent runtime | `eliza` | Adapter to shared wallet/tx/alerts interfaces |
| Decentralized agent transport | `uAgents` | Adapter to shared message bus + policy engine |
| Wallet lifecycle | `cdp-sdk`, `safe-core-sdk`, optional `lit` | Unified `WalletProvider` interface + provider routing |
| Onchain reads/writes | `viem/wagmi` | Unified chain config, multicall batching, typed decoder utils |
| DEX | `Uniswap sdk-core` (+ router SDKs) | Chain-agnostic quote/swap facade |
| Lending | Aave interfaces (avoid forking core internals) | Simple `LendingProvider` facade |
| Messaging bus | NATS/JetStream | Topic taxonomy + typed event contracts |
| Secrets and key rotation | Vault (Transit + KV) | `KeyringProvider` abstraction, rotation policy hooks |
| LLM calls | Existing model SDKs | Unified retry/circuit-breaker + structured-output parser |
| Alerts | Telegram/Discord/email SDKs | Rules-based alert router |
| Backtesting | Existing data/quant libs where needed | Standardized strategy I/O + replay harness |

## 3.3 Interface definitions (TypeScript)

```ts
// @oyster/core-types
export type ChainId = number;
export type Address = `0x${string}`;

export interface TxRequest {
  chainId: ChainId;
  to: Address;
  data?: `0x${string}`;
  value?: bigint;
}

export interface TxReceipt {
  txHash: `0x${string}`;
  chainId: ChainId;
  status: "success" | "reverted";
  blockNumber: bigint;
}
```

```ts
// @oyster/wallet-core
export interface WalletProvider {
  id(): string;
  createWallet(input: { label: string; chainIds: ChainId[] }): Promise<{ walletId: string; addresses: Record<ChainId, Address> }>;
  getAddress(walletId: string, chainId: ChainId): Promise<Address>;
  signMessage(walletId: string, message: string): Promise<`0x${string}`>;
  signTx(walletId: string, tx: TxRequest): Promise<`0x${string}`>;
  sendTx(walletId: string, tx: TxRequest): Promise<{ txHash: `0x${string}` }>;
}
```

```ts
// @oyster/llm-gateway
export interface LLMGateway {
  complete<T>(input: {
    model: string;
    system: string;
    user: string;
    schema?: unknown; // zod/json-schema for structured output
  }): Promise<{ text: string; parsed?: T; usage?: { input: number; output: number } }>;
}

// @oyster/intent-parser
export interface ParsedIntent {
  intent: string;
  entities: Record<string, string | number | boolean>;
  confidence: number;
}
```

```ts
// @oyster/chain-reader + @oyster/tx-executor
export interface ChainReader {
  getNativeBalance(chainId: ChainId, address: Address): Promise<bigint>;
  readContract<T>(input: {
    chainId: ChainId;
    address: Address;
    abi: readonly unknown[];
    functionName: string;
    args?: readonly unknown[];
  }): Promise<T>;
  multicall(calls: Array<Parameters<ChainReader["readContract"]>[0]>): Promise<unknown[]>;
}

export interface TxExecutor {
  simulate(tx: TxRequest): Promise<{ success: boolean; gasEstimate: bigint; reason?: string }>;
  estimateFees(chainId: ChainId): Promise<{ maxFeePerGas: bigint; maxPriorityFeePerGas: bigint }>;
  submit(walletId: string, tx: TxRequest): Promise<{ txHash: `0x${string}` }>;
  wait(txHash: `0x${string}`, chainId: ChainId, timeoutMs?: number): Promise<TxReceipt>;
}
```

```ts
// @oyster/price-feeds + @oyster/dex-uniswap + @oyster/notifier
export interface PriceFeed {
  getSpot(pair: { base: Address; quote: Address; chainId: ChainId }): Promise<{ price: number; source: string; ts: number }>;
  getTwap(pair: { base: Address; quote: Address; chainId: ChainId }, windowSec: number): Promise<{ price: number; source: string; ts: number }>;
}

export interface DexProvider {
  quoteSwap(input: { chainId: ChainId; tokenIn: Address; tokenOut: Address; amountIn: bigint; slippageBps: number }): Promise<{ amountOut: bigint; route: string }>;
  buildSwapTx(input: { wallet: Address; quoteId: string }): Promise<TxRequest>;
}

export interface Notifier {
  send(channel: "telegram" | "discord" | "email", message: string, metadata?: Record<string, string>): Promise<void>;
}
```

```ts
// @oyster/keyring + @oyster/resilience + @oyster/backtest
export interface KeyringProvider {
  createKey(alias: string, policy?: Record<string, unknown>): Promise<{ keyId: string }>;
  signDigest(keyId: string, digestHex: `0x${string}`): Promise<`0x${string}`>;
  rotateKey(keyId: string): Promise<{ newKeyId: string }>;
}

export interface ResilienceGuard {
  run<T>(op: string, fn: () => Promise<T>, opts?: { timeoutMs?: number; retries?: number; circuit?: string }): Promise<T>;
}

export interface BacktestEngine {
  run(input: {
    strategyId: string;
    startTs: number;
    endTs: number;
    initialCapitalUsd: number;
  }): Promise<{ pnlUsd: number; sharpe: number; maxDrawdownPct: number; trades: number }>;
}
```

## 3.4 Dependency graph

```mermaid
graph TD
  A[@oyster/core-types] --> B[@oyster/config]
  A --> C[@oyster/observability]
  A --> D[@oyster/resilience]
  A --> E[@oyster/messaging-nats]

  B --> F[@oyster/keyring]
  C --> F
  D --> F

  F --> G[@oyster/wallet-core]
  G --> H[@oyster/wallet-provider-cdp]
  G --> I[@oyster/wallet-provider-safe]
  G --> J[@oyster/wallet-provider-lit]

  A --> K[@oyster/chain-reader]
  K --> L[@oyster/tx-executor]
  K --> M[@oyster/price-feeds]
  L --> N[@oyster/dex-uniswap]
  K --> O[@oyster/lending-aave]

  C --> P[@oyster/llm-gateway]
  D --> P
  P --> Q[@oyster/intent-parser]
  P --> R[@oyster/agent-runtime-langgraph]
  R --> S[@oyster/agent-runtime-eliza]
  R --> T[@oyster/agent-runtime-uagents]

  C --> U[@oyster/notifier]
  K --> V[@oyster/backtest]
  A --> W[@oyster/identity]

  R --> X[@oyster/presets]
  G --> X
  L --> X
  M --> X
  U --> X
```

## 3.5 How each of the 13 projects imports/uses the library

| Project | Main imports |
|---|---|
| `agent-wallet-sdk` | `@oyster/wallet-core`, `@oyster/wallet-provider-cdp`, `@oyster/wallet-provider-safe`, `@oyster/keyring`, `@oyster/tx-executor`, `@oyster/identity` |
| `zkml-verification` | `@oyster/chain-reader`, `@oyster/tx-executor`, `@oyster/identity`, `@oyster/observability`, `@oyster/resilience` |
| `decentral-inference` | `@oyster/llm-gateway`, `@oyster/agent-runtime-langgraph`, `@oyster/messaging-nats`, `@oyster/keyring`, `@oyster/observability` |
| `agent-identity` | `@oyster/identity`, `@oyster/keyring`, `@oyster/wallet-core`, `@oyster/messaging-nats` |
| `stablecoin-yield` | `@oyster/price-feeds`, `@oyster/lending-aave`, `@oyster/dex-uniswap`, `@oyster/tx-executor`, `@oyster/backtest`, `@oyster/notifier` |
| `trading-agent` | `@oyster/agent-runtime-langgraph`, `@oyster/intent-parser`, `@oyster/price-feeds`, `@oyster/dex-uniswap`, `@oyster/tx-executor`, `@oyster/backtest`, `@oyster/notifier` |
| `treasury-manager` | `@oyster/wallet-core`, `@oyster/keyring`, `@oyster/chain-reader`, `@oyster/price-feeds`, `@oyster/tx-executor`, `@oyster/notifier` |
| `nl-defi-bot` | `@oyster/llm-gateway`, `@oyster/intent-parser`, `@oyster/wallet-core`, `@oyster/dex-uniswap`, `@oyster/tx-executor`, `@oyster/notifier` |
| `prediction-market` | `@oyster/llm-gateway`, `@oyster/intent-parser`, `@oyster/chain-reader`, `@oyster/price-feeds`, `@oyster/tx-executor`, `@oyster/backtest` |
| `nft-floor-agent` | `@oyster/chain-reader`, `@oyster/price-feeds`, `@oyster/tx-executor`, `@oyster/notifier`, `@oyster/observability` |
| `mev-agent` | `@oyster/chain-reader`, `@oyster/price-feeds`, `@oyster/dex-uniswap`, `@oyster/tx-executor`, `@oyster/backtest`, `@oyster/messaging-nats` |
| `dao-governance` | `@oyster/identity`, `@oyster/intent-parser`, `@oyster/tx-executor`, `@oyster/notifier`, `@oyster/agent-runtime-langgraph` |
| `crosschain-bridge` | `@oyster/wallet-core`, `@oyster/chain-reader`, `@oyster/tx-executor`, `@oyster/price-feeds`, `@oyster/resilience`, `@oyster/notifier` |

### Example usage pattern (all projects)

```ts
import { createPreset } from "@oyster/presets";

const kit = await createPreset("trading-agent", {
  chains: [1, 8453, 42161],
  walletProvider: "cdp",
  keyring: "vault",
  llmModel: "gpt-4.1-mini",
});

const quote = await kit.dex.quoteSwap({
  chainId: 8453,
  tokenIn: "0x...",
  tokenOut: "0x...",
  amountIn: 1_000_000n,
  slippageBps: 30,
});
```

---

## Implementation sequencing (practical rollout)

1. **Phase 1 (foundational, 2-3 weeks):** `core-types`, `config`, `observability`, `resilience`, `messaging-nats`, `keyring(Vault)`.
2. **Phase 2 (web3 core, 3-4 weeks):** `wallet-core + providers`, `chain-reader`, `tx-executor`, `price-feeds`, `dex-uniswap`, `notifier`.
3. **Phase 3 (agent intelligence, 2-3 weeks):** `llm-gateway`, `intent-parser`, `agent-runtime-langgraph`, `backtest`, `presets` for all 13 projects.

---

## Notes / risk controls

- `Uniswap/sdk-core` and `aave/aave-v3-core` READMEs indicate migration/deprecation concerns; consume as interfaces/primitives, avoid deep forks.
- `aave/aave-v3-core` and `hashicorp/vault` use BUSL terms; verify compliance before embedding modified source.
- `LIT-Protocol/agent-wallet` has deprecation notice + unclear license exposure from GitHub API; treat as optional reference implementation unless licensing is clarified.
