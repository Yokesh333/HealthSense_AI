import abc
import logging
import urllib.parse
from typing import List, Dict, Any

import httpx
from backend.config import WEB_SEARCH_MAX_RESULTS, WEB_SEARCH_TIMEOUT, WEB_SEARCH_RECENCY_DAYS

logger = logging.getLogger(__name__)

class BaseWebIntelligenceService(abc.ABC):
    @abc.abstractmethod
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Searches external web sources and returns structured results."""
        pass


class PubMedWebIntelligenceService(BaseWebIntelligenceService):
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.max_results = WEB_SEARCH_MAX_RESULTS
        self.timeout = WEB_SEARCH_TIMEOUT
        self.recency_days = WEB_SEARCH_RECENCY_DAYS
        
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Uses NCBI PubMed E-utilities to retrieve recent peer-reviewed articles.
        Returns a list of structured results.
        """
        if not query or not query.strip():
            return []
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Step 1: esearch
                esearch_url = f"{self.base_url}/esearch.fcgi"
                params = {
                    "db": "pubmed",
                    "term": f"{query} AND (\"last {self.recency_days} days\"[dp])",
                    "retmode": "json",
                    "retmax": self.max_results
                }
                
                logger.info("WebIntelligenceService: Searching PubMed with query='%s'", query)
                search_resp = await client.get(esearch_url, params=params)
                search_resp.raise_for_status()
                search_data = search_resp.json()
                
                id_list = search_data.get("esearchresult", {}).get("idlist", [])
                
                if not id_list:
                    logger.info("WebIntelligenceService: No PubMed results found.")
                    return []
                    
                # Step 2: esummary
                esummary_url = f"{self.base_url}/esummary.fcgi"
                summary_params = {
                    "db": "pubmed",
                    "id": ",".join(id_list),
                    "retmode": "json"
                }
                
                summary_resp = await client.get(esummary_url, params=summary_params)
                summary_resp.raise_for_status()
                summary_data = summary_resp.json()
                
                results = []
                docs = summary_data.get("result", {})
                for uid in id_list:
                    if uid in docs:
                        doc = docs[uid]
                        title = doc.get("title", "")
                        source = doc.get("source", "PubMed")
                        pubdate = doc.get("pubdate", "")
                        
                        # Get abstract/snippet if available, or just fallback
                        # esummary doesn't always have full abstract, but it's enough metadata
                        snippet = f"PubMed Article from {source}, published {pubdate}."
                        
                        results.append({
                            "title": title,
                            "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                            "source": source,
                            "domain": "pubmed.ncbi.nlm.nih.gov",
                            "published_date": pubdate,
                            "snippet": snippet,
                            "trust_indicator": "PubMed/NIH Authority"
                        })
                        
                return results

        except httpx.TimeoutException:
            logger.error("WebIntelligenceService: PubMed API timed out.")
            return []
        except httpx.HTTPError as e:
            logger.error("WebIntelligenceService: PubMed API HTTP error: %s", str(e))
            return []
        except Exception as e:
            logger.error("WebIntelligenceService: Unexpected error: %s", str(e))
            return []
