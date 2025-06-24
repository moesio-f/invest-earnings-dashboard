"""Entrypoint do dashboard
com streamlit multi página.
"""

from datetime import date

import streamlit as st
from app import patches
from app.config import ST_CONFIG as config
from app.utils.state import Manager

# Set page global configuration
st.set_page_config(page_title=config.PAGE_TITLE, layout=config.PAGE_LAYOUT)

# Configure navigation bar
st.sidebar.markdown(f"> _Data do sistema: {date.today().strftime(config.DATE_FORMAT)}_")
pg = st.navigation(
    [
        st.Page("analytics/pages/home.py", title="Home", icon=":material/home:"),
        # st.Page(
        #    "analytics/pages/economic_index.py",
        #    title="Rentabilidade vs Indicadores",
        #    icon=":material/monitoring:",
        # ),
        st.Page("wallet/pages/positions.py", title="Posição", icon=":material/wallet:"),
        st.Page(
            "wallet/pages/settings.py",
            title="Configurações",
            icon=":material/settings:",
        ),
    ],
    expanded=False,
)

# Clear all pages
Manager.clear_pages(destroy=True)

# Apply patches
patches.apply_streamlit_patches()

# Run selected page
pg.run()
