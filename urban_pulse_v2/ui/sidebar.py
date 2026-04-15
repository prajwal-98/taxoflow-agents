

import streamlit as st
import pandas as pd

_IC_CAL = """<svg class="up-sb-ic" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#737373" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>"""
_IC_PIN = """<svg class="up-sb-ic" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#737373" stroke-width="1.5"><path d="M12 21s7-4.5 7-11a7 7 0 1 0-14 0c0 6.5 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>"""
_IC_LAY = """<svg class="up-sb-ic" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#737373" stroke-width="1.5"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5M2 12l10 5 10-5"/></svg>"""
_IC_TAG = """<svg class="up-sb-ic" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#737373" stroke-width="1.5"><path d="M12 2H2v10l10 10 10-10L12 2z"/><circle cx="7" cy="7" r="1.5" fill="#737373" stroke="none"/></svg>"""


def _sb_br(count: int = 1) -> None:
    st.sidebar.markdown("<br>" * count, unsafe_allow_html=True)


def _scope_field_label(icon_html: str, text: str) -> None:
    st.sidebar.markdown(
        f'<div class="up-sb-field-hint">{icon_html}<span>{text}</span></div>',
        unsafe_allow_html=True,
    )


def render_sidebar():
    # Scoped theme only — do NOT set gap/margin on all stVerticalBlock (breaks nested widgets / overlap).
    st.markdown(
        """
    <style>
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] > div,
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            background-color: #000000 !important;
        }
        [data-testid="stSidebar"] h1 {
            font-size: 1.35rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            margin: 0 0 0.2rem 0 !important;
            padding: 0 !important;
            letter-spacing: -0.02em;
            line-height: 1.2 !important;
        }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] div[data-testid="stCaption"] {
            color: #888888 !important;
            font-size: 0.8rem !important;
            margin-top: 0 !important;
        }
        .up-sb-section {
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.1em !important;
            text-transform: uppercase !important;
            color: #737373 !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1.2 !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] {
            margin-top: -1.5 rem !important;
        
        .up-sb-field-hint {
            display: flex !important;
            align-items: center !important;
            gap: 0.45rem !important;
            margin: 0.4rem 0 0.15rem 0 !important;
            color: #737373 !important;
            font-size: 0.78rem !important;
            line-height: 1.2 !important;
        }
        .up-sb-field-hint .up-sb-ic { flex-shrink: 0; opacity: 0.95; }
        .up-upload-status {
            font-size: 0.78rem !important;
            color: #00C87E !important;
            margin: 0.25rem 0 0 0 !important;
            padding: 0 !important;
            line-height: 1.3 !important;
        }
        .up-upload-status--muted {
            color: #737373 !important;
        }
        .up-dataset-size {
            font-size: 0.72rem !important;
            color: #737373 !important;
            margin: 0.5rem 0 0.35rem 0 !important;
        }
        /* MODE — horizontal radio uses stHorizontalBlock in Streamlit 1.5x; avoid flex hacks on wrong wrappers. */
        [data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stHorizontalBlock"] {
            background: #2a2a2a !important;
            padding: 4px !important;
            border-radius: 8px !important;
            gap: 6px !important;
            align-items: stretch !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="column"] {
            padding: 0 2px !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 !important;
            padding: 0.26rem 0.3rem !important;
            border-radius: 6px !important;
            font-size: 0.7rem !important;
            font-weight: 600 !important;
            color: #a3a3a3 !important;
            background: transparent !important;
            line-height: 1.2 !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label p {
            color: inherit !important;
            font-size: inherit !important;
            margin: 0 !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
            background: #404040 !important;
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {
            color: #ffffff !important;
        }
        /* Upload — only the dropzone shell (no nested VerticalBlock hacks). */
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
            border: 1px solid #00C87E !important;
            border-radius: 10px !important;
            background: #1a1a1a !important;
            padding: 0.25rem 0.45rem !important;
            line-height: 1.1 !important;
        }
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] p {
            font-size: 0.74rem !important;
            margin: 0.1rem 0 !important;
            line-height: 1.25 !important;
        }
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small {
            font-size: 0.65rem !important;
            color: #888888 !important;
        }
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
            padding: 0.22rem 0.5rem !important;
            font-size: 0.68rem !important;
        }
        /* Compact scope widgets */
        [data-testid="stSidebar"] .stDateInput [data-baseweb="input"] {
            min-height: 2.1rem !important;
            font-size: 0.8rem !important;
            border-radius: 999px !important;
            background-color: #1a1a1a !important;
            border-color: #333333 !important;
        }
        [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div {
            min-height: 2.1rem !important;
            font-size: 0.8rem !important;
            border-radius: 999px !important;
            background-color: #1a1a1a !important;
            border-color: #333333 !important;
        }
        [data-testid="stSidebar"] button[kind="primary"] {
            background-color: #00C87E !important;
            color: #000000 !important;
            border: none !important;
            font-weight: 700 !important;
            border-radius: 10px !important;
            padding: 0.5rem 1rem !important;
            font-size: 0.82rem !important;
        }
        [data-testid="stSidebar"] button[kind="primary"]:hover {
            background-color: #00e08f !important;
            color: #000000 !important;
        }
        [data-testid="stSidebar"] button[kind="secondary"] {
            background-color: #2a2a2a !important;
            color: #a3a3a3 !important;
            border: 1px solid #404040 !important;
            border-radius: 10px !important;
            font-size: 0.82rem !important;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # --- HEADER ---
    st.sidebar.title("UrbanPulse")
    st.sidebar.caption("Multi-Agent Intelligence")
    st.sidebar.divider()
    uploaded_file = None

    # --- MODE (TOP PRIORITY) ---
    st.sidebar.markdown(
        '<p class="up-sb-section">MODE</p>', unsafe_allow_html=True
    )

    app_mode = st.sidebar.radio(
        "",
        options=["Demo Mode", "Live API"],  # Demo first
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )

    # --- LIVE MODE BLOCK ---
    if app_mode == "Live API":

        # API KEY
        st.sidebar.markdown(
            '<p class="up-sb-section">API KEY</p>', unsafe_allow_html=True
        )

        api_key = st.sidebar.text_input(
            "",
            type="password",
            label_visibility="collapsed"
        )

        st.session_state.api_key = api_key

        # MODEL
        st.sidebar.markdown(
            '<p class="up-sb-section">MODEL</p>', unsafe_allow_html=True
        )

        model = st.sidebar.selectbox(
            "",
            ["gemini-3.1-flash-lite-preview", "gemini-1.5-flash", "gemini-1.5-pro"],
            disabled=not bool(api_key),
            label_visibility="collapsed"
        )

        st.session_state.model = model

        # _sb_br(1)

        # --- FILE UPLOAD (EPHEMERAL) ---
        if not st.session_state.get("file_uploaded", False):

            uploaded_file = st.sidebar.file_uploader(
                "",
                type=["csv"],
                label_visibility="collapsed"
            )

            if uploaded_file is not None:
                st.session_state.file_uploaded = True
                st.session_state.uploaded_file = uploaded_file
                st.rerun()

        else:
            # GREEN SUCCESS BANNER
            st.sidebar.markdown(
            """
            <div style="
                background: rgba(0, 200, 126, 0.12);
                color: #00C87E;
                padding: 6px 10px;
                border-radius: 6px;
                font-size: 0.75rem;
                font-weight: 500;
                text-align: center;
                margin: 6px 0;
                border: 1px solid rgba(0, 200, 126, 0.3);
            ">
                Data loaded successfully
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- DEMO MODE ---
    else:
        st.session_state.file_uploaded = False

        # GREEN DEMO BANNER
        st.sidebar.markdown(
        """
        <div style="
            background: rgba(255, 255, 255, 0.06);
            color: #00C87E;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 500;
            text-align: center;
            margin: 6px 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        ">
            Using demo dataset
        </div>
        """,
        unsafe_allow_html=True
    )

    _sb_br(1)
    
    df = st.session_state.raw_df if "raw_df" in st.session_state else None

    # --- Data scope & actions (stacked; no overlap) ---
    if df is not None:
        st.sidebar.markdown(
            '<p class="up-sb-section">DATA SCOPE</p>', unsafe_allow_html=True
        )
        # _sb_br(1)

        is_locked = st.session_state.get("filters_locked", False)

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

                # _scope_field_label(_IC_CAL, "Date Range")
                date_selection = st.sidebar.date_input(
                    "Date",
                    value=(abs_min, abs_max),
                    min_value=abs_min,
                    max_value=abs_max,
                    disabled=is_locked,
                    label_visibility="collapsed",
                )
                # _sb_br(1)

                def get_opts(col):
                    return sorted(working_df[col].dropna().unique().tolist())

                # _scope_field_label(_IC_PIN, "City")
                selected_cities = st.sidebar.multiselect(
                    "City",
                    options=get_opts("city"),
                    default=[],
                    placeholder="City",
                    disabled=is_locked,
                    max_selections=3,
                    label_visibility="collapsed",
                )
                # _sb_br(1)

                # _scope_field_label(_IC_LAY, "Platform")
                selected_platforms = st.sidebar.multiselect(
                    "Platform",
                    options=get_opts("platform"),
                    default=[],
                    placeholder="Platform",
                    disabled=is_locked,
                    max_selections=3,
                    label_visibility="collapsed",
                )
                # _sb_br(1)

                # _scope_field_label(_IC_TAG, "Category")
                selected_categories = st.sidebar.multiselect(
                    "Category",
                    options=get_opts("category"),
                    default=[],
                    placeholder="Category",
                    disabled=is_locked,
                    max_selections=3,
                    label_visibility="collapsed",
                )
                # _sb_br(1)

                temp_df = working_df.copy()

                if selected_cities:
                    temp_df = temp_df[temp_df["city"].isin(selected_cities)]

                if selected_platforms:
                    temp_df = temp_df[temp_df["platform"].isin(selected_platforms)]

                if selected_categories:
                    temp_df = temp_df[temp_df["category"].isin(selected_categories)]

                if isinstance(date_selection, (list, tuple)) and len(date_selection) == 2:
                    temp_df = temp_df[
                        (temp_df["date"].dt.date >= date_selection[0])
                        & (temp_df["date"].dt.date <= date_selection[1])
                    ]

                row_count = len(temp_df)

                st.sidebar.markdown(
                    f'<p class="up-dataset-size">Dataset Size: {row_count:,}</p>',
                    unsafe_allow_html=True,
                )
                # _sb_br(1)

                is_demo = (app_mode == "Demo Mode")
                has_api_key = bool(st.session_state.get("api_key"))

                button_disabled = (
                    is_demo or
                    (app_mode == "Live API" and not has_api_key) or
                    row_count == 0
                )
                button_type = "primary" if not button_disabled else "secondary"
                if not is_locked:
                    if st.sidebar.button(
                        "Lock & Run Pipeline",
                        use_container_width=True,
                        type=button_type,
                        disabled = button_disabled
                    ):
                        if row_count > 0:
                            st.session_state.filters_locked = True
                            st.session_state.active_filters = {
                                "date_range": date_selection,
                                "city": selected_cities,
                                "platform": selected_platforms,
                                "category": selected_categories,
                            }
                            st.session_state.current_step = 1
                            st.rerun()
                        else:
                            st.sidebar.caption("No data selected")
                else:
                    st.sidebar.success("Filters Locked")
                    # _sb_br(1)
                    if st.sidebar.button("Reset Filters", use_container_width=True):
                        st.session_state.filters_locked = False
                        st.rerun()

    return uploaded_file, app_mode
