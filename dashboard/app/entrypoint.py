"""Entrypoint do dashboard
com streamlit multi página.
"""

from datetime import date

import streamlit as st
from app.config import ST_CONFIG as config

# Set page global configuration
st.set_page_config(page_title=config.PAGE_TITLE, layout=config.PAGE_LAYOUT)

# Configure navigation bar
st.sidebar.markdown(f"> _Data do sistema: {date.today().strftime(config.DATE_FORMAT)}_")
pg = st.navigation(
    [
        # st.Page("dashboard/pages/home.py", title="Home", icon=":material/home:"),
        # st.Page(
        #    "dashboard/pages/economic_index.py",
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

# Run selected page
pg.run()
