import streamlit as st
import pandas as pd

def render_sidebar():
    st.sidebar.title("📌 UrbanPulse")
    st.sidebar.markdown("*Multi-Agent Intelligent System*")
    st.sidebar.divider()

    # --- Section 1: Dataset ---
    st.sidebar.header("🔹 Section 1: Dataset")
    uploaded_file = st.sidebar.file_uploader("Upload Dataset (CSV)", type=["csv"])
    
    # Read dataframe directly from session state
    df = st.session_state.raw_df if "raw_df" in st.session_state else None

    if df is None:
        st.sidebar.warning("Upload data to enable dynamic filters.")
    else:
        # --- Section 2: Global Filters (ONLY shows if df exists) ---
        st.sidebar.success("✅ Data Active")
        st.sidebar.header("🔒 Global Filters")
        
        is_locked = st.session_state.get('filters_locked', False)

        required_cols = {"date", "city", "platform", "category", "raw_text"}
        if not required_cols.issubset(set(df.columns)):
            st.sidebar.error("Dataset missing required columns: date, city, platform, category, raw_text")
        else:
            working_df = df.copy()
            if not pd.api.types.is_datetime64_any_dtype(working_df["date"]):
                working_df["date"] = pd.to_datetime(working_df["date"], errors="coerce")
            working_df = working_df.dropna(subset=["date"])

            if working_df.empty:
                st.sidebar.error("No valid rows available after parsing date column.")
            else:
                abs_min = working_df["date"].min().date()
                abs_max = working_df["date"].max().date()
                
                date_selection = st.sidebar.date_input(
                    "Date Range", 
                    value=(abs_min, abs_max),
                    min_value=abs_min,
                    max_value=abs_max,
                    disabled=is_locked
                )
                
                # Dynamic helper to get unique options
                def get_opts(col):
                    return sorted(working_df[col].dropna().unique().tolist())

                selected_cities = st.sidebar.multiselect(
                    "Cities", options=get_opts('city'), 
                    default=get_opts('city'), disabled=is_locked
                )
                
                selected_platforms = st.sidebar.multiselect(
                    "Platforms", options=get_opts('platform'), 
                    default=get_opts('platform'), disabled=is_locked
                )

                selected_categories = st.sidebar.multiselect(
                    "Categories", options=get_opts('category'), 
                    default=get_opts('category'), disabled=is_locked
                )

                # --- Section 3: Live Selection Stats ---
                st.sidebar.divider()
                
                # Filtering temp_df for the progress bar
                temp_df = working_df.copy()
                if selected_cities: temp_df = temp_df[temp_df['city'].isin(selected_cities)]
                if selected_platforms: temp_df = temp_df[temp_df['platform'].isin(selected_platforms)]
                if selected_categories: temp_df = temp_df[temp_df['category'].isin(selected_categories)]
                
                if isinstance(date_selection, (list, tuple)) and len(date_selection) == 2:
                    temp_df = temp_df[(temp_df['date'].dt.date >= date_selection[0]) & 
                                      (temp_df['date'].dt.date <= date_selection[1])]

                row_count = len(temp_df)
                st.sidebar.metric("Rows Selected", f"{row_count:,}")
                st.sidebar.progress(row_count / len(working_df) if len(working_df) > 0 else 0)

                # Lock/Unlock Mechanism
                if not is_locked:
                    if st.sidebar.button("Lock & Run Pipeline", use_container_width=True, type="primary"):
                        if row_count > 0:
                            st.session_state.filters_locked = True
                            st.session_state.active_filters = {
                                "date_range": date_selection,
                                "city": selected_cities,
                                "platform": selected_platforms,
                                "category": selected_categories
                            }
                            st.session_state.current_step = 1
                            st.rerun()
                        else:
                            st.sidebar.error("0 rows selected!")
                else:
                    if st.sidebar.button("Unlock & Reset", use_container_width=True):
                        st.session_state.filters_locked = False
                        st.rerun()

    return uploaded_file