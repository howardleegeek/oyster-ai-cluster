# Oyster Labs Web3 AI Agent Unified Architecture

> Version: 1.0 | Date: 2026-02-18
> Author: Architect Agent (Opus)
> Status: DRAFT - Awaiting Howard review

---

## 1. Executive Summary

This document defines a unified technical architecture for 13 AI Agent + Web3 projects that share infrastructure while remaining independently deployable. The architecture is designed around three fundamental constraints:

1. **CAP Theorem** - Financial agents demand consistency for transactions but can tolerate eventual consistency for analytics
2. **Blast Radius Containment** - A bug in one agent must not drain wallets belonging to another
3. **Zero Marginal Cost** - Every shared service must justify itself by reducing per-project cost to near zero

---

## 2. System Architecture Diagram

```
                          OYSTER LABS WEB3 AI AGENT PLATFORM
 ============================================================================

                              +------------------+
                              |  Howard / Opus   |
                              |  (Direction)     |
                              +--------+---------+
                                       |
                              +--------v---------+
                              |  Dispatch v5     |
                              |  (DAG Scheduler) |
                              +--------+---------+
                                       |
 ============================================================================
  SHARED SERVICES LAYER (runs on oci-paid-1 + oci-paid-3)
 ============================================================================
  |                    |                   |                    |
  v                    v                   v                    v
+----------+   +-------------+   +----------------+   +---------------+
| Vault    |   | LLM Gateway |   | Event Bus      |   | TX Executor   |
| (Keys)   |   | (Router)    |   | (NATS/Redis)   |   | (Sequencer)   |
+----------+   +-------------+   +----------------+   +---------------+
  |                    |                   |                    |
  | +------------------+-------------------+--------------------+
  | |
  v v
+--------------------------------------------------------------------------+
|                        AGENT RUNTIME MESH                                 |
|                                                                           |
|  +------------------+  +------------------+  +------------------+         |
|  | agent-wallet-sdk |  | decentral-infer  |  | agent-identity   |         |
|  | (TS library)     |  | (Python svc)     |  | (Python svc)     |         |
|  +------------------+  +------------------+  +------------------+         |
|  +------------------+                                                     |
|  | zkml-verify      |   <-- These 4 are LIBRARIES/SERVICES               |
|  | (Rust svc)       |       consumed by the 9 application agents          |
|  +------------------+                                                     |
|                                                                           |
|  APPLICATION AGENTS (each is an independent container/process):           |
|                                                                           |
|  +---------------+ +---------------+ +---------------+ +---------------+  |
|  | stablecoin-   | | trading-      | | treasury-     | | nl-defi-bot  |  |
|  | yield (Sol)   | | agent (Py)    | | manager (TS)  | | (Py+TG)     |  |
|  +---------------+ +---------------+ +---------------+ +---------------+  |
|  +---------------+ +---------------+ +---------------+ +---------------+  |
|  | prediction-   | | nft-floor-    | | mev-agent     | | dao-         |  |
|  | market (Py)   | | agent (TS)    | | (Go)          | | governance   |  |
|  +---------------+ +---------------+ +---------------+ +---------------+  |
|  +---------------+                                                        |
|  | crosschain-   |                                                        |
|  | bridge (TS)   |                                                        |
|  +---------------+                                                        |
+--------------------------------------------------------------------------+
                                       |
                              +--------v---------+
                              | Monitoring Stack |
                              | Prometheus+Graf  |
                              | + Alert Manager  |
                              +------------------+
```

---

## 3. Shared vs. Project-Specific Components

### 3.1 Shared Components (build once, used by all 13)

| Component | Tech Choice | Why Shared | Deployment |
|-----------|------------|------------|------------|
| **Key Vault** | HashiCorp Vault OSS (or age-encrypted file vault) | Every agent needs private keys. Centralized = single audit point | oci-paid-1 (primary) + oci-paid-3 (replica) |
| **LLM Gateway** | FastAPI proxy -> MiniMax/GLM free APIs | Route all LLM calls through one endpoint. Rate limit, cache, fallback | oci-paid-1 |
| **Event Bus** | NATS JetStream (or Redis Streams as simpler alt) | Agents need to communicate: "price alert", "tx confirmed", "rebalance" | oci-paid-3 |
| **TX Executor** | Python FastAPI service with nonce management | Centralized nonce tracking prevents double-spend, enables batching | oci-paid-1 |
| **Monitoring** | Prometheus + Grafana + custom alerter | Unified dashboard for all 13 agents | oci-micro-1 |
| **Shared DB** | PostgreSQL 16 (one instance, 13 schemas) | Connection pooling, backup, single ops burden | oci-paid-3 |
| **RPC Pool** | JSON-RPC load balancer across free/paid endpoints | Avoid rate limits on any single RPC provider | Sidecar on oci-paid-1 |

