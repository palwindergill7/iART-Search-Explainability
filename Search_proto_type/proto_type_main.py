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