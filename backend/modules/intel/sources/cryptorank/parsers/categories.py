"""
Categories parser for CryptoRank
"""

from typing import Dict, List, Any


def parse_categories(data: List[Dict]) -> List[Dict]:
    """
    Parse categories from CryptoRank.
    
    Expected input format (from /v1/categories):
    {
        "key": "defi",
        "name": "DeFi",
        "description": "Decentralized Finance protocols",
        "coinsCount": 500,
        "marketCap": 80000000000,
        "volume24h": 5000000000,
        "percentChange24h": 2.5
    }
    """
    results = []
    
    for cat in data:
        cat_key = cat.get('key')
        cat_name = cat.get('name')
        
        if not cat_key or not cat_name:
            continue
        
        key = f"cryptorank:category:{cat_key}"
        
        doc = {
            'key': key,
            'source': 'cryptorank',
            'source_key': cat_key,
            
            'name': cat_name,
            'slug': cat_key,
            'description': cat.get('description'),
            
            # Stats
            'coins_count': cat.get('coinsCount') or cat.get('coins_count') or 0,
            'market_cap': cat.get('marketCap') or cat.get('market_cap'),
            'volume_24h': cat.get('volume24h') or cat.get('volume_24h'),
            'change_24h': cat.get('percentChange24h') or cat.get('percent_change_24h'),
            
            'raw': cat
        }
        
        results.append(doc)
    
    return results
