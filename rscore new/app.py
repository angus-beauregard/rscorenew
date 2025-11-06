import streamlit as st
import pandas as pd
from utils.rscore import compute_rscore, compute_overall_rscore
from utils.course_data import load_course_credits
from utils.supabase_client import get_user_profile, user_has_subscription

st.set_page_config(page_title="R-Score Calculator", layout="wide")

# ====== TOP BAR / HERO ======
with st.container():
    st.markdown(
        """
        <h1 style="margin-bottom:0">CEGEP R-Score Calculator</h1>
        <p style="color:gray;margin-top:4px;">Enter your courses, get an accurate R-score. Unlock pro to bulk-import and save.</p>
        """,
        unsafe_allow_html=True,
    )

# ====== AUTH / PROFILE ======
# In your real repo, you probably get the user from cookies / headers / supabase-py.
# Here we just mock it from query params or a toggle.
st.sidebar.header("Account")

mock_email = st.sidebar.text_input("Email (mock for now)", value="student@example.com")

profile = get_user_profile(mock_email)
is_pro = user_has_subscription(profile)

if is_pro:
    st.sidebar.success("✅ Pro active")
else:
    st.sidebar.warning("Free plan – upgrade to unlock OCR & saving")

# ====== DATA SOURCES ======
course_credits_df = load_course_credits("course_credits_mapping.csv")

# ====== LAYOUT ======
tab_free, tab_pro = st.tabs(["🆓 Free calculator", "⭐ Pro features"])

# -------------------------------------------------------------------------
# FREE TAB
# -------------------------------------------------------------------------
with tab_free:
    st.subheader("Manual course entry")

    st.markdown("Add each course with the info from Omnivox / teacher. We'll compute per-course R and the weighted average.")

    # We'll let the user add multiple rows in a small editor
    num_rows = st.number_input("How many courses this session?", min_value=1, max_value=12, value=4)

    courses = []
    for i in range(num_rows):
        st.markdown(f"**Course {i+1}**")
        cols = st.columns(5)
        with cols[0]:
            course_name = st.text_input(f"Name {i+1}", key=f"name_{i}")
        with cols[1]:
            mark = st.number_input(f"Mark {i+1}", 0.0, 100.0, 85.0, key=f"mark_{i}")
        with cols[2]:
            group_avg = st.number_input(f"Group avg {i+1}", 0.0, 100.0, 75.0, key=f"avg_{i}")
        with cols[3]:
            group_sd = st.number_input(f"SD {i+1}", 0.0, 30.0, 8.0, key=f"sd_{i}")
        with cols[4]:
            # try to suggest credits from csv
            default_credits = 2.0
            if not course_credits_df.empty and course_name:
                match = course_credits_df[course_credits_df["course_name"].str.lower() == course_name.lower()]
                if not match.empty:
                    default_credits = float(match.iloc[0]["credits"])
            credits = st.number_input(f"Cr {i+1}", 0.5, 6.0, default_credits, key=f"cr_{i}")

        courses.append(
            {
                "course_name": course_name,
                "mark": mark,
                "group_avg": group_avg,
                "group_sd": group_sd,
                "credits": credits,
            }
        )
        st.divider()

    if st.button("Calculate R-score", type="primary"):
        df = pd.DataFrame(courses)
        # compute per-course r
        df["rscore"] = df.apply(
            lambda row: compute_rscore(
                row["mark"],
                row["group_avg"],
                row["group_sd"],
            ),
            axis=1,
        )
        overall = compute_overall_rscore(df)
        st.success(f"Your weighted R-score (approx): **{overall}**")
        st.dataframe(df[["course_name", "mark", "rscore", "credits"]])

        # optional: download
        st.download_button(
            "Download results (CSV)",
            data=df.to_csv(index=False),
            file_name="rscore_results.csv",
            mime="text/csv",
        )

# -------------------------------------------------------------------------
# PRO TAB
# -------------------------------------------------------------------------
with tab_pro:
    st.subheader("Pro tools")

    if not is_pro:
        st.info(
            "These tools are for subscribers.\n\n"
            "👉 Add Stripe → on success set `is_subscribed = true` in Supabase → this tab unlocks."
        )
        st.markdown(
            """
            <a href="https://buy.stripe.com/test_..." target="_blank">
                <button style="background:#4f46e5;color:white;border:none;padding:0.5rem 1rem;border-radius:0.4rem;cursor:pointer;">
                    Go to checkout
                </button>
            </a>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.success("Pro active – upload a screenshot / bulk CSV.")

        pro_mode = st.radio("What do you want to do?", ["Upload Omnivox screenshot (OCR)", "Bulk CSV upload"])

        if pro_mode == "Upload Omnivox screenshot (OCR)":
            file = st.file_uploader("Upload screenshot", type=["png", "jpg", "jpeg"])
            if file is not None:
                # here you'd call your existing /mnt/data/ocr_utils.py logic
                st.write("📄 (placeholder) Run OCR here and parse courses → then feed into calculator.")
        else:
            csv_file = st.file_uploader("Upload CSV with columns: course_name,mark,group_avg,group_sd,credits", type=["csv"])
            if csv_file is not None:
                df = pd.read_csv(csv_file)
                if all(col in df.columns for col in ["course_name", "mark", "group_avg", "group_sd", "credits"]):
                    df["rscore"] = df.apply(
                        lambda row: compute_rscore(
                            row["mark"],
                            row["group_avg"],
                            row["group_sd"],
                        ),
                        axis=1,
                    )
                    overall = compute_overall_rscore(df)
                    st.success(f"Your weighted R-score (approx): **{overall}**")
                    st.dataframe(df)
                else:
                    st.error("CSV missing required columns.")
