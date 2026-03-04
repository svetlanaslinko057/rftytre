# FOMO Market Data API - PRD

## Version: 2.2.0

## Original Problem Statement
Создать FOMO Market Data API - Unified Exchange Data Backend уровня CoinGecko/CoinMarketCap для получения real-time и исторических данных из Binance / Bybit / Coinbase / Hyperliquid.

## Architecture Principle
```
Provider → Raw Data → Normalizer → Redis Store → Aggregation → API
```

**Мы забираем ВСЁ, что отдают провайдеры. Не выбирать. Не оптимизировать. Не фильтровать.**

---

## Layer 1 Roadmap Status

| Этап | Название | Статус |
|------|----------|--------|
| 1 | Provider Coverage | ✅ 80% |
| 2 | Instrument Registry | ✅ Done |
| 3 | Data Normalization | ✅ Done |
| 4 | Aggregation Engine v2 | ✅ Done |
| 5 | Redis Cache | ✅ Done |
| 6 | WebSocket Gateway | ⏳ Next |
| 7 | Market API | ✅ Done |

---

## Data Coverage

### Provider Matrix

| Provider | Role | Status | Coverage |
|----------|------|--------|----------|
| Binance | Primary derivatives | ❌ Blocked (451) | 91% |
| Bybit | Secondary derivatives | ❌ Blocked (403) | 75% |
| Coinbase | Spot reference | ✅ Working | 86% |
| Hyperliquid | On-chain perp + whale tracking | ✅ Working | 67% |

### Data Types Implemented

**Market Data:**
- ✅ Ticker, Trades, Orderbook, Candles
- ✅ Exchange Info, Symbols, Instruments

**Derivatives:**
- ✅ Funding Rate, Funding History
- ✅ Open Interest, OI History
- ✅ Mark Price, Index Price
- ✅ Long/Short Ratio
- ✅ Top Trader Ratio
- ✅ Taker Buy/Sell Ratio
- ✅ Liquidations
- ✅ Book Ticker (fast spread)

**Aggregation Engine v2:**
- ✅ Price Median (outlier detection)
- ✅ Price VWAP
- ✅ Volume by Type (spot/perp/futures)
- ✅ Funding Aggregation
- ✅ OI Aggregation
- ✅ Confidence Scoring

---

## API Endpoints

### /api/health
Service health check

### /api/redis/* (NEW - Stage 5)
- `GET /redis/health` - Redis health check
- `GET /redis/stats` - Redis key statistics
- `GET /redis/pipeline/status` - Pipeline status
- `POST /redis/pipeline/warm` - Manual cache warm
- `GET /redis/cache/ticker` - Cached ticker (ultra-fast)
- `GET /redis/cache/tickers` - Batch cached tickers
- `GET /redis/cache/funding` - Cached funding rate
- `GET /redis/cache/open-interest` - Cached OI
- `GET /redis/cache/asset` - Aggregated asset snapshot
- `GET /redis/cache/global` - Global market snapshot
- `GET /redis/cache/liquidations` - Liquidations stream
- `GET /redis/cache/trades` - Trades stream

### /api/market/*
- `GET /market/overview` - Global metrics, benchmarks
- `GET /market/assets` - Assets table
- `GET /market/stats` - Registry statistics

### /api/assets/*
- `GET /assets/search` - Search assets
- `GET /assets/{id}` - Asset profile + metrics
- `GET /assets/{id}/performance` - Performance by periods
- `GET /assets/{id}/chart` - Chart data
- `GET /assets/{id}/venues` - Market pairs

### /api/exchange/*
- `GET /exchange/instruments` - List instruments
- `GET /exchange/ticker` - Ticker
- `GET /exchange/orderbook` - L2 orderbook
- `GET /exchange/trades` - Recent trades
- `GET /exchange/candles` - OHLCV
- `GET /exchange/providers` - List providers
- `GET /exchange/providers/health` - Provider health

### /api/derivatives/*
- `GET /derivatives/funding` - Current funding rate
- `GET /derivatives/funding/history` - Funding history
- `GET /derivatives/open-interest` - Open Interest
- `GET /derivatives/open-interest/history` - OI history
- `GET /derivatives/liquidations` - Liquidations feed
- `GET /derivatives/long-short` - L/S ratio
- `GET /derivatives/sentiment` - Aggregated sentiment

