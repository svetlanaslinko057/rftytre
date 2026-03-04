# ГЛУБОКИЙ АУДИТ EXCHANGE ПРОВАЙДЕРОВ
## FOMO Exchange Backend v1.7.0

---

# 1. BINANCE FUTURES (USDT-M)

## Base URL: `https://fapi.binance.com`

### ✅ РЕАЛИЗОВАНО (что берем сейчас):

| Метод | Endpoint | Данные |
|-------|----------|--------|
| `fetch_ticker` | `/fapi/v1/ticker/24hr` | price, bid, ask, volume24h, change24h, high24h, low24h |
| `fetch_orderbook` | `/fapi/v1/depth` | bids[], asks[] (price + quantity) |
| `fetch_trades` | `/fapi/v1/trades` | tradeId, price, qty, side, timestamp |
| `fetch_candles` | `/fapi/v1/klines` | OHLCV (open, high, low, close, volume) |
| `fetch_funding` | `/fapi/v1/premiumIndex` | fundingRate, nextFundingTime |
| `fetch_open_interest` | `/fapi/v1/openInterest` | openInterest (количество контрактов) |
| `fetch_symbols` | `/fapi/v1/exchangeInfo` | список PERPETUAL пар |

### ❌ НЕ РЕАЛИЗОВАНО (можем добавить):

| Endpoint | Данные | Применение |
|----------|--------|------------|
| `/fapi/v1/aggTrades` | Агрегированные сделки | Анализ крупных сделок, CVD |
| `/fapi/v1/historicalTrades` | Исторические сделки | Бэктестинг |
| `/fapi/v1/continuousKlines` | Непрерывные свечи | Анализ без гэпов |
| `/fapi/v1/indexPriceKlines` | Index Price свечи | Базис-трейдинг |
| `/fapi/v1/markPriceKlines` | Mark Price свечи | Анализ маркировки |
| `/fapi/v1/fundingRate` | История funding rate | Анализ тренда funding |
| `/fapi/v1/fundingInfo` | Predicted funding | Прогноз funding |
| `/fapi/v1/ticker/bookTicker` | Best bid/ask | Быстрый спред |
| `/fapi/v2/ticker/price` | Все цены сразу | Скринер |
| `/fapi/v1/topLongShortAccountRatio` | Long/Short ratio (аккаунты) | Сентимент |
| `/fapi/v1/topLongShortPositionRatio` | Long/Short ratio (позиции) | Сентимент |
| `/fapi/v1/globalLongShortAccountRatio` | Глобальный L/S ratio | Сентимент |
| `/fapi/v1/takerlongshortRatio` | Taker Buy/Sell ratio | CVD анализ |
| `/fapi/v1/openInterestHist` | История OI | Тренд OI |
| `/fapi/v1/lvtKlines` | Leveraged token klines | - |
| `/futures/data/openInterestHist` | OI с группировкой | Анализ крупных игроков |
| `/futures/data/topLongShortAccountRatio` | Top trader ratio | Профи vs розница |
| `/futures/data/topLongShortPositionRatio` | Top position ratio | Анализ китов |
| `/futures/data/globalLongShortAccountRatio` | Global ratio | Массовый сентимент |

### WebSocket (real-time):
- `<symbol>@aggTrade` - агрегированные сделки
- `<symbol>@trade` - все сделки
- `<symbol>@kline_<interval>` - свечи real-time
- `<symbol>@miniTicker` - мини-тикер
- `<symbol>@ticker` - полный тикер
- `<symbol>@depth<levels>` - orderbook (5/10/20 уровней)
- `<symbol>@depth@100ms` - orderbook diff
- `<symbol>@bookTicker` - best bid/ask
- `<symbol>@forceOrder` - ликвидации
- `<symbol>@markPrice` - mark price
- `!forceOrder@arr` - все ликвидации

---

# 2. BYBIT (USDT Perpetual)

## Base URL: `https://api.bybit.com`

### ✅ РЕАЛИЗОВАНО:

| Метод | Endpoint | Данные |
|-------|----------|--------|
| `fetch_ticker` | `/v5/market/tickers` | price, bid1, ask1, volume24h, change24h, high24h, low24h, fundingRate |
| `fetch_orderbook` | `/v5/market/orderbook` | bids[], asks[] (до 1000 уровней!) |
| `fetch_trades` | `/v5/market/recent-trade` | execId, price, size, side, time |
| `fetch_candles` | `/v5/market/kline` | OHLCV |
| `fetch_funding` | `/v5/market/tickers` | fundingRate, nextFundingTime |
| `fetch_open_interest` | `/v5/market/open-interest` | openInterest, timestamp |
| `fetch_symbols` | `/v5/market/instruments-info` | список linear USDT пар |

