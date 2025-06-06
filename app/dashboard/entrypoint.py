"""Entrypoint do dashboard
com streamlit multi página.
"""

from datetime import date

import streamlit as st

from app.config import DASHBOARD_CONFIG as config

# Set page global configuration
st.set_page_config(page_title=config.PAGE_TITLE, layout=config.PAGE_LAYOUT)

# Configure navigation bar
st.sidebar.markdown(f"> _Data do sistema: {date.today().strftime(config.DATE_FORMAT)}_")
pg = st.navigation(
    [
        st.Page("pages/home.py", title="Home", icon=":material/home:"),
        st.Page(
            "pages/economic_index.py",
            title="Rentabilidade vs Indicadores",
            icon=":material/monitoring:",
        ),
        st.Page(
            "pages/settings.py",
            title="Configurações",
            icon=":material/settings:",
        ),
    ],
    expanded=False,
)

# Maybe clear state on page change
if config.CLEAR_STATE_ON_PAGE_CHANGE:
    from app.dashboard.state import Manager

    Manager.clear_pages(destroy=True)

# Run selected page
pg.run()
