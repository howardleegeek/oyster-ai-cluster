# x402 Hackathon — ClawVision Submission Spec
## "Pay-Per-Query Real World: AI Agents Buy Spatial Intelligence via x402"

> Hackathon: SF Agentic Commerce x402 (Feb 11-13, 2026)
> Prize pool: $50K | Partners: Coinbase, Google, SKALE, Virtuals, Vodafone
> Submission: Dorahacks (online accepted)

---

## 1. Pitch (30 seconds)

**"What if an AI agent could pay $0.01 to see what's happening at any location on Earth, right now?"**

ClawVision has 30K+ phones continuously capturing the real world at 1fps. We wrap our `world.query()` API with x402 payment headers — so any AI agent can autonomously pay for real-time spatial intelligence. No API key signup. No invoices. Just HTTP 402 → pay → get data.

---

## 2. Demo Concept

### Flow
```
AI Agent (GPT/Claude/Virtuals)
    │
    ├─ GET /v1/world/cells?lat=37.77&lon=-122.41&radius=500
    │   → HTTP 402 Payment Required
    │   → x-payment-required: 100 (100 credits = $0.01)
    │
    ├─ Agent auto-pays via x402 (USDC on SKALE = gasless)
    │
    └─ 200 OK → { cells: [...], events: [...], freshness: "2min ago" }
```

### What the Demo Shows
1. **Agent gets blocked** — 402 response with price quote
2. **Agent pays** — x402 USDC micro-payment (gasless on SKALE)
3. **Agent gets data** — real-time spatial events from ClawVision network
4. **Agent reasons** — uses spatial data to answer user question
5. **Dashboard** — shows payments flowing in real-time

---

## 3. Tech Stack

| Component | Technology | Role |
|-----------|-----------|------|
| **Payment layer** | x402 (Coinbase) | HTTP-native payments |
| **Chain** | SKALE (gasless) | Zero gas fees for micro-payments |
| **Data source** | Oysterworld Relay (port 8787) | 51 nodes, 443 cells, live data |
| **Agent** | Google A2A or Virtuals Agent | Autonomous spatial queries |
| **Frontend** | clawvision.org/map.html | Live visualization |
| **Payment token** | USDC on SKALE | Stablecoin, no volatility |

### Integration Points (Hackathon Partner Bonus)
- ✅ **Coinbase x402** — payment protocol on every API endpoint
- ✅ **Google A2A** — agent-to-agent interop (agent discovers ClawVision service)
- ✅ **SKALE** — gasless chain for micro-payments
- ✅ **Vodafone Pairpoint** — IoT device connectivity (phone fleet = IoT nodes)
- ⬜ **Virtuals** — optional: launch a "Spatial Intelligence Agent" on Virtuals platform
- ⬜ **Edge & Node / ampersend** — optional: agent wallet management

---

## 4. Implementation Plan (3 days)

### Day 1 (Feb 11): x402 Middleware + SKALE Setup
- [ ] Fork/install x402 server middleware (Coinbase reference impl)
- [ ] Add x402 payment check to Oysterworld relay endpoints:
  - `/v1/world/cells` — 100 credits ($0.01)
  - `/v1/world/events` — 200 credits ($0.02)
  - `/v1/world/stats` — free (preview tier)
- [ ] Deploy SKALE USDC contract (or use existing testnet)
- [ ] Test: curl gets 402 → manual pay → 200 OK

### Day 2 (Feb 12): Agent Integration + Demo
- [ ] Build agent flow:
  - Agent receives user question: "What's happening near Union Square right now?"
  - Agent calls world.query() → gets 402
  - Agent pays via x402 → gets spatial data
  - Agent interprets data → answers user
- [ ] Google A2A service registration (ClawVision as discoverable service)
- [ ] Payment dashboard: real-time payment flow visualization
- [ ] Record demo video (2 min)

### Day 3 (Feb 13): Polish + Submit
- [ ] Landing page update: add "x402 Enabled" badge to API portal
- [ ] Pricing page: show per-query costs
- [ ] Write submission text for Dorahacks
- [ ] Submit before deadline

---

## 5. Pricing Model (x402)

| Endpoint | Credits | USD | What You Get |
|----------|---------|-----|-------------|
| `/v1/world/stats` | 0 (free) | $0 | Network stats (teaser) |
| `/v1/world/cells` | 100 | $0.01 | Cell coverage + event counts |
| `/v1/world/events` | 200 | $0.02 | Full event details + thumbnails |
| `/v1/events/frame` (write) | 50 | $0.005 | Submit observation (earn-back) |

**Narrative**: "The cheapest way for an AI to see the real world. 100x cheaper than World Labs ($1.20/generation)."

---

## 6. Judging Criteria Alignment

| Criteria | Our Angle |
|----------|----------|
| **Innovation** | First real-world spatial data API with native x402 payments |
| **Technical Execution** | Live data from 51+ nodes, H3 spatial index, working API |
| **Use of Sponsors** | x402 + SKALE + A2A + Vodafone IoT |
| **Business Viability** | $0.01/query × 30K nodes × scale = real revenue model |
| **Demo Quality** | Agent autonomously pays for + uses real-world data |

---

## 7. Pitch Script (2 minutes)

> "Every AI model today can reason about the world. None of them can *see* it.
>
> ClawVision changes that. We have 30,000+ phones continuously observing the real world — 1 frame per second, spatially indexed, queryable via API.
>
> But here's the problem: how does an AI agent *pay* for this data? API keys don't work for autonomous agents. Monthly subscriptions don't work for one-off queries.
>
> Enter x402. We wrapped our world.query() API with Coinbase's x402 payment protocol. Now any AI agent can:
> 1. Discover our service via Google A2A
> 2. Hit our API — get HTTP 402 Payment Required
> 3. Pay $0.01 in USDC on SKALE — zero gas fees
> 4. Get real-time spatial intelligence
>
> No signup. No API key. No invoices. Just pay and query.
>
> World Labs charges $1.20 to *generate* a synthetic world. We charge $0.01 to *query* the real one.
>
> We call this the Real-Time World Index. And today, it's open for business."

---

## 8. Dispatch to Codex

```bash
# x402 middleware integration
codex exec --skip-git-repo-check --full-auto -C ~/Downloads/claw-nation/relay "
Read src/server.js (the Oysterworld relay server on port 8787).
Add x402 payment middleware to the existing Express/Koa endpoints:
1. Install @coinbase/x402-server-middleware (or implement from x402 spec)
2. Add 402 response to /v1/world/cells and /v1/world/events
3. Keep /v1/world/stats free (no payment required)
4. Accept USDC payments on SKALE chain
5. Add x-payment-required headers per the x402 spec
6. Test: curl without payment → 402, with valid payment → 200
Files: src/server.js
Acceptance: endpoints return 402 without payment, 200 with valid x402 payment
" --json
```
