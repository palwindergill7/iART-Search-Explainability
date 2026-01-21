"""
# search_proto_type/proto_type_main.py

"Streamlit UI for Artwork Explorer"

pip install streamlit

run script as -

streamlit run proto_type_main.py --logger.level=debug

"""

import streamlit as st
# my Custom SearchArtWorks Class
from SearchArtWorks import SearchArtWorks


def main():
    st.set_page_config(page_title="Artwork Explorer", layout="wide")
    
    st.title("🎨 Artwork Explorer [ via Wikidata ]")
    st.markdown("Search for artworks by title, artist, or description. Results from Wikidata.")
    
    # Initialize SearchArtworks class
    searcher = SearchArtWorks()
    
    # UI code for - Sidebar controls
    with st.sidebar:
        st.header("Search Settings")
        search_phrase = st.text_input(
            "Search phrase:", 
            #current DEFAULT
            value="civilization",
            help="Enter artwork title, artist name, or descriptive terms"
        )
        
        limit = st.slider("Number of results:", 1, 150, 200)
        
        search_button = st.button("🔍 Search Wikidata", type="primary")
        
        st.divider()
        st.markdown("**Search Tips:**")
        st.markdown("- Use quotes for exact phrases: `\"The Scream\"`")
        st.markdown("- Artist searches: `van Gogh` or `Rembrandt`")
        st.markdown("- Style searches: `impressionism` or `renaissance`")
    
    # UI code for - Main content area
    if search_button or 'results_df' in st.session_state:
        if search_button:
            with st.spinner(f"Searching Wikidata for '{search_phrase}'..."):
                # SPARQL query
                results = searcher.search_wikidata_artworks(search_phrase, limit)
                
                if results:
                    # store results
                    df = searcher.process_sparql_results(results)
                    st.session_state.results_df = df
                    st.session_state.search_phrase = search_phrase
                else:
                    st.warning("No results found. Try a different search term.")
                    return
        
        # Display results if available
        if 'results_df' in st.session_state and not st.session_state.results_df.empty:
            df = st.session_state.results_df
            
            st.subheader(f"Found {len(df)} artworks for '{st.session_state.search_phrase}'")
            
            # Results summary table
            with st.expander("📋 Results Table", expanded=True):
                display_df = df[['title', 'artist', 'description']].copy()
                display_df['description'] = display_df['description'].str[:100] + '...'
                st.dataframe(display_df, use_container_width=True)
            
            # Grid of artwork cards
            st.subheader(f"🎨 Search Gallery:- \t\t{st.session_state.search_phrase}")
            cols = st.columns(3)
            
            for idx, row in df.iterrows():
                with cols[idx % 3]:
                    
                    # st.image(row['image_url'], caption=row['title'], use_container_width=True)
                    
                    if row['image_url']:
                        
                        st.image(row['image_url'], caption=row['title'], use_container_width=True)
                    else:
                        st.warning(f"No image available for: {row['title']}")
                    

                    
                    with st.expander("Details"):
                        st.markdown(f"**Artist:** {row['artist']}")
                        if row['description']:
                            st.markdown(f"**Description:** {row['description']}")
                        
                        # Action buttons
                        # TODO
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("📥 Select", key=f"select_{idx}"):
                                st.session_state.selected_artwork = row
                                st.success(f"Selected: {row['title']}")
                        
                        with col2:
                            wikidata_url = f"https://www.wikidata.org/wiki/{row['id']}"
                            st.markdown(f"[🔗 Wikidata]({wikidata_url})", unsafe_allow_html=True)
            
            st.divider()
            # col1 = st.columns(1)
            
            # with col1:
            if st.button("🔄 New Search"):
                st.session_state.pop('results_df', None)
                st.rerun()
            
        else:
            st.info("No artworks found. Try a different search term.")
    
    else:
        # Initial state - show examples
        st.info("💡 **Try these example searches one at a time:** ")
        # st.markdown("mona lisa OR van gogh OR impressionism OR renaissance portrait")
        examples = st.columns(4)
        example_searches = ["mona lisa", "van gogh", "ancient civilization", "renaissance portrait"]
        
        for col, example in zip(examples, example_searches):
            with col:
                if st.button(f"{example}", use_container_width=True):
                    st.session_state.quick_search = example
                    st.rerun()
        
        st.divider()
        st.markdown("""
        ### How could we integrate this next for iART xAI project:
        1. **Search Interface** 
            -- Gets user's search phrase
        2. **SPARQL Engine** 
                    -- Queries Wikidata for matching artworks
        3. **Results Processing** 
                    -- Extracts structured data (title, image, artist)
        4. **PROBABLY steps TODO** 
                    -- Use this data for:\n
           **[ a ]** \t Model [ SigLip ? ] involment   \n 
           **[ b ]** \t ICC ++ (Scean Graph)   \n
           **[ c ]** \t Image similarity comparisons in iART   \n
           **[ d ]** \t Metadata enrichment for explanations   \n
           **[ e ]** . . . other TODO's
        """)


