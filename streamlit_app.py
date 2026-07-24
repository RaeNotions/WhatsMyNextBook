import os
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(page_title="What's My Next Book?", page_icon="📖", layout="centered")

st.title("📖 What's My Next Book?")
st.write("Click genre tags below to narrow down your choices and draw a random recommendation!")

# Use absolute path relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "books.xlsx")
CSV_FILE = os.path.join(BASE_DIR, "books.csv")


@st.cache_data
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE).fillna("")
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE, engine="openpyxl").fillna("")
    raise FileNotFoundError("Could not find 'books.csv' or 'books.xlsx'")


try:
    df = load_data()

    # Extract all unique individual genre tags from the 'Genre' column
    all_tags = set()
    for genre_str in df['Genre']:
        tags = [t.strip() for t in str(genre_str).split(',') if t.strip()]
        all_tags.update(tags)
    
    unique_tags = sorted(list(all_tags))

    # --- BOX 1: INTERACTIVE TAG SELECTION PANEL ---
    st.markdown("### 🏷️ Box 1: Select Genre Tags")
    st.caption("Books must contain **ALL** selected tags:")

    # Multi-select for genre filtering
    selected_tags = st.multiselect(
        label="Selected Genres",
        options=unique_tags,
        default=[unique_tags[0]] if unique_tags else []
    )

    if selected_tags:
        st.write("Filtering for books with **ALL** of these tags:", " + ".join([f"`{tag}`" for tag in selected_tags]))
    else:
        st.info("💡 Please select at least one tag above to start filtering.")

    # Draw Button
    if st.button("🎲 Pick My Next Book!", type="primary", use_container_width=True):
        if not selected_tags:
            st.warning("Please select at least one genre tag in Box 1!")
        else:
            # Strict AND filtering: book must contain EVERY selected tag
            mask = pd.Series([True] * len(df))
            for tag in selected_tags:
                mask = mask & df['Genre'].astype(str).str.contains(rf"\b{tag}\b", case=False, regex=True)

            matches = df[mask]

            # --- BOX 2: RAFFLE RESULT PANEL ---
            st.markdown("---")
            st.markdown(f"### 🎁 Box 2: Your Next Read ({len(matches)} book{'s' if len(matches) != 1 else ''} found)")

            if matches.empty:
                st.error(f"No books match **ALL** selected tags: {', '.join(selected_tags)}")
            else:
                winner = matches.sample(n=1).iloc[0]

                # Render result card
                with st.container(border=True):
                    st.subheader(f"📖 {winner['Title']}")
                    st.caption(f"**Author:** {winner['Author']} | **Genre:** {winner['Genre']}")
                    st.markdown("**Summary:**")
                    st.write(winner['Summary'])

except FileNotFoundError:
    st.error(f"Could not find '{EXCEL_FILE}'. Please ensure 'books.xlsx' is committed to your repository root.")