### 3.2 Infrastructure Libraries (imported, not deployed as services)

| Library | Language | Consumers | What It Provides |
|---------|----------|-----------|------------------|
| **agent-wallet-sdk** | TypeScript | 8 of 13 projects | Wallet creation, spending limits, allowlists, gas estimation |
| **zkml-verification** | Rust (with FFI bindings) | 4 of 13 projects | Generate/verify ZK proofs for AI model outputs |
| **agent-identity** | Python | All 13 projects | On-chain DID registration, reputation scoring, agent auth |
| **decentral-inference** | Python | All 13 projects | LLM inference with verifiable compute receipts |

### 3.3 Project-Specific (NOT shared)

| Concern | Why Per-Project |
|---------|-----------------|
| Trading strategies | Proprietary logic, different risk profiles |
| UI / Telegram bots | Each has unique user interaction |
| Smart contracts (Solidity) | Different chains, different upgrade patterns |
| ML models | Domain-specific training data |

---

## 4. Deployment Architecture

### 4.1 Node Inventory (actual from nodes.json)

| Node | Slots | vCPU/RAM (est.) | Role |
|------|-------|-----------------|------|
| oci-paid-1 | 40 | 8 vCPU / 24GB | **Platform Core**: Vault, LLM GW, TX Executor, RPC Pool |
| oci-paid-3 | 48 | 8 vCPU / 24GB | **Data + Events**: PostgreSQL, NATS, Event Bus, Monitoring |
| oci-arm-1 | 12 | 4 vCPU / 24GB (ARM) | **DeFi Agents**: trading-agent, stablecoin-yield, prediction-market |
| codex-node-1 | 8 | 2 vCPU / 8GB | **TS Agents**: nft-floor-agent, treasury-manager, crosschain-bridge |
| glm-node-2 | 8 | 2 vCPU / 8GB | **Governance**: dao-governance, agent-identity svc |
| glm-node-3 | 8 | 2 vCPU / 8GB | **MEV + Infra**: mev-agent (Go), zkml-verification svc |
| glm-node-4 | 8 | 2 vCPU / 8GB | **Consumer**: nl-defi-bot, decentral-inference svc |
| mac2 | 8 | M-series / 16GB | **Dev/Staging**: development builds, integration tests |
| oci-micro-1 | 0 (monitoring) | 1 vCPU / 1GB | **Monitoring**: Prometheus, Grafana, alerter |
| oci-micro-2 | 0 (monitoring) | 1 vCPU / 1GB | **Log aggregation**: Loki (optional) |

### 4.2 Per-Node Deployment Map

```
oci-paid-1 (Platform Core)
  [systemd] vault-server          -- HashiCorp Vault / age-vault
  [systemd] llm-gateway           -- FastAPI, port 8090
  [systemd] tx-executor           -- FastAPI, port 8091
  [systemd] rpc-pool              -- JSON-RPC LB, port 8545
  [container] stablecoin-yield    -- Solidity + keeper bot (Python)

oci-paid-3 (Data + Events)
  [systemd] postgresql-16         -- Schemas: shared + per-project
  [systemd] nats-server           -- JetStream enabled, port 4222
  [systemd] redis                 -- Cache + session, port 6379
  [container] trading-agent       -- Python, connects to NATS + PG
  [container] prediction-market   -- Python, connects to NATS + PG

oci-arm-1 (DeFi Cluster)
  [container] trading-agent-2     -- Second instance for redundancy
  [container] stablecoin-yield-2  -- Keeper redundancy
  [container] decentral-inference -- Python svc, port 8092

codex-node-1 (TypeScript Cluster)
  [pm2] nft-floor-agent           -- TS/Node.js
  [pm2] treasury-manager          -- TS/Node.js
  [pm2] crosschain-bridge         -- TS/Node.js

glm-node-2 (Governance)
  [pm2] dao-governance            -- TS/Node.js
  [systemd] agent-identity-svc    -- Python FastAPI, port 8093

glm-node-3 (MEV + ZK)
  [systemd] mev-agent             -- Go binary
  [systemd] zkml-verification-svc -- Rust binary, port 8094

glm-node-4 (Consumer)
  [systemd] nl-defi-bot           -- Python + Telegram bot
  [systemd] decentral-infer-2     -- Inference redundancy

mac2 (Dev/Staging)
  [docker-compose] full-stack-dev -- All 13 services in dev mode
  [cron] integration-tests        -- Nightly test suite
```

