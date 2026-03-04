"""
CryptoRank API Client
Base URL: https://api.cryptorank.io
"""

import logging
from typing import Optional, Dict, Any, List
from ...common.http_client import HttpClient

logger = logging.getLogger(__name__)

# CryptoRank API Endpoints
ENDPOINTS = {
    # Funding & Investors
    'funding': '/v1/funding',
    'investors': '/v0/coins/investors',
    'top_investors': '/v1/investors',
    
    # Token Unlocks
    'unlock_feed': '/v0/token-unlock-dynamics',
    'unlock_tge': '/v0/token-unlock-dynamics/tge',
    'unlock_totals': '/v0/token-unlock-dynamics/totals',
    
    # Projects & Categories
    'coins': '/v1/currencies',
    'coin_detail': '/v1/currencies/{slug}',
    'categories': '/v1/categories',
    
    # Launchpads & Exchanges
    'launchpads': '/v1/launchpads',
    'exchanges': '/v1/exchanges',
}


class CryptoRankClient:
    """
    Client for CryptoRank API.
    All methods return raw JSON data.
    """
    
    def __init__(self):
        self.http = HttpClient(
            base_url='https://api.cryptorank.io',
            min_interval_ms=1200,  # Be conservative with rate limits
            max_retries=3
        )
        # Override headers for CryptoRank
        self.http.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://cryptorank.io',
            'Referer': 'https://cryptorank.io/',
        }
    
    # ═══════════════════════════════════════════════════════════════
    # FUNDING & INVESTORS
    # ═══════════════════════════════════════════════════════════════
    
    async def funding(
        self,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = 'date',
        sort_dir: str = 'desc'
    ) -> Dict:
        """
        Fetch funding rounds.
        Returns: {data: [...], total: int}
        """
        try:
            params = {
                'limit': limit,
                'offset': offset,
                'sortBy': sort_by,
                'sortDirection': sort_dir
            }
            data = await self.http.get(ENDPOINTS['funding'], params=params)
            return data or {'data': [], 'total': 0}
        except Exception as e:
            logger.error(f"[CryptoRank] funding failed: {e}")
            return {'data': [], 'total': 0}
    
    async def investors(self, coin_key: str) -> List[Dict]:
        """
        Fetch investors for a specific coin.
        """
        try:
            params = {'coinKey': coin_key}
            data = await self.http.get(ENDPOINTS['investors'], params=params)
            return self._extract_list(data)
        except Exception as e:
            logger.error(f"[CryptoRank] investors for {coin_key} failed: {e}")
            return []
    
    async def top_investors(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """
        Fetch top investors/VCs list.
        Returns: {data: [...], total: int}
        """
        try:
            params = {
                'limit': limit,
                'offset': offset
            }
            data = await self.http.get(ENDPOINTS['top_investors'], params=params)
            return data or {'data': [], 'total': 0}
        except Exception as e:
            logger.error(f"[CryptoRank] top_investors failed: {e}")
            return {'data': [], 'total': 0}
    
    # ═══════════════════════════════════════════════════════════════
    # TOKEN UNLOCKS
    # ═══════════════════════════════════════════════════════════════
    
    async def unlock_feed(
        self,
        limit: int = 50,
        offset: int = 0,
        period: str = '1m',
        sort_by: str = 'date'
    ) -> Dict:
        """
        Fetch token unlock feed.
        period: 1w, 2w, 1m, 3m, 6m, 1y
        Returns: {data: [...]}
        """
        try:
            params = {
                'limit': limit,
                'offset': offset,
                'period': period,
                'sortBy': sort_by
            }
            data = await self.http.get(ENDPOINTS['unlock_feed'], params=params)
            return data or {'data': []}
        except Exception as e:
            logger.error(f"[CryptoRank] unlock_feed failed: {e}")
            return {'data': []}
    
    async def unlock_tge(self, limit: int = 50, offset: int = 0) -> Dict:
        """
        Fetch TGE (Token Generation Event) unlocks.
        These are initial unlocks at token launch.
        """
        try:
            params = {'limit': limit, 'offset': offset}
            data = await self.http.get(ENDPOINTS['unlock_tge'], params=params)
            return data or {'data': []}
        except Exception as e:
            logger.error(f"[CryptoRank] unlock_tge failed: {e}")
            return {'data': []}
    
    async def unlock_totals(self) -> Dict:
        """
        Fetch aggregated unlock totals.
        Useful for market-wide sell pressure metrics.
        """
        try:
            data = await self.http.get(ENDPOINTS['unlock_totals'])
            return data or {}
        except Exception as e:
            logger.error(f"[CryptoRank] unlock_totals failed: {e}")
            return {}
    
    # ═══════════════════════════════════════════════════════════════
    # PROJECTS / COINS
    # ═══════════════════════════════════════════════════════════════
    
    async def coins(
        self,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = 'rank'
    ) -> Dict:
        """
        Fetch cryptocurrency list.
        Returns: {data: [...], total: int}
        """
        try:
            params = {
                'limit': limit,
                'offset': offset,
                'sortBy': sort_by
            }
            data = await self.http.get(ENDPOINTS['coins'], params=params)
            return data or {'data': [], 'total': 0}
        except Exception as e:
            logger.error(f"[CryptoRank] coins failed: {e}")
            return {'data': [], 'total': 0}
    
    async def coin_detail(self, slug: str) -> Optional[Dict]:
        """
        Fetch detailed info for a specific coin.
        """
        try:
            endpoint = ENDPOINTS['coin_detail'].format(slug=slug)
            data = await self.http.get(endpoint)
            return data.get('data') if data else None
        except Exception as e:
            logger.error(f"[CryptoRank] coin_detail for {slug} failed: {e}")
            return None
    
    # ═══════════════════════════════════════════════════════════════
    # CATEGORIES & LAUNCHPADS
    # ═══════════════════════════════════════════════════════════════
    
    async def categories(self, limit: int = 100) -> Dict:
        """
        Fetch crypto categories (DeFi, Layer2, etc.)
        """
        try:
            params = {'limit': limit}
            data = await self.http.get(ENDPOINTS['categories'], params=params)
            return data or {'data': []}
        except Exception as e:
            logger.error(f"[CryptoRank] categories failed: {e}")
            return {'data': []}
    
    async def launchpads(self, limit: int = 50, offset: int = 0) -> Dict:
        """
        Fetch launchpad platforms (Binance Launchpad, etc.)
        """
        try:
            params = {'limit': limit, 'offset': offset}
            data = await self.http.get(ENDPOINTS['launchpads'], params=params)
            return data or {'data': []}
        except Exception as e:
            logger.error(f"[CryptoRank] launchpads failed: {e}")
            return {'data': []}
    
    async def exchanges(self, limit: int = 100) -> Dict:
        """
        Fetch exchanges list.
        """
        try:
            params = {'limit': limit}
            data = await self.http.get(ENDPOINTS['exchanges'], params=params)
            return data or {'data': []}
        except Exception as e:
            logger.error(f"[CryptoRank] exchanges failed: {e}")
            return {'data': []}
    
    # ═══════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════
    
    def _extract_list(self, data: Any) -> List[Dict]:
        """Extract list from various response formats"""
        if data is None:
            return []
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ['data', 'items', 'list', 'results']:
                if key in data and isinstance(data[key], list):
                    return data[key]
        return []


# Singleton
cryptorank_client = CryptoRankClient()
