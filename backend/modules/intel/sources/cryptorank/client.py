"""
CryptoRank Scraper Client
Uses public frontend endpoints (no API key required)

This is a SCRAPER, not an official API client.
Data is fetched from CryptoRank's internal frontend endpoints.
"""

import logging
from typing import Optional, Dict, Any, List
from ...common.http_client import HttpClient

logger = logging.getLogger(__name__)

# CryptoRank Frontend Endpoints (scraped from website)
# These are internal API endpoints used by cryptorank.io frontend
BASE_URL = "https://api.cryptorank.io"

ENDPOINTS = {
    # Funding & Investors
    'funding': '/v0/coins/funding-rounds',
    'top_investors': '/v0/widgets/funding-rounds/top-investors',
    
    # Token Unlocks  
    'unlocks': '/v0/token-unlock-dynamics',
    'unlock_tge': '/v0/token-unlock-dynamics/tge',
    'unlock_totals': '/v0/token-unlock-dynamics/totals',
    
    # Projects & Categories
    'categories': '/v0/categories',
    
    # Launchpads & Exchanges
    'launchpads': '/v0/fundraising-platforms',
    'exchanges': '/v0/exchanges',
}


class CryptoRankClient:
    """
    Scraper client for CryptoRank frontend API.
    No API key required - uses public endpoints.
    """
    
    def __init__(self):
        self.http = HttpClient(
            base_url=BASE_URL,
            min_interval_ms=1500,  # Conservative rate limiting
            max_retries=3
        )
        # Browser-like headers for scraping
        self.http.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://cryptorank.io',
            'Referer': 'https://cryptorank.io/',
        }
    
    # ═══════════════════════════════════════════════════════════════
    # FUNDING & INVESTORS  
    # ═══════════════════════════════════════════════════════════════
    
    async def funding(self, limit: int = 50, offset: int = 0) -> Dict:
        """
        Fetch funding rounds.
        Returns: {total: int, data: [...]}
        
        Each item contains:
        - key, name, symbol (project)
        - raise, stage, date (funding)
        - funds (investors list with tier, category, totalInvestments)
        """
        try:
            params = {
                'limit': limit,
                'offset': offset
            }
            data = await self.http.get(ENDPOINTS['funding'], params=params)
            return data or {'data': [], 'total': 0}
        except Exception as e:
            logger.error(f"[CryptoRank] funding failed: {e}")
            return {'data': [], 'total': 0}
    
    async def top_investors(self, limit: int = 50) -> List[Dict]:
        """
        Fetch top investors ranking.
        Returns list of: {slug, name, count, logo}
        """
        try:
            params = {'limit': limit}
            data = await self.http.get(ENDPOINTS['top_investors'], params=params)
            return self._extract_list(data)
        except Exception as e:
            logger.error(f"[CryptoRank] top_investors failed: {e}")
            return []
    
    # ═══════════════════════════════════════════════════════════════
    # TOKEN UNLOCKS
    # ═══════════════════════════════════════════════════════════════
    
    async def unlocks(self, limit: int = 50, offset: int = 0) -> Dict:
        """
        Fetch token unlock schedule.
        Returns: {data: [...]}
        
        Each item contains:
        - key, symbol (token)
        - unlockUsd, tokensPercent
        - unlockDate
        """
        try:
            params = {
                'limit': limit,
                'offset': offset
            }
            data = await self.http.get(ENDPOINTS['unlocks'], params=params)
            return data or {'data': []}
        except Exception as e:
            logger.error(f"[CryptoRank] unlocks failed: {e}")
            return {'data': []}
    
    async def unlock_tge(self, limit: int = 50, offset: int = 0) -> Dict:
        """
        Fetch TGE (Token Generation Event) unlocks.
        Initial unlock at token launch.
        """
        try:
            params = {'limit': limit, 'offset': offset}
            data = await self.http.get(ENDPOINTS['unlock_tge'], params=params)
            return data or {'data': []}
        except Exception as e:
            logger.error(f"[CryptoRank] unlock_tge failed: {e}")
            return {'data': []}
    
    async def unlock_totals(self) -> List[Dict]:
        """
        Fetch market-wide unlock totals by date.
        Returns: [{usdUnlock, timePoint}, ...]
        
        Used for calculating market sell pressure.
        """
        try:
            data = await self.http.get(ENDPOINTS['unlock_totals'])
            return self._extract_list(data)
        except Exception as e:
            logger.error(f"[CryptoRank] unlock_totals failed: {e}")
            return []
    
    # ═══════════════════════════════════════════════════════════════
    # CATEGORIES & LAUNCHPADS
    # ═══════════════════════════════════════════════════════════════
    
    async def categories(self) -> List[Dict]:
        """
        Fetch crypto categories/sectors (DeFi, GameFi, etc.)
        Used for narrative analysis.
        """
        try:
            data = await self.http.get(ENDPOINTS['categories'])
            return self._extract_list(data)
        except Exception as e:
            logger.error(f"[CryptoRank] categories failed: {e}")
            return []
    
    async def launchpads(self, limit: int = 100) -> List[Dict]:
        """
        Fetch launchpad platforms (IDO, IEO, ICO).
        """
        try:
            params = {'limit': limit}
            data = await self.http.get(ENDPOINTS['launchpads'], params=params)
            return self._extract_list(data)
        except Exception as e:
            logger.error(f"[CryptoRank] launchpads failed: {e}")
            return []
    
    async def exchanges(self, limit: int = 100) -> List[Dict]:
        """
        Fetch exchanges list.
        """
        try:
            params = {'limit': limit}
            data = await self.http.get(ENDPOINTS['exchanges'], params=params)
            return self._extract_list(data)
        except Exception as e:
            logger.error(f"[CryptoRank] exchanges failed: {e}")
            return []
    
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