### ❌ НЕ РЕАЛИЗОВАНО:

| Endpoint | Данные | Применение |
|----------|--------|------------|
| `/v5/market/mark-price-kline` | Mark Price OHLCV | Анализ маркировки |
| `/v5/market/index-price-kline` | Index Price OHLCV | Базис-трейдинг |
| `/v5/market/premium-index-price-kline` | Premium Index | Арбитраж |
| `/v5/market/funding/history` | История funding | Тренд funding |
| `/v5/market/risk-limit` | Risk limits | Ликвидации |
| `/v5/market/delivery-price` | Settlement price | Экспирация |
| `/v5/market/historical-volatility` | Историческая волатильность | Options/Greeks |
| `/v5/market/insurance` | Insurance fund | Системный риск |
| `/v5/market/long-short-ratio` | Long/Short ratio | Сентимент |

### WebSocket:
- `orderbook.{depth}.{symbol}` - orderbook (1/50/200/500)
- `publicTrade.{symbol}` - сделки
- `tickers.{symbol}` - тикер (50ms update!)
- `kline.{interval}.{symbol}` - свечи
- `liquidation.{symbol}` - ликвидации
- `lt.{symbol}` - leveraged tokens

---

# 3. COINBASE (Spot)

## Base URL: `https://api.exchange.coinbase.com`

### ✅ РЕАЛИЗОВАНО:

| Метод | Endpoint | Данные |
|-------|----------|--------|
| `fetch_ticker` | `/products/{pair}/ticker` | price, bid, ask, volume |
| `fetch_trades` | `/products/{pair}/trades` | trade_id, price, size, side, time |
| `fetch_candles` | `/products/{pair}/candles` | OHLCV |
| `fetch_symbols` | `/products` | список USD пар |

### ❌ НЕ РЕАЛИЗОВАНО:

| Endpoint | Данные | Применение |
|----------|--------|------------|
| `/products/{pair}/book` | Order book (L1/L2/L3) | Глубина рынка |
| `/products/{pair}/stats` | 24h статистика | Детальная статистика |
| `/products` (full) | Детали инструмента | min/max size, tick size |
| `/currencies` | Список валют | Мета-данные |
| `/time` | Серверное время | Синхронизация |

### WebSocket:
- `level2` - L2 orderbook
- `level2_batch` - Батч orderbook
- `matches` - Исполненные сделки
- `ticker` - Real-time тикер
- `ticker_batch` - Батч тикеров
- `full` - Full channel (L3)
- `user` - Приватные данные (требует auth)

### ⚠️ ОГРАНИЧЕНИЯ COINBASE:
- **ТОЛЬКО SPOT** - нет фьючерсов, нет funding rate, нет OI
- Подходит для **подтверждения цены** и **спот-анализа**
- Хорош для divergence analysis (spot vs futures)

---

# 4. HYPERLIQUID (Perp DEX)

## Base URL: `https://api.hyperliquid.xyz`

### ✅ РЕАЛИЗОВАНО:

| Метод | Endpoint | Данные |
|-------|----------|--------|
| `fetch_whale_positions` | POST `/info` (clearinghouseState) | positions[], pnl, leverage, entry |
| `fetch_all_whale_snapshots` | Итерация по адресам | Агрегация позиций китов |

### ❌ НЕ РЕАЛИЗОВАНО (ОГРОМНЫЙ ПОТЕНЦИАЛ!):

