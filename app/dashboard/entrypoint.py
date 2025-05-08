"""Entrypoint do dashboard
com streamlit multi página.
"""

import streamlit as st

from app.config import DASHBOARD_CONFIG as config

# Set page global configuration
st.set_page_config(page_title=config.PAGE_TITLE, layout=config.PAGE_LAYOUT)

# Configure navigation bar
pg = st.navigation(
    [
        st.Page("pages/home.py", title="Home", icon=":material/home:"),
        st.Page(
            "pages/settings.py",
            title="Configurações",
            icon=":material/settings:",
        ),
    ]
)

# Maybe clear state on page change
if config.CLEAR_STATE_ON_PAGE_CHANGE:
    from app.dashboard.scoped_state import ScopedState

    ScopedState.clear_scopes(keep_no_initialize=True)

# Run selected page
pg.run()