### 4.3 Container Strategy

We use **systemd + venv** for Python/Go/Rust services (no Docker overhead on small VMs) and **pm2** for Node.js/TypeScript services. Docker is reserved for the dev environment on mac2 where we need reproducibility.

Rationale: The OCI free-tier and small paid instances have limited RAM. Docker overhead (100-200MB per container) adds up across 13 projects. Native processes with systemd supervision are lighter and sufficient for single-tenant VMs connected via Tailscale.

```
Runtime Decision Matrix:
  Python  --> systemd + venv + uvicorn
  TS/Node --> pm2 ecosystem
  Go      --> systemd + static binary
  Rust    --> systemd + static binary
  Solidity--> Hardhat for deploy; keeper bots are Python
```

---

## 5. Data Architecture

### 5.1 Database Strategy

One PostgreSQL 16 instance on oci-paid-3, with **schema-per-project** isolation:

```sql
-- Shared schemas
CREATE SCHEMA shared_wallet;    -- Wallet balances, tx history (all agents)
CREATE SCHEMA shared_identity;  -- Agent DIDs, reputation scores
CREATE SCHEMA shared_market;    -- Price feeds, market data cache

-- Per-project schemas
CREATE SCHEMA s_stablecoin_yield;
CREATE SCHEMA s_trading_agent;
CREATE SCHEMA s_treasury_manager;
CREATE SCHEMA s_nl_defi_bot;
CREATE SCHEMA s_prediction_market;
CREATE SCHEMA s_nft_floor_agent;
CREATE SCHEMA s_mev_agent;
CREATE SCHEMA s_dao_governance;
CREATE SCHEMA s_crosschain_bridge;
```

**Why one instance, not 13:**
- Connection pooling (PgBouncer) serves all 13 with ~50 total connections
- Single backup/restore procedure
- Cross-schema joins when needed (e.g., "show all agent wallet balances")
- PostgreSQL schemas provide strong isolation without operational overhead

### 5.2 Inter-Agent Communication

```
Communication Patterns:
 ============================================================================

 Pattern 1: EVENT-DRIVEN (async, decoupled)
 ──────────────────────────────────────────
   trading-agent  --[price.alert.ETH]--> NATS --> stablecoin-yield
   trading-agent  --[arb.opportunity]---> NATS --> mev-agent
   prediction-mkt --[outcome.resolved]--> NATS --> dao-governance

 Pattern 2: REQUEST-RESPONSE (sync, through shared services)
 ──────────────────────────────────────────────────────────────
   any-agent --[POST /tx/execute]--> TX Executor --[broadcast]--> Chain
   any-agent --[POST /llm/chat]---> LLM Gateway --[route]------> MiniMax/GLM
   any-agent --[GET /vault/key]---> Key Vault   --[response]---> Agent

 Pattern 3: SHARED STATE (via PostgreSQL)
 ──────────────────────────────────────────
   all-agents --> shared_wallet schema (read wallet balances)
   all-agents --> shared_market schema (read cached price feeds)

 Pattern 4: DIRECT P2P (rare, latency-critical only)
 ──────────────────────────────────────────────────────
   mev-agent <--> trading-agent  (gRPC over Tailscale, <10ms)
```

### 5.3 NATS Subject Hierarchy

