"""
Investors parser for CryptoRank
"""

from typing import Dict, List, Any, Optional


def parse_investors(data: List[Dict], coin_key: str = None) -> List[Dict]:
    """
    Parse investors for a specific coin from CryptoRank.
    
    Expected input format (from /v0/coins/investors):
    {
        "key": "paradigm",
        "name": "Paradigm",
        "tier": "1",
        "type": "Venture Capital",
        "description": "...",
        "links": {...}
    }
    """
    results = []
    
    for inv in data:
        inv_key = inv.get('key')
        inv_name = inv.get('name')
        
        if not inv_key or not inv_name:
            continue
        
        key = f"cryptorank:investor:{inv_key}"
        
        doc = {
            'key': key,
            'source': 'cryptorank',
            'source_key': inv_key,
            
            'name': inv_name,
            'slug': inv_key,
            
            'tier': inv.get('tier'),
            'type': inv.get('type'),
            'description': inv.get('description'),
            
            # Links
            'website': inv.get('links', {}).get('website') if isinstance(inv.get('links'), dict) else None,
            'twitter': inv.get('links', {}).get('twitter') if isinstance(inv.get('links'), dict) else None,
            
            # Track which coins this investor is associated with
            'invested_coins': [coin_key] if coin_key else [],
            
            'raw': inv
        }
        
        results.append(doc)
    
    return results


def parse_top_investors(data: List[Dict]) -> List[Dict]:
    """
    Parse top investors list from CryptoRank.
    
    Expected input format (from /v1/investors):
    {
        "key": "paradigm",
        "name": "Paradigm",
        "tier": "1",
        "type": "Venture Capital",
        "description": "...",
        "investmentsCount": 150,
        "leadsCount": 45,
        "totalRaised": 5000000000,
        "medianRoi": 2.5,
        "links": {...},
        "image": {...}
    }
    """
    results = []
    
    for inv in data:
        inv_key = inv.get('key')
        inv_name = inv.get('name')
        
        if not inv_key or not inv_name:
            continue
        
        key = f"cryptorank:investor:{inv_key}"
        
        # Parse links
        links = inv.get('links') or {}
        
        doc = {
            'key': key,
            'source': 'cryptorank',
            'source_key': inv_key,
            
            'name': inv_name,
            'slug': inv_key,
            
            'tier': inv.get('tier'),
            'type': inv.get('type'),
            'description': inv.get('description'),
            
            # Stats - very valuable for VC scoring
            'investments_count': inv.get('investmentsCount') or inv.get('investments_count') or 0,
            'leads_count': inv.get('leadsCount') or inv.get('leads_count') or 0,
            'total_raised': inv.get('totalRaised') or inv.get('total_raised'),
            'median_roi': inv.get('medianRoi') or inv.get('median_roi'),
            
            # Links
            'website': links.get('website'),
            'twitter': links.get('twitter'),
            
            # Image
            'image': inv.get('image', {}).get('native') if isinstance(inv.get('image'), dict) else None,
            
            'raw': inv
        }
        
        results.append(doc)
    
    return results
