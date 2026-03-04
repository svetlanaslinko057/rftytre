"""
Funding rounds parser for CryptoRank
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


def parse_timestamp(value: Any) -> Optional[int]:
    """Convert various date formats to unix timestamp"""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        # Already timestamp - check if ms or seconds
        return int(value) if value < 1e12 else int(value / 1000)
    if isinstance(value, str):
        try:
            # Try ISO format
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return int(dt.timestamp())
        except:
            pass
        try:
            # Try common formats
            for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%d/%m/%Y']:
                dt = datetime.strptime(value, fmt)
                return int(dt.timestamp())
        except:
            pass
    return None


def parse_funding(data: List[Dict]) -> List[Dict]:
    """
    Parse funding rounds from CryptoRank.
    
    Expected input format (from /v1/funding):
    {
        "key": "kaito-seed-2025-02-28",
        "coin": {"key": "kaito", "name": "Kaito", "symbol": "KAITO", ...},
        "round": {"key": "seed", "name": "Seed"},
        "date": "2025-02-28",
        "amount": 10000000,
        "valuation": null,
        "investors": [
            {"key": "paradigm", "name": "Paradigm", "tier": "1", ...},
            ...
        ],
        "leadInvestors": [{"key": "paradigm", ...}]
    }
    """
    results = []
    
    for r in data:
        coin = r.get('coin') or {}
        symbol = (coin.get('symbol') or '').upper()
        
        if not symbol:
            continue
        
        project_name = coin.get('name') or symbol
        project_key = coin.get('key') or symbol.lower()
        
        # Round info
        round_obj = r.get('round') or {}
        round_name = round_obj.get('name') or round_obj.get('key') or 'unknown'
        
        # Date
        date = parse_timestamp(r.get('date'))
        
        # Create unique key
        cr_key = r.get('key') or f"{project_key}-{round_name}-{date or 'nodate'}"
        key = f"cryptorank:funding:{cr_key}"
        
        # Parse investors
        investors = []
        lead_investors = []
        
        for inv in (r.get('investors') or []):
            inv_name = inv.get('name') or inv.get('key')
            if inv_name:
                investors.append({
                    'name': inv_name,
                    'key': inv.get('key'),
                    'tier': inv.get('tier'),
                    'type': inv.get('type')
                })
        
        for inv in (r.get('leadInvestors') or []):
            inv_name = inv.get('name') or inv.get('key')
            if inv_name:
                lead_investors.append(inv_name)
        
        doc = {
            'key': key,
            'source': 'cryptorank',
            'source_key': cr_key,
            
            # Project info
            'project': project_name,
            'project_key': project_key,
            'symbol': symbol,
            
            # Round details
            'round': round_name,
            'date': date,
            
            # Amounts
            'amount': r.get('amount'),
            'valuation': r.get('valuation'),
            
            # Investors
            'investors': investors,
            'investors_count': len(investors),
            'lead_investors': lead_investors,
            
            # Coin metadata
            'coin_rank': coin.get('rank'),
            'coin_category': coin.get('category', {}).get('name') if isinstance(coin.get('category'), dict) else None,
            
            # Raw for debugging
            'raw': r
        }
        
        results.append(doc)
    
    return results