```
oyster.price.{chain}.{token}         -- Price updates
oyster.tx.{agent}.submitted          -- TX submitted
oyster.tx.{agent}.confirmed          -- TX confirmed
oyster.tx.{agent}.failed             -- TX failed
oyster.alert.{agent}.{severity}      -- Operational alerts
oyster.rebalance.{vault}.trigger     -- Rebalance signals
oyster.governance.{dao}.proposal     -- New proposals
oyster.governance.{dao}.vote         -- Vote cast
oyster.bridge.{src}.{dst}.request    -- Cross-chain requests
oyster.nft.{collection}.floor        -- Floor price changes
oyster.mev.{chain}.opportunity       -- MEV opportunities
```

---

## 6. Security Architecture

### 6.1 Threat Model

```
THREAT                          MITIGATION
────────────────────────────────────────────────────────────────
Private key theft               Vault with seal/unseal + audit log
Agent compromise drains funds   Per-agent spending limits (daily/tx)
Rogue agent transaction         TX Executor allowlist per agent
Cross-agent contamination       Schema isolation + NATS ACLs
RPC endpoint compromise         RPC pool with multiple providers
MEV extraction front-running    Private mempool (Flashbots Protect)
Smart contract exploit          Timelocked upgrades + multisig
LLM prompt injection -> tx      TX Executor validates against rules
```

### 6.2 Key Management Model

```
                    +-------------------+
                    | Master Key (HSM)  |  <-- Howard's hardware key
                    | Offline, air-gap  |
                    +--------+----------+
                             |
                    +--------v----------+
                    | Vault Server      |  <-- oci-paid-1, sealed at rest
                    | Auto-unseal via   |
                    | OCI KMS           |
                    +--------+----------+
                             |
              +--------------+--------------+
              |              |              |
     +--------v---+  +------v-----+  +-----v------+
     | Agent Key 1|  | Agent Key 2|  | Agent Key N|
     | (derived)  |  | (derived)  |  | (derived)  |
     | Limits:    |  | Limits:    |  | Limits:    |
     | $100/day   |  | $500/day   |  | $50/tx     |
     +------------+  +------------+  +------------+

Key Hierarchy:
  L0: Master (offline, only for emergency recovery)
  L1: Hot Vault (Vault server, auto-unsealed, audit-logged)
  L2: Agent Keys (derived HD wallets, spending-limited)
  L3: Session Keys (ephemeral, per-operation, auto-expire)
```

### 6.3 TX Executor Security Rules

```python
# Pseudocode for TX Executor validation
class TxExecutor:
    RULES = {
        "stablecoin-yield":  {"max_tx_usd": 10000, "max_daily_usd": 50000,
                               "allowed_contracts": ["aave_v3", "compound_v3"]},
        "trading-agent":     {"max_tx_usd": 5000,  "max_daily_usd": 25000,
                               "allowed_dexes": ["uniswap_v3", "curve"]},
        "mev-agent":         {"max_tx_usd": 2000,  "max_daily_usd": 10000,
                               "allowed_methods": ["backrun", "sandwich_protect"]},
        "treasury-manager":  {"max_tx_usd": 50000, "max_daily_usd": 200000,
                               "requires_multisig": True,
                               "timelock_hours": 24},
        "nft-floor-agent":   {"max_tx_usd": 1000,  "max_daily_usd": 5000},
        "crosschain-bridge": {"max_tx_usd": 5000,  "max_daily_usd": 20000,
                               "allowed_bridges": ["lifi", "stargate"]},
        # ... remaining agents
    }

    def validate(self, agent_id, tx):
        rules = self.RULES[agent_id]
        assert tx.value_usd <= rules["max_tx_usd"]
        assert self.daily_spent(agent_id) + tx.value_usd <= rules["max_daily_usd"]
        if rules.get("requires_multisig"):
            assert tx.has_multisig_approval()
        # Log everything to audit table
        self.audit_log(agent_id, tx, "APPROVED")
```

### 6.4 Network Security

```
All inter-node communication: Tailscale mesh (WireGuard)
  - Every node is on the same Tailnet
  - No public ports except:
    - nl-defi-bot: Telegram webhook (443, behind Cloudflare)
    - monitoring: Grafana (3000, Tailscale-only)

Firewall rules (per-node iptables):
  ALLOW: Tailscale subnet (100.x.x.x/8)
  ALLOW: established connections
  DROP:  everything else inbound
```

