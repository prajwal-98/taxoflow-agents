

import streamlit as st
import pandas as pd

def render_sidebar():
    st.markdown("""
    <style>
        /* Reduce the gap between all elements in the sidebar */
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 1 rem;
        }
        /* Reduce margins for headers specifically */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            margin-bottom: 13px;
            padding-bottom: 5px;
        }
        /* Reduce top margin of the radio button and file uploader */
        .stRadio, .stFileUploader {
            margin-top: -15px;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- TITLE ---
    st.sidebar.title("UrbanPulse")
    st.sidebar.caption("Multi-Agent Intelligence")

    # --- MODE ---
    st.sidebar.markdown("## Mode")
    app_mode = st.sidebar.radio(
        "",
        options=["Live API", "Demo Mode"],
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )
    st.sidebar.container(height=5, border=False)

    uploaded_file = st.sidebar.file_uploader(
        "",
        type=["csv"],
        label_visibility="collapsed"
    )


    df = st.session_state.raw_df if "raw_df" in st.session_state else None

    if df is None:
        st.sidebar.caption("No data loaded")
    else:
        st.sidebar.caption(f"{len(df):,} reviews loaded")

    # --- FILTERS ---
    if df is not None:

        st.sidebar.markdown("## Filter Data")

        is_locked = st.session_state.get('filters_locked', False)

        required_cols = {"date", "city", "platform", "category", "raw_text"}

        if not required_cols.issubset(set(df.columns)):
            st.sidebar.error("Dataset missing required columns")
        else:
            working_df = df.copy()

            if not pd.api.types.is_datetime64_any_dtype(working_df["date"]):
                working_df["date"] = pd.to_datetime(working_df["date"], errors="coerce")

            working_df = working_df.dropna(subset=["date"])

            if working_df.empty:
                st.sidebar.error("No valid rows available")
            else:
                abs_min = working_df["date"].min().date()
                abs_max = working_df["date"].max().date()

                # --- DATE ---
                date_selection = st.sidebar.date_input(
                    "Date",
                    value=(abs_min, abs_max),
                    min_value=abs_min,
                    max_value=abs_max,
                    disabled=is_locked
                )

                def get_opts(col):
                    return sorted(working_df[col].dropna().unique().tolist())

                # --- CITY ---
                selected_cities = st.sidebar.multiselect(
                    "City",
                    options=get_opts('city'),
                    default=[],
                    placeholder="All",
                    disabled=is_locked,
                    max_selections=3
                )

                # --- PLATFORM ---
                selected_platforms = st.sidebar.multiselect(
                    "Platform",
                    options=get_opts('platform'),
                    default=[],
                    placeholder="All",
                    disabled=is_locked,
                    max_selections=3
                )

                # --- CATEGORY ---
                selected_categories = st.sidebar.multiselect(
                    "Category",
                    options=get_opts('category'),
                    default=[],
                    placeholder="All",
                    disabled=is_locked,
                    max_selections=3
                )

                # --- FILTER CALCULATION ---
                temp_df = working_df.copy()

                if selected_cities:
                    temp_df = temp_df[temp_df['city'].isin(selected_cities)]

                if selected_platforms:
                    temp_df = temp_df[temp_df['platform'].isin(selected_platforms)]

                if selected_categories:
                    temp_df = temp_df[temp_df['category'].isin(selected_categories)]

                if isinstance(date_selection, (list, tuple)) and len(date_selection) == 2:
                    temp_df = temp_df[
                        (temp_df['date'].dt.date >= date_selection[0]) &
                        (temp_df['date'].dt.date <= date_selection[1])
                    ]

                row_count = len(temp_df)

                # --- DATA SIZE ---
                st.sidebar.caption(f"Dataset Size: {row_count:,}")

                # Decide button style based on data
                button_type = "primary" if row_count > 0 else "secondary"
                # --- BUTTONS ---
                if not is_locked:
                    if st.sidebar.button("🔒 Lock & Run Pipeline",use_container_width=True,type=button_type):
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
                            st.sidebar.caption("No data selected")
                else:
                    st.sidebar.success("Filters Locked")

                    if st.sidebar.button(
                        "Reset Filters",
                        use_container_width=True
                    ):
                        st.session_state.filters_locked = False
                        st.rerun()

    return uploaded_file, app_mode