if __name__ == "__main__":
    main()

# import streamlit as st
# import requests
# import pandas as pd
# from urllib.parse import quote
# import json

# # ---- SPARQL QUERY FUNCTION ----
# def search_wikidata_artworks(search_term, limit):
#     """
#     Search Wikidata for paintings matching the search phrase
#     Returns: List of dictionaries with artwork data
#     """
#     # URL-encode the search term
#     encoded_search = quote(search_term)
    
#     #here, passing the query
#     query = f"""
#             SELECT ?artwork ?artworkLabel ?image ?description ?artist ?artistLabel WHERE {{
#             SERVICE wikibase:mwapi {{
#                 bd:serviceParam wikibase:endpoint "www.wikidata.org";
#                                 wikibase:api "Generator";
#                                 mwapi:generator "search";
#                                 mwapi:gsrsearch "{search_term}";
#                                 mwapi:gsrlimit "50".  # Get more initially, filter later
#                 ?artwork wikibase:apiOutputItem mwapi:title.
#             }}
            
#             # Filter to paintings with images
#             ?artwork wdt:P31/wdt:P279* wd:Q3305213;  # Instance of painting or subclass
#                     wdt:P18 ?image.
                    
#             # Optional: get description and artist
#             OPTIONAL {{ ?artwork schema:description ?description. 
#                         FILTER(LANG(?description) = "en") }}
#             OPTIONAL {{ ?artwork wdt:P170 ?artist. }}
            
#             SERVICE wikibase:label {{ 
#                 bd:serviceParam wikibase:language "en". 
#                 ?artist rdfs:label ?artistLabel.
#             }}
#             }}
#             LIMIT {limit}
#         """
    
#     # Debug: print the query @terminal
#     if st.session_state.get('debug_mode', False):
#         st.code(query, language='sparql')
    
#     # the SPARQL request
#     url = "https://query.wikidata.org/sparql"
#     #IMPORTANT
#     headers = {
#         'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)',
#         "Accept": "application/sparql-results+json",
#         "Content-Type": "application/sparql-query"
#     }
    
#     try:
#         response = requests.post(url, data=query.encode('utf-8'), headers=headers, timeout=30)
        
#         if response.status_code == 200:
#             return response.json()
#         else:
#             st.error(f"SPARQL Error {response.status_code}: {response.text[:200]}")
#             return None
            
#     except requests.exceptions.Timeout:
#         st.error("Query timeout - try a simpler search term")
#         return None
#     except Exception as e:
#         st.error(f"Connection error: {e}")
#         return None

# # --- DATA PROCESSING --
# def process_sparql_results(sparql_results):
#     """
#     Converting SPARQL JSON results responses to a DataFrame
#     """
#     if not sparql_results or 'results' not in sparql_results:
#         return pd.DataFrame()
    
#     bindings = sparql_results['results']['bindings']
#     processed = []
    
#     for item in bindings:
#         # extracting Q-id from artwork URI
#         artwork_uri = item.get('artwork', {}).get('value', '')
#         q_id = artwork_uri.split('/')[-1] if '/' in artwork_uri else artwork_uri
        
#         processed.append({
#             'id': q_id,
#             'title': item.get('artworkLabel', {}).get('value', 'Unknown'),
#             'image_url': item.get('image', {}).get('value', ''),
#             'description': item.get('description', {}).get('value', ''),
#             'artist': item.get('artistLabel', {}).get('value', 'Unknown'),
#             'wikidata_url': artwork_uri
#         })
    
#     return pd.DataFrame(processed)

# # -- STREAMLET UI --
# def main():
#     st.set_page_config(page_title="Artwork Explorer", layout="wide")
    