---

## 7. Cost Architecture

### 7.1 Monthly Cost Estimate

```
INFRASTRUCTURE COSTS (Monthly)
 ============================================================================

 FREE TIER (OCI Always Free + existing)
 ──────────────────────────────────────
 oci-arm-1          ARM A1 (4 OCPU/24GB)     $0    OCI Always Free
 oci-micro-1        AMD E2.1 Micro            $0    OCI Always Free
 oci-micro-2        AMD E2.1 Micro            $0    OCI Always Free
 Tailscale          100 devices               $0    Personal plan
 MiniMax API        LLM inference             $0    Free tier
 GLM API            LLM inference             $0    Free tier
 GitHub             Private repos             $0    Free for private
 Vercel             Frontend hosting          $0    Hobby plan

 PAID (Existing, already running)
 ──────────────────────────────────────
 oci-paid-1         8 vCPU / 24GB             ~$65  OCI Flex
 oci-paid-3         8 vCPU / 24GB             ~$65  OCI Flex
 codex-node-1       GCP e2-standard-2         ~$50  GCP
 glm-node-2         GCP e2-standard-2         ~$50  GCP
 glm-node-3         GCP e2-standard-2         ~$50  GCP
 glm-node-4         GCP e2-standard-2         ~$50  GCP

 NEW COSTS (for this architecture)
 ──────────────────────────────────────
 PostgreSQL         Runs on oci-paid-3         $0   Self-hosted
 NATS               Runs on oci-paid-3         $0   Self-hosted
 Redis              Runs on oci-paid-3         $0   Self-hosted
 Vault              Runs on oci-paid-1         $0   Self-hosted OSS
 RPC endpoints      Alchemy/Infura free tier   $0   Free (25M compute/mo)
 Backup storage     OCI Object Storage 10GB    $0   OCI free tier
 Domain/TLS         Cloudflare                 $0   Free plan

 ──────────────────────────────────────
 TOTAL MONTHLY                               ~$330
 Per-project average                         ~$25/project/month
 ============================================================================

 WHAT WOULD COST MORE WITHOUT THIS ARCHITECTURE:
 13 separate DB instances (RDS)              ~$195/mo
 13 separate key management (KMS)            ~$130/mo
 13 separate monitoring stacks               ~$65/mo
 Separate RPC plans per project              ~$100/mo
 ──────────────────────────────────────────────────
 SAVINGS FROM SHARED ARCHITECTURE:           ~$490/mo
```

### 7.2 RPC Cost Optimization

```
Free RPC Strategy:
  1. Alchemy     -- 300M compute units/mo free --> ~10M requests
  2. Infura      -- 100K requests/day free     --> ~3M/mo
  3. QuickNode   -- 50M API credits free       --> ~5M requests
  4. Ankr        -- Public RPCs (no key needed) --> Unlimited (slower)

  Load balancer rotates across all 4, with Ankr as fallback.
  Estimated need: ~2M requests/mo across all 13 agents.
  Well within free tier.
```

---

## 8. Implementation Order

### Phase 0: Foundation (Week 1-2) -- SHARED SERVICES

```
Priority: CRITICAL -- Nothing else works without these

  [P] = Parallelizable

  S01: Vault setup on oci-paid-1                        2 days
       - Install Vault OSS, configure auto-unseal
       - Create 13 agent key paths
       - Set spending limit policies

  S02: PostgreSQL + schemas on oci-paid-3               1 day
       - Install PG 16, create all schemas
       - PgBouncer for connection pooling
       - Backup cron to OCI Object Storage

  S03: NATS JetStream on oci-paid-3                     1 day  [P with S02]
       - Install NATS, enable JetStream
       - Create subject ACLs per agent
       - Retention policy: 7 days

  S04: LLM Gateway on oci-paid-1                        2 days [P with S02]
       - FastAPI service routing to MiniMax/GLM
       - Request caching (Redis)
       - Rate limiting per agent
       - Fallback chain: MiniMax -> GLM -> queue

  S05: TX Executor on oci-paid-1                        3 days
       - Nonce manager (per-chain, per-wallet)
       - Spending limit enforcement
       - Audit log to PostgreSQL
       - Gas price oracle integration

  S06: RPC Pool on oci-paid-1                           1 day  [P with S05]
       - nginx/HAProxy load balancer
       - Health checks per provider
       - Automatic failover

  S07: Monitoring stack on oci-micro-1                  1 day  [P]
       - Prometheus + node_exporter on all nodes
       - Grafana dashboards
       - Alert rules -> Discord webhook
```

