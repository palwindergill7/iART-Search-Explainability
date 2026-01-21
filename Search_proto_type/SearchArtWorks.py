"""
# search_proto_type/SearchArtWorks.py

Class for handling Wikidata SPARQL queries and artwork data processing

"""
import streamlit as st
import requests
import pandas as pd
from urllib.parse import quote



class SearchArtWorks:
    """
    A class to search and process artwork data from Wikidata
    """

    def __init__(self):
        
        self.SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
        
        # IMPORTANT
        self.HEADERS = {
            'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)',
            "Accept": "application/sparql-results+json",
            # SPECIFIC to SPARql
            "Content-Type": "application/sparql-query"
        }

        
        self.RESPONSE_STATUS_CODE = 200



    # ---- SPARQL QUERY FUNCTION ----
    def search_wikidata_artworks(self, search_term, limit):
        """
        Search Wikidata for paintings matching the search phrase
        Returns: List of dictionaries with artwork data
        """
        # URL-encode the search term
        encoded_search = quote(search_term)
        
        #here, passing the query
        query = f"""
                SELECT ?artwork ?artworkLabel ?image ?description ?artist ?artistLabel WHERE {{
                SERVICE wikibase:mwapi {{
                    bd:serviceParam wikibase:endpoint "www.wikidata.org";
                                    wikibase:api "Generator";
                                    mwapi:generator "search";
                                    mwapi:gsrsearch "{search_term}";
                                    mwapi:gsrlimit "250".               # we could Get more initially, filter later at UI (below)
                    ?artwork wikibase:apiOutputItem mwapi:title.
                }}
                
                # Filter to paintings with images
                ?artwork wdt:P31/wdt:P279* wd:Q3305213;  # Instance of painting or subclass
                        wdt:P18 ?image.
                        
                # Optional: get description and artist
                OPTIONAL {{ ?artwork schema:description ?description. 
                            FILTER(LANG(?description) = "en") }}
                OPTIONAL {{ ?artwork wdt:P170 ?artist. }}
                
                SERVICE wikibase:label {{ 
                    bd:serviceParam wikibase:language "en". 
                    ?artist rdfs:label ?artistLabel.
                }}
                }}
                LIMIT {limit}               # filter limit at UI
            """
        print(f"-----------{query}")
        
        # Debug: print the query @terminal
        if st.session_state.get('debug_mode', False):
            st.code(query, language='sparql')
        
        # the SPARQL request
        try:
            response = requests.post(self.SPARQL_ENDPOINT, data=query.encode('utf-8'), 
                                   headers=self.HEADERS, timeout=30)
            
            #checicking for result of response
            if response.status_code == self.RESPONSE_STATUS_CODE:
                return response.json()
            else:
                st.error(f"SPARQL Error {response.status_code}: {response.text[:200]}")
                return None
                
        except requests.exceptions.Timeout:
            st.error("Query timeout - try a simpler search term")
            return None
        except Exception as e:
            st.error(f"Connection error: {e}")
            return None
    


    def process_sparql_results(self, sparql_results):
        """
        Converting SPARQL JSON results responses to a DataFrame
        """
        if not sparql_results or 'results' not in sparql_results:
            return pd.DataFrame()
        
        bindings = sparql_results['results']['bindings']
        processed = []
        
        for item in bindings:
            # extracting Q-id from artwork URI
            artwork_uri = item.get('artwork', {}).get('value', '')
            q_id = artwork_uri.split('/')[-1] if '/' in artwork_uri else artwork_uri
            
            processed.append({
                'id': q_id,
                'title': item.get('artworkLabel', {}).get('value', 'Unknown'),
                'image_url': item.get('image', {}).get('value', ''),
                'description': item.get('description', {}).get('value', ''),
                'artist': item.get('artistLabel', {}).get('value', 'Unknown'),
                'wikidata_url': artwork_uri
            })
        
        return pd.DataFrame(processed)