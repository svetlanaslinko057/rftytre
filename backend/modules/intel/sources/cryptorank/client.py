"""
CryptoRank API Client
Base URL: https://api.cryptorank.io

NOTE: CryptoRank API requires an API key for authentication.
Get your key at: https://cryptorank.io/public-api

Usage:
  Set CRYPTORANK_API_KEY environment variable or pass api_key to client
"""

import os
import logging
from typing import Optional, Dict, Any, List
from ...common.http_client import HttpClient

logger = logging.getLogger(__name__)

# CryptoRank API Endpoints
ENDPOINTS = {
    # Funding & Investors
    'funding': '/v1/funding-rounds',
    'investors': '/v1/funds',
    
    # Token Unlocks
    'unlocks': '/v1/token-unlocks',
    
    # Projects & Categories  
    'coins': '/v1/currencies',
    'coin_detail': '/v1/currencies/{key}',
    'categories': '/v1/categories',
    
    # Launchpads & Exchanges
    'launchpads': '/v1/ido-platforms',
    'ieo_platforms': '/v1/ieo-platforms',
    'exchanges': '/v1/exchanges',
}


class CryptoRankClient:
    """
    Client for CryptoRank API.
    All methods return raw JSON data.
    
    Requires API key from https://cryptorank.io/public-api
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('CRYPTORANK_API_KEY')
        
        self.http = HttpClient(
            base_url='https://api.cryptorank.io',
            min_interval_ms=1200,  # Be conservative with rate limits
            max_retries=3
        )
        # Override headers for CryptoRank
        self.http.headers = {
            'User-Agent': 'FOMO-Market-API/1.0',
            'Accept': 'application/json',
        }
    
    def _add_api_key(self, params: Optional[Dict] = None) -> Dict:
        """Add API key to params"""
        params = params or {}
        if self.api_key:
            params['api_key'] = self.api_key
        return params
    
    def is_configured(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key)
    
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
        if not self.is_configured():
            logger.warning("[CryptoRank] API key not configured. Set CRYPTORANK_API_KEY env var.")
            return {'data': [], 'total': 0}
        
        try:
            params = self._add_api_key({
                'limit': limit,
                'offset': offset,
                'sortBy': sort_by,
                'sortDirection': sort_dir
            })
            data = await self.http.get(ENDPOINTS['funding'], params=params)
            return data or {'data': [], 'total': 0}
        except Exception as e:
            logger.error(f"[CryptoRank] funding failed: {e}")
            return {'data': [], 'total': 0}
    
    async def investors(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """
        Fetch investors/funds list.
        Returns: {data: [...], total: int}
        """
        if not self.is_configured():
            logger.warning("[CryptoRank] API key not configured")
            return {'data': [], 'total': 0}
        
        try:
            params = self._add_api_key({
                'limit': limit,
                'offset': offset
            })
            data = await self.http.get(ENDPOINTS['investors'], params=params)
            return data or {'data': [], 'total': 0}
        except Exception as e:
            logger.error(f"[CryptoRank] investors failed: {e}")
            return {'data': [], 'total': 0}
    
    # ═══════════════════════════════════════════════════════════════
    # TOKEN UNLOCKS
    # ═══════════════════════════════════════════════════════════════
    
    async def unlocks(
        self,
        limit: int = 100,
        offset: int = 0,
        period: str = '1m'
    ) -> Dict:
        """
        Fetch token unlock schedule.
        period: 1w, 2w, 1m, 3m, 6m, 1y
        Returns: {data: [...]}
        """
        if not self.is_configured():
            logger.warning("[CryptoRank] API key not configured")
            return {'data': []}
        
        try:
            params = self._add_api_key({
                'limit': limit,
                'offset': offset,
                'period': period
            })
            data = await self.http.get(ENDPOINTS['unlocks'], params=params)
            return data or {'data': []}
        except Exception as e:
            logger.error(f"[CryptoRank] unlocks failed: {e}")
            return {'data': []}
    
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
        if not self.is_configured():
            logger.warning("[CryptoRank] API key not configured")
            return {'data': [], 'total': 0}
        
        try:
            params = self._add_api_key({
                'limit': limit,
                'offset': offset,
                'sortBy': sort_by
            })
            data = await self.http.get(ENDPOINTS['coins'], params=params)
            return data or {'data': [], 'total': 0}
        except Exception as e:
            logger.error(f"[CryptoRank] coins failed: {e}")
            return {'data': [], 'total': 0}
    
    async def coin_detail(self, key: str) -> Optional[Dict]:
        """
        Fetch detailed info for a specific coin.
        """
        if not self.is_configured():
            return None
        
        try:
            endpoint = ENDPOINTS['coin_detail'].format(key=key)
            params = self._add_api_key()
            data = await self.http.get(endpoint, params=params)
            return data.get('data') if data else None
        except Exception as e:
            logger.error(f"[CryptoRank] coin_detail for {key} failed: {e}")
            return None
    
    # ═══════════════════════════════════════════════════════════════
    # CATEGORIES & LAUNCHPADS
    # ═══════════════════════════════════════════════════════════════
    
    async def categories(self, limit: int = 100) -> Dict:
        """
        Fetch crypto categories (DeFi, Layer2, etc.)
        """
        if not self.is_configured():
            return {'data': []}
        
        try:
            params = self._add_api_key({'limit': limit})
            data = await self.http.get(ENDPOINTS['categories'], params=params)
            return data or {'data': []}
        except Exception as e:
            logger.error(f"[CryptoRank] categories failed: {e}")
            return {'data': []}
    
    async def launchpads(self, limit: int = 50, offset: int = 0) -> Dict:
        """
        Fetch IDO launchpad platforms
        """
        if not self.is_configured():
            return {'data': []}
        
        try:
            params = self._add_api_key({'limit': limit, 'offset': offset})
            data = await self.http.get(ENDPOINTS['launchpads'], params=params)
            return data or {'data': []}
        except Exception as e:
            logger.error(f"[CryptoRank] launchpads failed: {e}")
            return {'data': []}
    
    async def ieo_platforms(self, limit: int = 50) -> Dict:
        """
        Fetch IEO platforms (CEX launchpads)
        """
        if not self.is_configured():
            return {'data': []}
        
        try:
            params = self._add_api_key({'limit': limit})
            data = await self.http.get(ENDPOINTS['ieo_platforms'], params=params)
            return data or {'data': []}
        except Exception as e:
            logger.error(f"[CryptoRank] ieo_platforms failed: {e}")
            return {'data': []}
    
    async def exchanges(self, limit: int = 100) -> Dict:
        """
        Fetch exchanges list.
        """
        if not self.is_configured():
            return {'data': []}
        
        try:
            params = self._add_api_key({'limit': limit})
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


# Singleton - initialized with env var
cryptorank_client = CryptoRankClient()