### Phase 1: Infrastructure Libraries (Week 2-3)

```
  S08: agent-wallet-sdk (TS)                            5 days
       - Fork coinbase/agentkit
       - Integrate with Vault for key storage
       - Spending limit middleware
       - Unit tests + integration tests with testnet

  S09: agent-identity (Python)                          4 days [P with S08]
       - Fork fetchai/uAgents
       - On-chain DID registration (ERC-725)
       - Reputation scoring model
       - NATS event publisher for identity changes

  S10: decentral-inference (Python)                     4 days [P with S08]
       - Fork ritual-net/infernet-node
       - Integrate with LLM Gateway
       - Verifiable compute receipts
       - Benchmark: latency, throughput

  S11: zkml-verification (Rust)                         5 days
       - Fork zkonduit/ezkl
       - Build FFI bindings for Python + Node.js
       - Circuit compilation pipeline
       - Proof generation benchmarks on oci-arm-1
```

### Phase 2: High-Value Application Agents (Week 3-5)

```
  S12: stablecoin-yield (Solidity + Python)             7 days
       - Fork yearn/yearn-vaults-v3
       - Custom strategy: Aave/Compound auto-rebalance
       - Keeper bot integrates TX Executor
       - Testnet deployment + simulation

  S13: trading-agent (Python)                           7 days [P with S12]
       - Fork hummingbot/hummingbot
       - Strategy: simple market making + arb
       - Integrates: Vault, TX Executor, NATS
       - Paper trading mode first

  S14: nl-defi-bot (Python)                             5 days [P with S12]
       - Fork web3-ethereum-defi
       - Telegram bot + LLM Gateway for NL parsing
       - Commands: swap, check balance, yield status
       - This is the USER INTERFACE for non-technical users

  S15: treasury-manager (TS)                            5 days
       - Fork safe-fndn/safe-smart-account
       - Multisig integration
       - Reporting dashboard (simple React)
       - Timelock enforcement via TX Executor
```

### Phase 3: Vertical Agents (Week 5-7)

```
  S16: prediction-market (Python)                       5 days
  S17: nft-floor-agent (TS)                             4 days [P with S16]
  S18: mev-agent (Go)                                   5 days [P with S16]
  S19: dao-governance (TS)                              4 days
  S20: crosschain-bridge (TS)                           5 days [P with S19]
```

### Phase 4: Hardening (Week 7-8)

```
  S21: End-to-end integration tests                     3 days
  S22: Load testing (simulated market conditions)       2 days
  S23: Security audit (smart contracts + key flows)     3 days
  S24: Runbook documentation                            2 days
  S25: Mainnet deployment (graduated rollout)           3 days
```

---

## 9. Shared Service API Contracts

### 9.1 LLM Gateway API

```
POST /llm/chat
{
  "agent_id": "trading-agent",
  "model": "minimax",          // or "glm", or "auto" for routing
  "messages": [...],
  "max_tokens": 1000,
  "temperature": 0.3
}

Response:
{
  "id": "req_xxx",
  "content": "...",
  "model_used": "minimax",
  "tokens_used": 450,
  "latency_ms": 1200,
  "cached": false
}
```

### 9.2 TX Executor API

```
POST /tx/execute
{
  "agent_id": "stablecoin-yield",
  "chain": "ethereum",
  "to": "0xAaveV3Pool...",
  "data": "0x...",
  "value_usd": 5000,
  "gas_strategy": "medium",    // fast/medium/slow
  "idempotency_key": "yield-rebalance-2026-02-18-001"
}

Response:
{
  "tx_hash": "0x...",
  "status": "submitted",       // submitted/confirmed/failed
  "nonce": 42,
  "gas_used": 150000,
  "block_number": null         // null until confirmed
}

GET /tx/status/{tx_hash}
{
  "tx_hash": "0x...",
  "status": "confirmed",
  "block_number": 19234567,
  "gas_used": 148000,
  "effective_gas_price": "15 gwei"
}
```