| Endpoint | Type | Данные | Применение |
|----------|------|--------|------------|
| POST `/info` | `meta` | Все рынки | Список инструментов |
| POST `/info` | `allMids` | Все mid prices | Скринер |
| POST `/info` | `metaAndAssetCtxs` | Мета + контексты | OI, funding, volume |
| POST `/info` | `l2Book` | L2 Orderbook | Глубина рынка |
| POST `/info` | `recentTrades` | Последние сделки | Tape reading |
| POST `/info` | `candleSnapshot` | OHLCV | Свечи |
| POST `/info` | `fundingHistory` | История funding | Тренд |
| POST `/info` | `userFills` | Fills пользователя | История сделок |
| POST `/info` | `userFunding` | Funding пользователя | P&L от funding |
| POST `/info` | `openOrders` | Открытые ордера | Whale tracking |
| POST `/info` | `frontendOpenOrders` | Frontend ордера | UI данные |
| POST `/info` | `userRateLimit` | Rate limits | API лимиты |
| POST `/info` | `orderStatus` | Статус ордера | Отслеживание |
| POST `/info` | `spotMeta` | Spot метаданные | Spot trading |
| POST `/info` | `spotClearinghouseState` | Spot позиции | Spot whale |
| POST `/info` | `vaultDetails` | Vault данные | LP анализ |
| POST `/info` | `delegatorHistory` | История делегаций | Staking |
| POST `/info` | `referral` | Реферальная статистика | - |
| POST `/info` | `leaderboard` | Топ трейдеры | Smart money |
| POST `/info` | `historicalOrders` | История ордеров | Бэктест |

### WebSocket:
- `allMids` - Все mid prices
- `l2Book` - Orderbook updates
- `trades` - Сделки
- `orderUpdates` - Обновления ордеров
- `user` - Данные пользователя
- `notification` - Уведомления

### 🔥 УНИКАЛЬНЫЕ ВОЗМОЖНОСТИ HYPERLIQUID:
1. **On-chain прозрачность** - все позиции публичны
2. **Whale tracking** - отслеживание любого адреса
3. **Leaderboard API** - топ трейдеры
4. **Vault analytics** - LP позиции
5. **Полная история** - все сделки on-chain

---

# СВОДНАЯ ТАБЛИЦА ПО ПРОВАЙДЕРАМ

| Функция | Binance | Bybit | Coinbase | Hyperliquid |
|---------|---------|-------|----------|-------------|
| **Ticker** | ✅ | ✅ | ✅ | ❌ (можно добавить) |
| **Orderbook** | ✅ | ✅ | ❌ | ❌ (можно добавить) |
| **Trades** | ✅ | ✅ | ✅ | ❌ (можно добавить) |
| **Candles** | ✅ | ✅ | ✅ | ❌ (можно добавить) |
| **Funding Rate** | ✅ | ✅ | ❌ (spot) | ❌ (можно добавить) |
| **Open Interest** | ✅ | ✅ | ❌ (spot) | ❌ (можно добавить) |
| **Symbols** | ✅ | ✅ | ✅ | ❌ (можно добавить) |
| **Whale Positions** | ❌ | ❌ | ❌ | ✅ |
| **Liquidations** | ❌ | ❌ | ❌ | ❌ |
| **Long/Short Ratio** | ❌ | ❌ | ❌ | ❌ |
| **Aggregated Trades** | ❌ | ❌ | ❌ | ❌ |
| **Mark/Index Price** | ❌ | ❌ | ❌ | ❌ |
| **WebSocket** | ❌ | ❌ | ❌ | ❌ |

---

# РЕКОМЕНДАЦИИ ПО РАСШИРЕНИЮ

## Приоритет 1 - Критичные индикаторы:
1. **Long/Short Ratio** (Binance) - сентимент рынка
2. **Liquidations stream** (Binance/Bybit) - ликвидации
3. **Aggregated Trades** (Binance) - CVD (Cumulative Volume Delta)
4. **Funding History** (все) - тренд funding rate

## Приоритет 2 - Hyperliquid расширение:
1. **Market data** (ticker, orderbook, trades, candles)
2. **Leaderboard API** - топ трейдеры
3. **More whale addresses** - реальные киты

## Приоритет 3 - WebSocket:
1. Real-time tickers
2. Real-time orderbook
3. Real-time trades
4. Liquidations feed

## Приоритет 4 - Расширенная аналитика:
1. **Mark/Index Price** - базис-трейдинг
2. **Top Trader Ratio** - профи vs розница
3. **Taker Buy/Sell Ratio** - анализ агрессии

---

# СТАТИСТИКА ТЕКУЩЕЙ РЕАЛИЗАЦИИ

| Провайдер | Реализовано | Доступно | Покрытие |
|-----------|-------------|----------|----------|
| Binance | 7 endpoints | 25+ endpoints | ~28% |
| Bybit | 7 endpoints | 15+ endpoints | ~47% |
| Coinbase | 4 endpoints | 10+ endpoints | ~40% |
| Hyperliquid | 2 endpoints | 20+ endpoints | ~10% |

**Общий потенциал расширения: 70+ новых endpoints**