### /api/whales/*
- `GET /whales/health` - Whale provider health
- `GET /whales/snapshots` - Whale positions
- `GET /whales/user/{address}` - User positions
- `GET /whales/leaderboard` - Top traders
- `GET /whales/status` - Tracking status

---

## Module Structure

```
/app/backend/modules/market_data/
├── domain/
│   └── types.py              # All DTO contracts
├── providers/
│   ├── base.py               # MarketDataProvider interface
│   ├── registry.py           # Provider registry
│   ├── binance/adapter.py    # 20+ endpoints
│   ├── bybit/adapter.py
│   ├── coinbase/adapter.py
│   └── hyperliquid/adapter.py
├── services/
│   ├── instrument_registry.py
│   ├── aggregator.py
│   ├── aggregation_engine.py # v2 with VWAP, confidence
│   └── redis_pipeline.py     # NEW - Data pipeline for Redis
├── store/
│   └── redis_store.py        # NEW - Redis client & operations
└── api/
    ├── routes_exchange.py
    ├── routes_market.py
    ├── routes_assets.py
    ├── routes_derivatives.py
    ├── routes_whales.py
    └── routes_redis.py       # NEW - Redis cache endpoints
```

---

## What's Been Implemented

### ЭТАП 1 - Provider Coverage (80%)
- ✅ Binance: 20 endpoints (blocked by region - 451)
- ✅ Bybit: 9 endpoints (blocked by region - 403)
- ✅ Coinbase: 6 endpoints (working)
- ✅ Hyperliquid: 10 endpoints + whale tracking (working)

### ЭТАП 2 - Instrument Registry
- ✅ 606 instruments (377 Coinbase spot + 229 Hyperliquid perp)
- ✅ 483 assets
- ✅ Symbol mapping

### ЭТАП 3 - Data Normalization
- ✅ All DTO contracts

### ЭТАП 4 - Aggregation Engine v2
- ✅ Price median with outlier detection
- ✅ Price VWAP
- ✅ Volume by type
- ✅ Derivatives aggregation
- ✅ Confidence scoring

### ЭТАП 5 - Redis Realtime Layer (2026-03-04) ✅ NEW
- ✅ Redis Store with key schemas:
  - `ticker:{instrument_id}` - Price snapshots (TTL 20s)
  - `funding:{instrument_id}` - Funding rates (TTL 120s)
  - `oi:{instrument_id}` - Open Interest (TTL 120s)
  - `asset:snap:{asset_id}` - Aggregated assets (TTL 30s)
  - `global:snapshot` - Global metrics (TTL 60s)
- ✅ Redis Pipeline with 4 loops:
  - Ticker loop (3s interval)
  - Funding loop (60s interval)
  - Asset snapshot loop (5s interval)
  - Global snapshot loop (30s interval)
- ✅ Cache API endpoints for ultra-fast data access
- ✅ PubSub for real-time updates

### ЭТАП 7 - Market API
- ✅ All endpoints implemented

---

## Known Issues

1. **Regional Blocks:** Binance (451) and Bybit (403) return regional restriction errors. Need Proxy Manager for production.
2. **Rate Limiting:** Coinbase and Hyperliquid may return 429 during high-frequency sync. Recommend implementing backoff.

---

## Next Steps (Priority Order)

### P0 - WebSocket Gateway (ЭТАП 6)
- `/ws/market` endpoint
- Channels: ticker, orderbook, trades, funding, liquidations
- Listen to Redis PubSub for real-time streaming

### P1 - Historical Storage (ЭТАП 7)
- Candles persistence (MongoDB/TimeSeries)
- Trades history
- Funding history for backtesting

### P2 - Proxy Manager
- Rotating proxies for blocked providers
- Smart routing to bypass regional restrictions

---

## Final Goal

После завершения Layer 1:

**FOMO Market API** → может заменить CoinGecko/CoinMarketCap для внутреннего использования.

Layer 2 (следующий этап):
**Crypto Intelligence Engine** (tokenomics, unlocks, fundraising, entities)