### 9.3 Vault API

```
POST /vault/sign
{
  "agent_id": "trading-agent",
  "chain": "ethereum",
  "tx_data": "0x...",          // unsigned tx bytes
  "session_token": "sess_xxx"  // ephemeral, from agent auth
}

Response:
{
  "signed_tx": "0x...",
  "signer_address": "0xAgentWallet...",
  "audit_id": "aud_xxx"
}

GET /vault/balance/{agent_id}
{
  "agent_id": "trading-agent",
  "wallets": [
    {"chain": "ethereum", "address": "0x...", "balance_usd": 12500},
    {"chain": "arbitrum", "address": "0x...", "balance_usd": 3200}
  ],
  "daily_spent_usd": 1500,
  "daily_limit_usd": 25000
}
```

---

## 10. Architectural Decision Records (ADRs)

### ADR-001: Schema-per-project over Database-per-project
- **Decision**: One PostgreSQL instance with 13+ schemas
- **Rationale**: OCI free/cheap VMs cannot run 13 PG instances. Schema isolation is sufficient for non-adversarial multi-tenant (we own all agents). Cross-schema queries enable portfolio-level analytics.
- **Risk**: Schema migration complexity. Mitigated by Alembic with per-schema migration paths.

### ADR-002: NATS over Kafka
- **Decision**: NATS JetStream
- **Rationale**: Kafka requires 3+ brokers minimum (6GB+ RAM). NATS runs in a single 50MB binary. Our message volume (est. 10K msg/hour) does not need Kafka's throughput. NATS JetStream provides at-least-once delivery which is sufficient.
- **Risk**: No built-in exactly-once. Mitigated by idempotency keys in TX Executor.

### ADR-003: Systemd over Kubernetes
- **Decision**: systemd + pm2 for process management
- **Rationale**: K8s control plane needs 2-4GB RAM minimum. Our nodes are 2-8 vCPU. The operational complexity of K8s on 8 heterogeneous nodes (ARM + x86, different OSes) outweighs benefits for 13 services. systemd is universal, battle-tested, and already present.
- **Risk**: No auto-scaling. Mitigated by: (a) our load is predictable, (b) horizontal scale = add another node with bootstrap.sh.

### ADR-004: Centralized TX Executor over per-agent signing
- **Decision**: All on-chain transactions go through one TX Executor
- **Rationale**: Nonce management across 13 agents on multiple chains is the #1 operational hazard. Centralized nonce tracking with idempotency prevents the most common failure mode (stuck transactions from nonce gaps). Also enables spending limits and audit trail.
- **Risk**: Single point of failure. Mitigated by: (a) TX Executor runs on two nodes (primary + standby), (b) agents can fall back to direct signing for emergency withdrawals only.

### ADR-005: Free LLM APIs as primary, no paid backup
- **Decision**: MiniMax and GLM free tiers only
- **Rationale**: Monthly cost of OpenAI/Anthropic for 13 agents would be $500-2000/mo. Free APIs provide sufficient quality for DeFi decision-making (which is rule-based with LLM augmentation, not LLM-dependent). LLM Gateway enables seamless provider switching if free tier degrades.
- **Risk**: Free API instability. Mitigated by: (a) response caching reduces API calls 60%, (b) fallback chain, (c) critical paths (TX execution) do not depend on LLM.

---

## 11. Failure Modes and Recovery

```
FAILURE                          DETECTION            RECOVERY
─────────────────────────────────────────────────────────────────
Vault server down                Health check 10s     Auto-restart (systemd)
                                                      Agents queue tx locally
                                                      Alert -> Howard

PostgreSQL down                  Health check 10s     Auto-restart
                                                      Agents use local cache
                                                      WAL replay on restart

NATS down                        Health check 10s     Auto-restart
                                                      Agents retry with backoff
                                                      No data loss (JetStream)

TX Executor down                 Health check 10s     Failover to standby
                                                      Pending TXs in PG queue

RPC provider down                Health check 30s     Auto-failover to next
                                                      4-provider rotation

Agent process crash              systemd/pm2          Auto-restart <5s
                                                      State recovered from PG

Node unreachable                 Tailscale ping 30s   Alert -> Howard
                                                      Redistribute workload

Smart contract exploit           On-chain monitoring  Circuit breaker in TX Exec
                                                      Freeze agent keys in Vault
                                                      Alert -> Howard IMMEDIATELY
```

