"""
Token Unlocks parser for CryptoRank
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


def parse_timestamp(value: Any) -> Optional[int]:
    """Convert various date formats to unix timestamp"""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value) if value < 1e12 else int(value / 1000)
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return int(dt.timestamp())
        except:
            pass
        try:
            for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S']:
                dt = datetime.strptime(value, fmt)
                return int(dt.timestamp())
        except:
            pass
    return None


def parse_unlocks(data: List[Dict]) -> List[Dict]:
    """
    Parse token unlocks from CryptoRank unlock feed.
    
    Expected input format (from /v0/token-unlock-dynamics):
    {
        "key": "arb-2024-03-16",
        "coin": {
            "key": "arbitrum",
            "name": "Arbitrum",
            "symbol": "ARB",
            "price": {"USD": 1.85},
            "rank": 45
        },
        "date": "2024-03-16",
        "unlockTokens": 92650000,
        "unlockTokensPercent": 0.925,
        "unlockUsd": 171402500,
        "type": "cliff",
        "allocation": "Team & Advisors"
    }
    """
    results = []
    
    for u in data:
        coin = u.get('coin') or {}
        symbol = (coin.get('symbol') or '').upper()
        
        if not symbol:
            continue
        
        project_name = coin.get('name') or symbol
        project_key = coin.get('key') or symbol.lower()
        
        unlock_date = parse_timestamp(u.get('date'))
        if not unlock_date:
            continue
        
        # Create unique key
        cr_key = u.get('key') or f"{project_key}-{unlock_date}"
        key = f"cryptorank:unlock:{cr_key}"
        
        # Get price
        price_data = coin.get('price') or {}
        price_usd = price_data.get('USD') if isinstance(price_data, dict) else None
        
        doc = {
            'key': key,
            'source': 'cryptorank',
            'source_key': cr_key,
            
            # Project
            'project': project_name,
            'project_key': project_key,
            'symbol': symbol,
            
            # Unlock details
            'unlock_date': unlock_date,
            'unlock_amount': u.get('unlockTokens') or u.get('unlock_tokens'),
            'unlock_percent': u.get('unlockTokensPercent') or u.get('unlock_tokens_percent'),
            'unlock_value_usd': u.get('unlockUsd') or u.get('unlock_usd'),
            
            # Category/allocation
            'unlock_type': u.get('type'),  # cliff, linear
            'allocation': u.get('allocation'),  # Team, Investors, etc.
            
            # Current price for reference
            'price_usd': price_usd,
            'coin_rank': coin.get('rank'),
            
            'raw': u
        }
        
        results.append(doc)
    
    return results


def parse_tge_unlocks(data: List[Dict]) -> List[Dict]:
    """
    Parse TGE (Token Generation Event) unlocks from CryptoRank.
    
    Expected input format (from /v0/token-unlock-dynamics/tge):
    {
        "coin": {
            "key": "movement",
            "name": "Movement",
            "symbol": "MOVE",
            ...
        },
        "tgeDate": "2024-12-09",
        "tgeUnlockPercent": 22.5,
        "tgeUnlockTokens": 2250000000,
        "vestingEnd": "2028-12-09",
        "circulatingSupply": 2500000000,
        "totalSupply": 10000000000
    }
    """
    results = []
    
    for u in data:
        coin = u.get('coin') or {}
        symbol = (coin.get('symbol') or '').upper()
        
        if not symbol:
            continue
        
        project_name = coin.get('name') or symbol
        project_key = coin.get('key') or symbol.lower()
        
        tge_date = parse_timestamp(u.get('tgeDate'))
        if not tge_date:
            continue
        
        key = f"cryptorank:tge:{project_key}"
        
        doc = {
            'key': key,
            'source': 'cryptorank',
            'source_key': project_key,
            
            # Project
            'project': project_name,
            'project_key': project_key,
            'symbol': symbol,
            
            # TGE details
            'unlock_date': tge_date,
            'unlock_type': 'tge',
            'unlock_amount': u.get('tgeUnlockTokens'),
            'unlock_percent': u.get('tgeUnlockPercent'),
            
            # Vesting schedule
            'vesting_end': parse_timestamp(u.get('vestingEnd')),
            
            # Supply metrics
            'circulating_supply': u.get('circulatingSupply'),
            'total_supply': u.get('totalSupply'),
            
            'raw': u
        }
        
        results.append(doc)
    
    return results