#     st.title("🎨 Artwork Explorer via Wikidata Search")
#     st.markdown("Search for artworks by title, artist, or description. Results from Wikidata.")
    
#     # UI code for - Sidebar controls
#     with st.sidebar:
#         st.header("Search Settings")
#         search_phrase = st.text_input(
#             "Search phrase:", 
#             value="starry night",
#             help="Enter artwork title, artist name, or descriptive terms"
#         )
        
#         limit = st.slider("Number of results:", 1, 150, 200)
        
#         search_button = st.button("🔍 Search Wikidata", type="primary")
        
#         st.divider()
#         st.markdown("**Search Tips:**")
#         st.markdown("- Use quotes for exact phrases: `\"The Scream\"`")
#         st.markdown("- Artist searches: `van Gogh` or `Rembrandt`")
#         st.markdown("- Style searches: `impressionism` or `renaissance`")
    
#     # UI code for - Main content area
#     if search_button or 'results_df' in st.session_state:
#         if search_button:
#             with st.spinner(f"Searching Wikidata for '{search_phrase}'..."):
#                 # SPARQL query
#                 results = search_wikidata_artworks(search_phrase, limit)
                
#                 if results:
#                     # store results
#                     df = process_sparql_results(results)
#                     st.session_state.results_df = df
#                     st.session_state.search_phrase = search_phrase
#                 else:
#                     st.warning("No results found. Try a different search term.")
#                     return
        
#         # Display results if available
#         if 'results_df' in st.session_state and not st.session_state.results_df.empty:
#             df = st.session_state.results_df
            
#             st.subheader(f"Found {len(df)} artworks for '{st.session_state.search_phrase}'")
            
#             # Results summary table
#             with st.expander("📋 Results Table", expanded=True):
#                 display_df = df[['title', 'artist', 'description']].copy()
#                 display_df['description'] = display_df['description'].str[:100] + '...'
#                 st.dataframe(display_df, use_container_width=True)
            
#             # Grid of artwork cards
#             st.subheader("🎨 Artwork Gallery")
#             cols = st.columns(3)
            
#             for idx, row in df.iterrows():
#                 with cols[idx % 3]:
#                     st.image(row['image_url'], caption=row['title'], use_column_width=True)
                    
                    
#                     with st.expander("Details"):
#                         st.markdown(f"**Artist:** {row['artist']}")
#                         if row['description']:
#                             st.markdown(f"**Description:** {row['description']}")
                        
#                         # Action buttons
#                         col1, col2 = st.columns(2)
#                         with col1:
#                             if st.button("📥 Select", key=f"select_{idx}"):
#                                 st.session_state.selected_artwork = row
#                                 st.success(f"Selected: {row['title']}")
                        
#                         with col2:
#                             wikidata_url = f"https://www.wikidata.org/wiki/{row['id']}"
#                             st.markdown(f"[🔗 Wikidata]({wikidata_url})", unsafe_allow_html=True)
            

#             st.divider()
#             col1 = st.columns(1)
            
#             with col1:
#                 if st.button("🔄 New Search"):
#                     st.session_state.pop('results_df', None)
#                     st.rerun()
            
#         else:
#             st.info("No artworks found. Try a different search term.")
    
#     else:
#         # Initial state - show examples
#         st.info("💡 **Try these example searches:**")
#         examples = st.columns(4)
#         example_searches = ["mona lisa", "van gogh", "impressionism", "renaissance portrait"]
        
#         for col, example in zip(examples, example_searches):
#             with col:
#                 if st.button(f"`{example}`", use_container_width=True):
#                     st.session_state.quick_search = example
#                     st.rerun()
        
#         st.divider()
#         st.markdown("""
#         ### How could we integrate this next for iART xAI project:
#         1. **Search Interface** 
#             -- Gets user's search phrase
#         2. **SPARQL Engine** 
#                     -- Queries Wikidata for matching artworks
#         3. **Results Processing** 
#                     -- Extracts structured data (title, image, artist)
#         4. **PROBABLY steps TODO** 
#                     -- Use this data for:
#            [ a ] Model (SigLip ?) involment
#            [ b ] ICC ++ (Scean Graph)
#            [ c ] Image similarity comparisons in iART
#            [ d ] Metadata enrichment for explanations
#         """)


# if __name__ == "__main__":
#     main()
