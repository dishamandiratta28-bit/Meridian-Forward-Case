import pandas as pd
import streamlit as st
from calc import BUDGET, MAX_VENDORS, run

st.set_page_config(
    page_title="Meridian Forward | Workforce Planning",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.6rem; padding-bottom: 2.2rem; max-width: 1400px;}
      .eyebrow {text-transform:uppercase; letter-spacing:.12em; font-size:.76rem; font-weight:700; opacity:.7;}
      .hero {padding:1.25rem 1.4rem; border:1px solid rgba(128,128,128,.28); border-radius:16px;
             background:linear-gradient(115deg, rgba(16,185,129,.12), rgba(59,130,246,.06)); margin:.5rem 0 1.1rem 0;}
      .hero h2 {margin:.3rem 0 .45rem 0; font-size:1.7rem;}
      .hero p {margin:0; font-size:1.03rem;}
      .note {font-size:.88rem; opacity:.78;}
      div[data-testid="stMetric"] {border:1px solid rgba(128,128,128,.23); border-radius:13px; padding:12px 14px;}
      div[data-testid="stMetricLabel"] p {font-size:.86rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="eyebrow">Session 5 · Four-week pilot package · Q5.01</div>', unsafe_allow_html=True)
st.title("Meridian Forward | Workforce Planning")
st.caption("A decision tool for one pilot package — not the full 8,400-person workforce or all 600 positions.")

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">The central insight</div>
      <h2>Unblock the work before adding more people.</h2>
      <p>The case is not only about headcount. It combines skill shortages, time pressure, access constraints and decision authority. Test bounded delegation, count customer-data preparation once, and protect internal legacy knowledge.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_problem, tab_calc, tab_log = st.tabs(["01 · Problem & recommendation", "02 · Pilot calculator", "03 · Comparison & revision log"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Case framing
# ─────────────────────────────────────────────────────────────────────────────
with tab_problem:
    st.subheader("One composite problem")
    left, right = st.columns([1.2, 0.8], gap="large")
    with left:
        st.markdown("### Four shortages hiding behind one hiring number")
        dimensions = [
            ("Skill", "The work needs specific specialist capabilities."),
            ("Time", "A four-week delivery window is shorter than the hiring lead time."),
            ("Access", "Teams cannot always get the information or support they need in time."),
            ("Authority", "Important approvals remain with decision-makers elsewhere."),
        ]
        for label, desc in dimensions:
            st.markdown(f"**{label}**  \n{desc}")
        st.markdown("### Evidence trail from the case")
        st.markdown(
            "- **Main evidence:** P023–P029 and P050–P052  \n"
            "- **Supporting evidence:** P008–P014 and P042–P044  \n"
            "- **Concrete example:** a Friday release waited on three approvals (P012)."
        )
    with right:
        st.markdown("### Recommended pilot response")
        st.markdown(
            "1. **Count customer-data preparation once** with one agreed output and a named receiving owner.\n"
            "2. **Use bounded delegation** for routine decisions, with clear limits and a response clock.\n"
            "3. **Add targeted vendor support** for data preparation and QA.\n"
            "4. **Keep legacy expertise internal** and move the 64-hour teaching gap past the pilot window only with service-owner agreement.\n"
            "5. **Revisit hiring after the pilot** using the measured results."
        )
        st.info("Power form: the case describes an as-is Type A arrangement for reserved decisions and proposes a Type D arrangement for this pilot only (Mintzberg, 1980, Fig. 2).")

    st.divider()
    st.subheader("Default recommendation at a glance")
    default = pd.DataFrame(run(workflow=2, include_duplicate=False, buy_legacy=False))
    gap = int(default["Gap"].sum())
    cost = int(default["Cost"].sum())
    workers = int(default["Workers"].sum())
    unfilled = int(default["Unfilled"].sum())
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Remaining specialist gap", f"{gap:,} h")
    k2.metric("Targeted vendor workers", f"{workers}")
    k3.metric("Proposed vendor cost", f"₹{cost:,}")
    k4.metric("Budget remaining", f"₹{BUDGET - cost:,}")
    st.warning(f"The remaining {unfilled} hours are in legacy expertise. The model leaves this work unfilled within the four-week window; move the teaching blocks only after the service owner agrees.")
    st.caption("P-number references are paragraphs in the original case. Q5-numbered values are teaching inputs used for this calculation, not claims about the full workforce.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Interactive calculator
# ─────────────────────────────────────────────────────────────────────────────
with tab_calc:
    st.subheader("Test the pilot assumptions")
    st.write("Change the workflow, duplicate-data decision or legacy fallback. The role-level results and budget check update automatically.")

    select_col, options_col = st.columns([1, 1], gap="large")
    with select_col:
        wf = st.radio(
            "Workflow arrangement · Q5.05",
            [1, 2],
            index=1,
            format_func=lambda v: "1 · Retained approvals" if v == 1 else "2 · Bounded delegation",
            help="Bounded delegation reduces the coordination allowance in the teaching model. The reduction depends on agreement and use in practice.",
        )
    with options_col:
        dup = st.radio(
            "Customer-data preparation · Q5.04 / P024",
            [False, True],
            index=0,
            format_func=lambda v: "Counted once · one owner" if not v else "Included twice · baseline case",
            help="Select whether the duplicate 60-pack preparation is counted a second time in pilot demand.",
        )
        legacy = st.checkbox("Buy one legacy-expert vendor worker as a fallback", value=False,
                             help="This is a scenario choice, not the default recommendation. It adds a vendor worker and the associated cost.")

    rows = run(workflow=wf, include_duplicate=dup, buy_legacy=legacy)
    df = pd.DataFrame(rows)
    demand = int(df["Demand"].sum())
    assigned = int(df["Assigned"].sum())
    gap = int(df["Gap"].sum())
    workers = int(df["Workers"].sum())
    cost = int(df["Cost"].sum())
    unfilled = int(df["Unfilled"].sum())
    budget_left = BUDGET - cost

    st.markdown("#### Scenario results")
    metrics = st.columns(5)
    metrics[0].metric("Pilot demand", f"{demand:,} h")
    metrics[1].metric("Internal hours assigned", f"{assigned:,} h")
    metrics[2].metric("Specialist gap before vendors", f"{gap:,} h")
    metrics[3].metric("Vendor workers", f"{workers}", f"Limit: {MAX_VENDORS}")
    metrics[4].metric("Vendor cost", f"₹{cost:,}", f"₹{budget_left:,} {'left' if budget_left >= 0 else 'over'}")

    if cost > BUDGET:
        st.error(f"Over the ₹{BUDGET:,} vendor budget by ₹{cost - BUDGET:,}.")
    elif workers > MAX_VENDORS:
        st.error(f"Over the {MAX_VENDORS}-worker limit.")
    else:
        st.success("This scenario is within both the vendor budget and worker limit.")

    if unfilled > 0:
        st.warning(f"Unfilled gap: {unfilled:,} h. In the recommended default scenario, this is the legacy-expertise gap. Sequence the teaching blocks beyond the pilot only if the service owner agrees.")
    elif legacy:
        st.info("The legacy-expert vendor option covers the modelled legacy gap, but it should remain a fallback because this work depends on internal knowledge.")

    display = df.rename(columns={
        "Role": "Role / skill", "Demand": "Pilot demand (h)", "Usable": "Usable internal supply (h)",
        "Assigned": "Internal assigned (h)", "Gap": "Gap before vendors (h)", "Positions": "Whole role positions",
        "Pool": "Pool people", "Workers": "Vendor workers", "Cost": "Vendor cost (₹)", "Unfilled": "Unfilled after vendors (h)",
    })
    st.dataframe(display, hide_index=True, use_container_width=True, column_config={
        "Vendor cost (₹)": st.column_config.NumberColumn(format="₹%d"),
        "Pilot demand (h)": st.column_config.NumberColumn(format="%d"),
        "Usable internal supply (h)": st.column_config.NumberColumn(format="%d"),
        "Internal assigned (h)": st.column_config.NumberColumn(format="%d"),
        "Gap before vendors (h)": st.column_config.NumberColumn(format="%d"),
        "Unfilled after vendors (h)": st.column_config.NumberColumn(format="%d"),
    })

    st.markdown("#### What the selected scenario means")
    if wf == 2 and not dup and not legacy:
        st.markdown("**Recommended case:** bounded delegation + count duplicate preparation once + one vendor each for data preparation and QA. Vendor cost is ₹2,16,000. The 64-hour legacy gap remains outside the pilot window, subject to service-owner agreement.")
    elif wf == 1 or dup:
        st.markdown("This setting retains more coordination work and/or counts the duplicate data-preparation task. Compare its gap and cost with the recommended case before selecting it.")
    else:
        st.markdown("This setting adds a legacy vendor as a fallback. Compare the extra cost against the benefit, and consider the risk of transferring internal knowledge to an external worker.")

    st.caption("Model assumptions: role-specific skills; no overtime; no attrition (Q5.02). New hires add 0 hours during this four-week pilot because the teaching input uses an eight-week lead time (Q5.07). Coordination reductions are conditional (Q5.05).")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Comparison and editable revision log
# ─────────────────────────────────────────────────────────────────────────────
with tab_log:
    st.subheader("Compare the workflow choices")
    st.write("This table buys vendors for all modelled gaps, including legacy expertise, to make the scenario costs comparable. It is a comparison view—not the recommended staffing plan.")
    comparison = []
    for workflow in (1, 2):
        for duplicate in (True, False):
            result = pd.DataFrame(run(workflow, duplicate, True))
            total_cost = int(result["Cost"].sum())
            comparison.append({
                "Workflow": "Retained approvals" if workflow == 1 else "Bounded delegation",
                "Duplicate data prep": "Included twice" if duplicate else "Counted once",
                "Gap before vendors (h)": int(result["Gap"].sum()),
                "Vendor workers": int(result["Workers"].sum()),
                "Vendor cost (₹)": total_cost,
                "Budget status": "Within budget" if total_cost <= BUDGET else "Over budget",
            })
    comp_df = pd.DataFrame(comparison)
    st.dataframe(comp_df, hide_index=True, use_container_width=True, column_config={
        "Vendor cost (₹)": st.column_config.NumberColumn(format="₹%d"),
    })

    st.markdown("#### Revision log")
    st.write("Add what changed after feedback so your team can show how the recommendation developed.")
    if "revision_entries" not in st.session_state:
        st.session_state.revision_entries = []
    with st.form("revision_form", clear_on_submit=True):
        rev_date = st.date_input("Date")
        rev_change = st.text_input("What changed?", placeholder="e.g., clarified the legacy-expertise fallback")
        rev_reason = st.text_input("Why did it change?", placeholder="e.g., feedback or a case assumption")
        submitted = st.form_submit_button("Add revision")
        if submitted:
            if rev_change.strip() and rev_reason.strip():
                st.session_state.revision_entries.append({"Date": str(rev_date), "Change": rev_change.strip(), "Reason / evidence": rev_reason.strip()})
                st.success("Revision added to this session.")
            else:
                st.error("Please fill in both the change and the reason.")

    if st.session_state.revision_entries:
        log_df = pd.DataFrame(st.session_state.revision_entries)
        st.dataframe(log_df, hide_index=True, use_container_width=True)
        st.download_button("Download revision log (CSV)", data=log_df.to_csv(index=False).encode("utf-8"), file_name="meridian_forward_revision_log.csv", mime="text/csv")
    else:
        st.info("No revisions added yet. Entries are held in the current app session; download the CSV if you need to keep a copy.")

    st.markdown("#### Decision to carry into the presentation")
    st.success("Bounded delegation + customer-data preparation counted once + one vendor each for data preparation and QA = ₹2,16,000. Sequence the 64-hour legacy teaching gap beyond the four-week window only with service-owner agreement.")

st.divider()
st.caption("Source discipline: P-number references identify paragraphs in the original case. Q5.02–Q5.08 are labelled teaching inputs for the calculation. Results apply to this four-week pilot package only.")
