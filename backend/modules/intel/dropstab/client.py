"""
Dropstab API Client
Base URL: https://api2.dropstab.com
"""

import logging
from typing import Optional, Dict, Any, List
from ..common.http_client import HttpClient

logger = logging.getLogger(__name__)

# Known endpoints from network analysis
ENDPOINTS = {
    'investors': '/portfolio/api/investors',
    'vesting': '/portfolio/api/vesting', 
    'fundraising': '/portfolio/api/fundraising',
    'projects': '/portfolio/api/projects',
    'activity': '/portfolio/api/activity',
    'unlocks': '/portfolio/api/unlocks',
    'discover': '/portfolio/api/discover',
}


class DropstabClient:
    """
    Client for Dropstab API.
    All methods return raw JSON data.
    """
    
    def __init__(self):
        self.http = HttpClient(
            base_url='https://api2.dropstab.com',
            min_interval_ms=1000,  # 1 request per second
            max_retries=3
        )
    
    async def investors(self, params: Optional[Dict] = None) -> List[Dict]:
        """Fetch investors/VCs list"""
        try:
            data = await self.http.post(ENDPOINTS['investors'], params or {})
            return self._extract_list(data)
        except Exception as e:
            logger.error(f"[Dropstab] investors failed: {e}")
            return []
    
    async def vesting(self, params: Optional[Dict] = None) -> List[Dict]:
        """Fetch token vesting/unlock data"""
        try:
            data = await self.http.post(ENDPOINTS['vesting'], params or {})
            return self._extract_list(data)
        except Exception as e:
            logger.error(f"[Dropstab] vesting failed: {e}")
            return []
    
    async def unlocks(self, params: Optional[Dict] = None) -> List[Dict]:
        """Fetch token unlocks"""
        try:
            data = await self.http.post(ENDPOINTS['unlocks'], params or {})
            return self._extract_list(data)
        except Exception as e:
            logger.error(f"[Dropstab] unlocks failed: {e}")
            return []
    
    async def fundraising(self, params: Optional[Dict] = None) -> List[Dict]:
        """Fetch funding rounds"""
        try:
            data = await self.http.post(ENDPOINTS['fundraising'], params or {})
            return self._extract_list(data)
        except Exception as e:
            logger.error(f"[Dropstab] fundraising failed: {e}")
            return []
    
    async def projects(self, params: Optional[Dict] = None) -> List[Dict]:
        """Fetch projects list"""
        try:
            data = await self.http.post(ENDPOINTS['projects'], params or {})
            return self._extract_list(data)
        except Exception as e:
            logger.error(f"[Dropstab] projects failed: {e}")
            return []
    
    async def activity(self, params: Optional[Dict] = None) -> List[Dict]:
        """Fetch activity/news feed"""
        try:
            data = await self.http.post(ENDPOINTS['activity'], params or {})
            return self._extract_list(data)
        except Exception as e:
            logger.error(f"[Dropstab] activity failed: {e}")
            return []
    
    async def discover(self, params: Optional[Dict] = None) -> List[Dict]:
        """Fetch discover/trending projects"""
        try:
            data = await self.http.post(ENDPOINTS['discover'], params or {})
            return self._extract_list(data)
        except Exception as e:
            logger.error(f"[Dropstab] discover failed: {e}")
            return []
    
    def _extract_list(self, data: Any) -> List[Dict]:
        """Extract list from various response formats"""
        if data is None:
            return []
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            # Try common response structures
            for key in ['data', 'items', 'list', 'results', 'rows']:
                if key in data and isinstance(data[key], list):
                    return data[key]
            # If dict has expected fields, wrap in list
            if 'name' in data or 'symbol' in data:
                return [data]
        return []


# Singleton
dropstab_client = DropstabClient()