---

## 12. Monorepo vs. Polyrepo Decision

**Decision: Polyrepo with shared package registry**

Each of the 13 projects remains its own Git repo (already configured in projects.json). Shared libraries are published as packages:

```
agent-wallet-sdk   --> npm private registry (GitHub Packages)
agent-identity     --> PyPI private registry (GitHub Packages)
decentral-inference --> PyPI private registry (GitHub Packages)
zkml-verification  --> Cargo private registry + npm (via NAPI-RS)
```

Shared API contracts are defined in a new repo:

```
oyster-contracts/
  schemas/
    llm-gateway.openapi.yaml
    tx-executor.openapi.yaml
    vault.openapi.yaml
    nats-subjects.yaml
  protos/
    mev-trading.proto          # gRPC for latency-critical path
```

---

## 13. Constitutional Principles

These are immutable rules that govern all implementation decisions:

1. **No agent may sign transactions without TX Executor validation** -- Even if an agent holds its own key, all outbound transactions must pass through spending limits and audit logging.

2. **Keys at rest are always encrypted** -- No private key may exist in plaintext on disk, in environment variables, or in application memory longer than the signing operation.

3. **Blast radius is bounded** -- A compromised agent can lose at most its daily spending limit. No agent has access to another agent's keys or data.

4. **All state is recoverable** -- Every agent must be able to restart from PostgreSQL state alone, with no local state dependencies.

5. **Free before paid** -- Any service selection must exhaust free-tier options before considering paid alternatives. Paid services require Howard's explicit approval.

6. **Testnet before mainnet** -- No smart contract deployment to mainnet without 7 days of testnet operation and at least 1000 simulated transactions.

7. **Observable by default** -- Every service exposes Prometheus metrics. Every transaction is audit-logged. Silence is a bug.

---

## 14. Development Workflow Integration

This architecture integrates with the existing dispatch system:

```
Existing Flow:
  Howard -> Opus (direction) -> MiniMax (spec) -> dispatch.py -> 140 agent slots

Web3 Agent Development:
  Same flow, but specs reference shared service APIs:

  spec example:
    ---
    task_id: S12-stablecoin-yield-keeper
    project: stablecoin-yield
    depends_on: [S01-vault, S05-tx-executor]
    modifies: ["src/keeper.py", "src/strategies/aave_v3.py"]
    ---
    ## Objective
    Implement keeper bot that monitors Aave V3 positions and rebalances
    when utilization rate exceeds 80%.

    ## Shared Service Integration
    - TX Executor: POST /tx/execute for all rebalance transactions
    - Vault: POST /vault/sign for transaction signing
    - NATS: Publish to oyster.rebalance.aave.trigger on rebalance
    - LLM Gateway: POST /llm/chat for strategy reasoning (optional)

    ## Constraints
    - Max $10,000 per rebalance transaction
    - Max 3 rebalances per day
    - Must work on Ethereum mainnet + Arbitrum
```

---

## 15. Summary Table

| Dimension | Decision | Justification |
|-----------|----------|---------------|
| Orchestration | systemd + pm2 | Lightweight, universal, no K8s overhead |
| Database | PostgreSQL (schema-per-project) | Single ops burden, cross-agent queries |
| Messaging | NATS JetStream | 50MB binary, at-least-once, sufficient throughput |
| Key Management | Vault OSS (self-hosted) | Free, auditable, policy-driven |
| LLM Inference | LLM Gateway -> MiniMax/GLM | Free APIs, cached, fallback chain |
| TX Execution | Centralized TX Executor | Nonce safety, spending limits, audit |
| Networking | Tailscale mesh | Zero-config WireGuard, free tier |
| Monitoring | Prometheus + Grafana | Industry standard, self-hosted, free |
| RPC | Multi-provider load balancer | Free tier rotation across 4 providers |
| CI/CD | dispatch.py (existing) | Already proven with 140 agent slots |
| Repos | Polyrepo + shared packages | Independence + shared contracts |
| Cost | ~$330/month total | 75% runs on free tier |
