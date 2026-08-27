import streamlit as st
import datetime

# -----------------------------------------------------------------------------------------
# DATE CALCULATION ENGINE
# -----------------------------------------------------------------------------------------
def get_federal_holidays(year):
    """
    Returns a dictionary of federal holidays for the given year.
    Keys are datetime.date objects, values are holiday names.
    Both actual and observed holidays are included per 5 U.S.C. Sec. 6103(a).
    """
    holidays = {}
    
    # New Year's Day
    holidays[datetime.date(year, 1, 1)] = "New Year's Day"
    
    # MLK Jr. Day - 3rd Monday in Jan
    d = datetime.date(year, 1, 1)
    while d.weekday() != 0:
        d += datetime.timedelta(days=1)
    mlk = d + datetime.timedelta(weeks=2)
    holidays[mlk] = "Martin Luther King Jr. Day"
    
    # Presidents' Day - 3rd Monday in Feb
    d = datetime.date(year, 2, 1)
    while d.weekday() != 0:
        d += datetime.timedelta(days=1)
    pres = d + datetime.timedelta(weeks=2)
    holidays[pres] = "Washington's Birthday"
    
    # Memorial Day - Last Monday in May
    d = datetime.date(year, 5, 31)
    while d.weekday() != 0:
        d -= datetime.timedelta(days=1)
    holidays[d] = "Memorial Day"
    
    # Juneteenth
    holidays[datetime.date(year, 6, 19)] = "Juneteenth"
    
    # Independence Day
    holidays[datetime.date(year, 7, 4)] = "Independence Day"
    
    # Labor Day - 1st Monday in Sep
    d = datetime.date(year, 9, 1)
    while d.weekday() != 0:
        d += datetime.timedelta(days=1)
    holidays[d] = "Labor Day"
    
    # Columbus Day - 2nd Monday in Oct
    d = datetime.date(year, 10, 1)
    while d.weekday() != 0:
        d += datetime.timedelta(days=1)
    col = d + datetime.timedelta(weeks=1)
    holidays[col] = "Columbus Day"
    
    # Veterans Day
    holidays[datetime.date(year, 11, 11)] = "Veterans Day"
    
    # Thanksgiving Day - 4th Thursday in Nov
    d = datetime.date(year, 11, 1)
    while d.weekday() != 3:
        d += datetime.timedelta(days=1)
    thanks = d + datetime.timedelta(weeks=3)
    holidays[thanks] = "Thanksgiving Day"
    
    # Christmas Day
    holidays[datetime.date(year, 12, 25)] = "Christmas Day"
    
    # Holiday Observation Rules:
    observed_holidays = {}
    for h_date, h_name in holidays.items():
        observed_holidays[h_date] = h_name
        if h_date.weekday() == 5: # Saturday
            obs_date = h_date - datetime.timedelta(days=1)
            observed_holidays[obs_date] = f"{h_name} (Observed)"
        elif h_date.weekday() == 6: # Sunday
            obs_date = h_date + datetime.timedelta(days=1)
            observed_holidays[obs_date] = f"{h_name} (Observed)"
            
    return observed_holidays

def is_business_day(date, holidays_dict):
    if date.weekday() in [5, 6]:
        return False
    if date in holidays_dict:
        return False
    return True

def calculate_deadline(base_date, days, direction="forward", holidays_cache=None):
    if base_date is None or days is None:
        return None, ""
        
    if isinstance(base_date, str):
        base_date = datetime.datetime.strptime(base_date, "%Y-%m-%d").date()
        
    if direction == "forward":
        target_date = base_date + datetime.timedelta(days=days)
    else:
        target_date = base_date - datetime.timedelta(days=days)
        
    year = target_date.year
    if holidays_cache is None or year not in holidays_cache:
        if holidays_cache is None:
            holidays_cache = {}
        holidays_cache[year] = get_federal_holidays(year)
        holidays_cache[year - 1] = get_federal_holidays(year - 1)
        holidays_cache[year + 1] = get_federal_holidays(year + 1)
        
    all_holidays = {}
    for y in holidays_cache:
        all_holidays.update(holidays_cache[y])
        
    rolled = False
    original_date = target_date
    if not is_business_day(target_date, all_holidays):
        rolled = True
        if direction == "forward":
            while not is_business_day(target_date, all_holidays):
                target_date += datetime.timedelta(days=1)
        else:
            while not is_business_day(target_date, all_holidays):
                target_date -= datetime.timedelta(days=1)
                
    holiday_name = all_holidays.get(target_date, None)
    
    note = ""
    if rolled:
        note = f"Rolled from {original_date.strftime('%A, %b %d')}"
        if holiday_name:
            note += f" due to {holiday_name}"
        else:
            note += " because of the weekend"
            
    return target_date, note

def calculate_business_days_deadline(base_date, days, holidays_cache=None):
    if base_date is None or days is None:
        return None, ""
        
    if isinstance(base_date, str):
        base_date = datetime.datetime.strptime(base_date, "%Y-%m-%d").date()
        
    curr = base_date
    year = curr.year
    if holidays_cache is None or year not in holidays_cache:
        if holidays_cache is None:
            holidays_cache = {}
        holidays_cache[year] = get_federal_holidays(year)
        holidays_cache[year - 1] = get_federal_holidays(year - 1)
        holidays_cache[year + 1] = get_federal_holidays(year + 1)
        
    all_holidays = {}
    for y in holidays_cache:
        all_holidays.update(holidays_cache[y])
        
    count = 0
    while count < days:
        curr += datetime.timedelta(days=1)
        if is_business_day(curr, all_holidays):
            count += 1
            
    return curr, f"Calculated as {days} business days after receipt (skips weekends/holidays)"

# -----------------------------------------------------------------------------------------
# STREAMLIT UI LAYOUT
# -----------------------------------------------------------------------------------------
st.set_page_config(page_title="Florida Real Estate Deadline Calculator v5", layout="wide")

st.title("🌴 Florida Real Estate Contract Deadline Calculator v5.0")
st.markdown("""
An advanced comparative deadline calculator featuring all core milestones, **Buyer's Additional Deposit**, **condo resale rescission periods**, and **dispute-specific inspection timelines** under **NABOR** and **FAR/BAR** rules. This dashboard is perfectly synchronized with the Excel v4.0 Tracker.
""")

# Setup Sidebar Sections
st.sidebar.header("📅 Section 1: Key Base Dates")
eff_date = st.sidebar.date_input("Effective Date (Day 0)", datetime.date(2026, 9, 1))
closing_date = st.sidebar.date_input("Scheduled Closing Date", datetime.date(2026, 10, 15))

# Optional inputs (with toggles)
enable_condo = st.sidebar.checkbox("Include Condo Documents Timelines", value=True)
condo_date = None
if enable_condo:
    condo_date = st.sidebar.date_input("Condo Docs Delivery Date", datetime.date(2026, 9, 5))

enable_assoc = st.sidebar.checkbox("Include HOA/Association Timeline", value=True)
assoc_date = None
if enable_assoc:
    assoc_date = st.sidebar.date_input("Association App Receipt Date", datetime.date(2026, 9, 4))

enable_dispute = st.sidebar.checkbox("Include Inspection Election Dispute Timeline", value=True)
election_date = None
seller_resp_date = None
if enable_dispute:
    election_date = st.sidebar.date_input("Inspection Election Delivery Date", datetime.date(2026, 9, 16))
    seller_resp_date = st.sidebar.date_input("Seller Response to Election Date", datetime.date(2026, 9, 20))

# Custom Offsets
st.sidebar.markdown("---")
st.sidebar.header("⏱️ Section 2: Custom Milestone Offsets")

with st.sidebar.expander("💼 Escrow & Financing Offsets"):
    dep_offset = st.number_input("Initial Deposit (Days after)", value=3, min_value=0)
    add_dep_offset = st.number_input("Additional Deposit (Days after)", value=10, min_value=0)
    loan_app_offset = st.number_input("Loan Application (Days after)", value=5, min_value=0)
    nab_fin_offset = st.number_input("NABOR Financing (Days after)", value=45, min_value=0)
    fb_fin_offset = st.number_input("FAR/BAR Financing (Days after)", value=30, min_value=0)

with st.sidebar.expander("🔍 Inspection & Dispute Offsets"):
    insp_offset = st.number_input("Inspection Period (Days after)", value=15, min_value=0)
    election_offset = st.number_input("Buyer Election (Days after Inspection end)", value=5, min_value=0)
    seller_offset = st.number_input("Seller Response (Days after Buyer Election)", value=10, min_value=0)
    terminate_offset = st.number_input("Buyer Terminate Right (Days after Seller Response)", value=5, min_value=0)

with st.sidebar.expander("🏢 Association & Condo Offsets"):
    assoc_app_offset = st.number_input("Association Filing (Days after receipt)", value=10, min_value=0)
    condo_resciss_offset = st.number_input("Condo Rescission Period (Business Days)", value=7, min_value=0)

with st.sidebar.expander("📋 Title & Survey Offsets (Backward-looking)"):
    title_offset = st.number_input("Title Evidence (Days prior to Closing)", value=15, min_value=0)
    survey_offset = st.number_input("Survey Deadline (Days prior to Closing)", value=15, min_value=0)

# -----------------------------------------------------------------------------------------
# CALCULATIONS
# -----------------------------------------------------------------------------------------
holidays_cache = {}

# Actual Rolled Closing Date
rolled_closing_nab, closing_nab_note = calculate_deadline(closing_date, 0, "forward", holidays_cache)
rolled_closing_fb, closing_fb_note = calculate_deadline(closing_date, 0, "forward", holidays_cache)

# Forward Milestones
nab_dep_date, nab_dep_note = calculate_deadline(eff_date, dep_offset, "forward", holidays_cache)
fb_dep_date, fb_dep_note = calculate_deadline(eff_date, dep_offset, "forward", holidays_cache)

nab_add_dep_date, nab_add_dep_note = calculate_deadline(eff_date, add_dep_offset, "forward", holidays_cache)
fb_add_dep_date, fb_add_dep_note = calculate_deadline(eff_date, add_dep_offset, "forward", holidays_cache)

nab_loan_app, nab_loan_note = calculate_deadline(eff_date, loan_app_offset, "forward", holidays_cache)
fb_loan_app, fb_loan_note = calculate_deadline(eff_date, loan_app_offset, "forward", holidays_cache)

nab_insp_date, nab_insp_note = calculate_deadline(eff_date, insp_offset, "forward", holidays_cache)
fb_insp_date, fb_insp_note = calculate_deadline(eff_date, insp_offset, "forward", holidays_cache)

# Inspection dispute steps
nab_election, nab_election_note = calculate_deadline(nab_insp_date, election_offset, "forward", holidays_cache)
fb_election, fb_election_note = calculate_deadline(fb_insp_date, election_offset, "forward", holidays_cache)

nab_seller_resp, nab_seller_note = calculate_deadline(election_date, seller_offset, "forward", holidays_cache) if enable_dispute else (None, "")
fb_seller_resp, fb_seller_note = calculate_deadline(election_date, seller_offset, "forward", holidays_cache) if enable_dispute else (None, "")

nab_terminate, nab_terminate_note = calculate_deadline(seller_resp_date, terminate_offset, "forward", holidays_cache) if enable_dispute else (None, "")
fb_terminate, fb_terminate_note = calculate_deadline(seller_resp_date, terminate_offset, "forward", holidays_cache) if enable_dispute else (None, "")

# Condo Rescission (Business Days)
nab_condo, nab_condo_note = calculate_business_days_deadline(condo_date, condo_resciss_offset, holidays_cache) if enable_condo else (None, "")
fb_condo, fb_condo_note = calculate_business_days_deadline(condo_date, condo_resciss_offset, holidays_cache) if enable_condo else (None, "")

# Association Application Filing
nab_assoc, nab_assoc_note = calculate_deadline(assoc_date, assoc_app_offset, "forward", holidays_cache) if enable_assoc else (None, "")
fb_assoc, fb_assoc_note = calculate_deadline(assoc_date, assoc_app_offset, "forward", holidays_cache) if enable_assoc else (None, "")

# Financing
nab_fin, nab_fin_note = calculate_deadline(eff_date, nab_fin_offset, "forward", holidays_cache)
fb_fin, fb_fin_note = calculate_deadline(eff_date, fb_fin_offset, "forward", holidays_cache)

# Title & Survey (Backward-looking relative to actual Closing)
nab_title, nab_title_note = calculate_deadline(rolled_closing_nab, title_offset, "backward", holidays_cache)
fb_title, fb_title_note = calculate_deadline(rolled_closing_fb, title_offset, "backward", holidays_cache)

nab_survey, nab_survey_note = calculate_deadline(rolled_closing_nab, survey_offset, "backward", holidays_cache)
fb_survey, fb_survey_note = calculate_deadline(rolled_closing_fb, survey_offset, "backward", holidays_cache)

# -----------------------------------------------------------------------------------------
# DEFINE TABS FOR DETAILED VS CLIENT VIEW
# -----------------------------------------------------------------------------------------
tab1, tab2 = st.tabs(["🎛️ Detailed Comparative Calculator", "📋 Simplified Client Summaries"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.header("🏢 NABOR Contract Milestones")
        st.markdown("**Naples Area Board of Realtors Rules**")
        st.metric("Effective Date (Day 0)", eff_date.strftime("%A, %B %d, %Y"))
        
        st.subheader("🗓️ Calendar Milestones")
        
        st.write(f"🟢 **Initial Escrow Deposit**: {nab_dep_date.strftime('%A, %b %d, %Y')} *({dep_offset} days after)*")
        if nab_dep_note: st.caption(f"ℹ️ {nab_dep_note}")
        
        st.write(f"🔵 **Buyer's Additional Deposit**: {nab_add_dep_date.strftime('%A, %b %d, %Y')} *({add_dep_offset} days after)*")
        if nab_add_dep_note: st.caption(f"ℹ️ {nab_add_dep_note}")
        
        st.write(f"📝 **Buyer's Loan Application**: {nab_loan_app.strftime('%A, %b %d, %Y')} *({loan_app_offset} days after)*")
        if nab_loan_note: st.caption(f"ℹ️ {nab_loan_note}")
        
        st.write(f"🔍 **Inspection / Due Diligence Period**: {nab_insp_date.strftime('%A, %b %d, %Y')} *({insp_offset} days after)*")
        if nab_insp_note: st.caption(f"ℹ️ {nab_insp_note}")
        
        st.write(f"✏️ **Buyer Election of Defective Items**: {nab_election.strftime('%A, %b %d, %Y')} *({election_offset} days after inspection expiration)*")
        if nab_election_note: st.caption(f"ℹ️ {nab_election_note}")
        
        if enable_dispute and nab_seller_resp:
            st.write(f"🤝 **Seller's Response to Election**: {nab_seller_resp.strftime('%A, %b %d, %Y')} *({seller_offset} days after buyer election)*")
            if nab_seller_note: st.caption(f"ℹ️ {nab_seller_note}")
            
            st.write(f"❌ **Buyer's Right to Terminate**: {nab_terminate.strftime('%A, %b %d, %Y')} *({terminate_offset} days after seller response)*")
            if nab_terminate_note: st.caption(f"ℹ️ {nab_terminate_note}")
            
        if enable_assoc and nab_assoc:
            st.write(f"📄 **Buyer Application for Association Approval**: {nab_assoc.strftime('%A, %b %d, %Y')} *({assoc_app_offset} days after receipt)*")
            if nab_assoc_note: st.caption(f"ℹ️ {nab_assoc_note}")
            
        if enable_condo and nab_condo:
            st.write(f"🏢 **Condominium Rescission Period**: {nab_condo.strftime('%A, %b %d, %Y')} *({condo_resciss_offset} Business Days after receipt)*")
            if nab_condo_note: st.caption(f"ℹ️ {nab_condo_note}")
            
        st.write(f"💰 **Financing Contingency**: {nab_fin.strftime('%A, %b %d, %Y')} *({nab_fin_offset} days after)*")
        if nab_fin_note: st.caption(f"ℹ️ {nab_fin_note}")
        
        st.write(f"📋 **Title Evidence**: {nab_title.strftime('%A, %b %d, %Y')} *({title_offset} days prior)*")
        if nab_title_note: st.caption(f"ℹ️ {nab_title_note}")
        
        st.write(f"📐 **Survey Deadline**: {nab_survey.strftime('%A, %b %d, %Y')} *({survey_offset} days prior)*")
        if nab_survey_note: st.caption(f"ℹ️ {nab_survey_note}")
        
        st.write(f"🚶 **Buyer Walk-through Inspection**: Prior to Closing Date / {rolled_closing_nab.strftime('%A, %b %d, %Y')} *(or possession if earlier)*")
        
        st.metric("🔒 Rolled Closing Date", rolled_closing_nab.strftime("%A, %B %d, %Y"))
        if closing_nab_note: st.caption(f"ℹ️ {closing_nab_note}")

    with col2:
        st.header("⚖️ FAR/BAR Contract Milestones")
        st.markdown("**Florida Realtors/Florida Bar Rules**")
        st.metric("Effective Date (Day 0)", eff_date.strftime("%A, %B %d, %Y"))
        
        st.subheader("🗓️ Calendar Milestones")
        
        st.write(f"🟢 **Initial Escrow Deposit**: {fb_dep_date.strftime('%A, %b %d, %Y')} *({dep_offset} days after)*")
        if fb_dep_note: st.caption(f"ℹ️ {fb_dep_note}")
        
        st.write(f"🔵 **Buyer's Additional Deposit**: {fb_add_dep_date.strftime('%A, %b %d, %Y')} *({add_dep_offset} days after)*")
        if fb_add_dep_note: st.caption(f"ℹ️ {fb_add_dep_note}")
        
        st.write(f"📝 **Buyer's Loan Application**: {fb_loan_app.strftime('%A, %b %d, %Y')} *({loan_app_offset} days after)*")
        if fb_loan_note: st.caption(f"ℹ️ {fb_loan_note}")
        
        st.write(f"🔍 **Inspection / Due Diligence Period**: {fb_insp_date.strftime('%A, %b %d, %Y')} *({insp_offset} days after)*")
        if fb_insp_note: st.caption(f"ℹ️ {fb_insp_note}")
        
        st.write(f"✏️ **Buyer Election of Defective Items**: {fb_election.strftime('%A, %b %d, %Y')} *({election_offset} days after inspection expiration)*")
        if fb_election_note: st.caption(f"ℹ️ {fb_election_note}")
        
        if enable_dispute and fb_seller_resp:
            st.write(f"🤝 **Seller's Response to Election**: {fb_seller_resp.strftime('%A, %b %d, %Y')} *({seller_offset} days after buyer election)*")
            if fb_seller_note: st.caption(f"ℹ️ {fb_seller_note}")
            
            st.write(f"❌ **Buyer's Right to Terminate**: {fb_terminate.strftime('%A, %b %d, %Y')} *({terminate_offset} days after seller response)*")
            if fb_terminate_note: st.caption(f"ℹ️ {fb_terminate_note}")
            
        if enable_assoc and fb_assoc:
            st.write(f"📄 **Buyer Application for Association Approval**: {fb_assoc.strftime('%A, %b %d, %Y')} *({assoc_app_offset} days after receipt)*")
            if fb_assoc_note: st.caption(f"ℹ️ {fb_assoc_note}")
            
        if enable_condo and fb_condo:
            st.write(f"🏢 **Condominium Rescission Period**: {fb_condo.strftime('%A, %b %d, %Y')} *({condo_resciss_offset} Business Days after receipt)*")
            if fb_condo_note: st.caption(f"ℹ️ {fb_condo_note}")
            
        st.write(f"💰 **Financing Contingency**: {fb_fin.strftime('%A, %b %d, %Y')} *({fb_fin_offset} days after)*")
        if fb_fin_note: st.caption(f"ℹ️ {fb_fin_note}")
        
        st.write(f"📋 **Title Evidence**: {fb_title.strftime('%A, %b %d, %Y')} *({title_offset} days prior)*")
        if fb_title_note: st.caption(f"ℹ️ {fb_title_note}")
        
        st.write(f"📐 **Survey Deadline**: {fb_survey.strftime('%A, %b %d, %Y')} *({survey_offset} days prior)*")
        if fb_survey_note: st.caption(f"ℹ️ {fb_survey_note}")
        
        st.write(f"🚶 **Buyer Walk-through Inspection**: Prior to Closing Date / {rolled_closing_fb.strftime('%A, %b %d, %Y')} *(or possession if earlier)*")
        
        st.metric("🔒 Rolled Closing Date", rolled_closing_fb.strftime("%A, %B %d, %Y"))
        if closing_fb_note: st.caption(f"ℹ️ {closing_fb_note}")

    st.markdown("---")
    st.subheader("⚖️ Advanced Real Estate Rule Summary")
    st.markdown("""
    - **Day Zero Rule**: Both contracts agree that counting starts the day *after* the contract's Effective Date (meaning Day 1 is the day after).
    - **Condo Rescission**: Under Florida Statute § 718.503, the **7-day resale cancel period** counts strictly in **Business Days** (excluding weekends and federal holidays).
    - **Inspection Disputes (NABOR)**: After the initial Inspection Period, the buyer has **5 calendar days** to deliver notice of Defective Inspection Items. The seller has **10 calendar days** to respond, and the buyer has **5 calendar days** from said response to terminate the contract if repair items are rejected or countered.
    - **Walk-through**: Under both NABOR and FAR/BAR contracts, the buyer walk-through must occur **prior to the Closing Date** (or possession if earlier).
    """)

# -----------------------------------------------------------------------------------------
# TAB 2: SIMPLIFIED CHRONOLOGICAL CLIENT SUMMARIES
# -----------------------------------------------------------------------------------------
with tab2:
    st.header("📋 Client Transaction Milestones Roadmap (Chronological)")
    st.markdown("""
    Here are simplified chronological summaries of key transaction dates, designed to be easily shared with your buyers or sellers. 
    All deadlines are sorted chronologically in **ascending order** so you can track each requirement down the calendar list.
    """)
    
    # 1. Compile and Sort NABOR
    nab_milestones = []
    if nab_dep_date:
        nab_milestones.append(("Escrow: Initial Escrow Deposit", nab_dep_date))
    if nab_add_dep_date:
        nab_milestones.append(("Escrow: Buyer's Additional Deposit", nab_add_dep_date))
    if nab_loan_app:
        nab_milestones.append(("Financing: Buyer's Loan Application Deadline", nab_loan_app))
    if nab_insp_date:
        nab_milestones.append(("Inspections: Inspection Period Expiration", nab_insp_date))
    if nab_election:
        nab_milestones.append(("Inspections: Buyer Defective Items Notice Election", nab_election))
    if enable_dispute and nab_seller_resp:
        nab_milestones.append(("Inspections: Seller Response to Defective Items", nab_seller_resp))
    if enable_dispute and nab_terminate:
        nab_milestones.append(("Inspections: Buyer Right to Terminate Expiration", nab_terminate))
    if enable_assoc and nab_assoc:
        nab_milestones.append(("Association: Buyer Membership Filing Deadline", nab_assoc))
    if enable_condo and nab_condo:
        nab_milestones.append(("Condominium: 7-Business-Day Rescission Expiration", nab_condo))
    if nab_fin:
        nab_milestones.append(("Financing: Financing Contingency Expiration", nab_fin))
    if nab_title:
        nab_milestones.append(("Title: Title Evidence Due Date", nab_title))
    if nab_survey:
        nab_milestones.append(("Survey: Boundary Survey Due Date", nab_survey))
    nab_milestones.append(("Walk-through: Pre-Closing Final Walk-through Inspection (Prior to)", rolled_closing_nab))
    nab_milestones.append(("Closing: Actual Closing & Ownership Transfer", rolled_closing_nab))

    sorted_nab = sorted([m for m in nab_milestones if m[1] is not None], key=lambda x: x[1])

    # 2. Compile and Sort FAR/BAR
    fb_milestones = []
    if fb_dep_date:
        fb_milestones.append(("Escrow: Initial Escrow Deposit", fb_dep_date))
    if fb_add_dep_date:
        fb_milestones.append(("Escrow: Buyer's Additional Deposit", fb_add_dep_date))
    if fb_loan_app:
        fb_milestones.append(("Financing: Buyer's Loan Application Deadline", fb_loan_app))
    if fb_insp_date:
        fb_milestones.append(("Inspections: Inspection / Due Diligence Expiration", fb_insp_date))
    if fb_election:
        fb_milestones.append(("Inspections: Buyer Defective Items Notice Election", fb_election))
    if enable_dispute and fb_seller_resp:
        fb_milestones.append(("Inspections: Seller Response to Defective Items", fb_seller_resp))
    if enable_dispute and fb_terminate:
        fb_milestones.append(("Inspections: Buyer Right to Terminate Expiration", fb_terminate))
    if enable_assoc and fb_assoc:
        fb_milestones.append(("Association: Buyer Membership Filing Deadline", fb_assoc))
    if enable_condo and fb_condo:
        fb_milestones.append(("Condominium: 7-Business-Day Rescission Expiration", fb_condo))
    if fb_fin:
        fb_milestones.append(("Financing: Financing Contingency Expiration", fb_fin))
    if fb_title:
        fb_milestones.append(("Title: Title Evidence Due Date", fb_title))
    if fb_survey:
        fb_milestones.append(("Survey: Boundary Survey Due Date", fb_survey))
    fb_milestones.append(("Walk-through: Pre-Closing Final Walk-through Inspection (Prior to)", rolled_closing_fb))
    fb_milestones.append(("Closing: Actual Closing & Ownership Transfer", rolled_closing_fb))

    sorted_fb = sorted([m for m in fb_milestones if m[1] is not None], key=lambda x: x[1])

    # Display Side-by-Side summaries
    sum_col1, sum_col2 = st.columns(2)
    
    with sum_col1:
        st.subheader("🏢 NABOR Milestones Schedule")
        st.markdown("**Ordered Chronologically**")
        
        # Build Markdown Table for NABOR
        nab_table_md = "| Deadline Description | Milestone Date |\n| :--- | :--- |\n"
        for desc, dt in sorted_nab:
            # Format nicely
            dt_str = dt.strftime("%A, %b %d, %Y")
            if "Closing" in desc:
                nab_table_md += f"| 🔒 **{desc}** | **{dt_str}** |\n"
            elif "Walk-through" in desc:
                nab_table_md += f"| 🚶 **{desc}** | *Prior to Closing on {dt.strftime('%b %d, %Y')}* |\n"
            elif "Deposit" in desc:
                nab_table_md += f"| 🟢 **{desc}** | **{dt_str}** |\n"
            elif "Rescission" in desc:
                nab_table_md += f"| 🏢 **{desc}** | **{dt_str}** |\n"
            elif "Expiration" in desc:
                nab_table_md += f"| 🛑 **{desc}** | **{dt_str}** |\n"
            else:
                nab_table_md += f"| {desc} | {dt_str} |\n"
                
        st.markdown(nab_table_md)
        
    with sum_col2:
        st.subheader("⚖️ FAR/BAR Milestones Schedule")
        st.markdown("**Ordered Chronologically**")
        
        # Build Markdown Table for FAR/BAR
        fb_table_md = "| Deadline Description | Milestone Date |\n| :--- | :--- |\n"
        for desc, dt in sorted_fb:
            # Format nicely
            dt_str = dt.strftime("%A, %b %d, %Y")
            if "Closing" in desc:
                fb_table_md += f"| 🔒 **{desc}** | **{dt_str}** |\n"
            elif "Walk-through" in desc:
                fb_table_md += f"| 🚶 **{desc}** | *Prior to Closing on {dt.strftime('%b %d, %Y')}* |\n"
            elif "Deposit" in desc:
                fb_table_md += f"| 🟢 **{desc}** | **{dt_str}** |\n"
            elif "Rescission" in desc:
                fb_table_md += f"| 🏢 **{desc}** | **{dt_str}** |\n"
            elif "Expiration" in desc:
                fb_table_md += f"| 🛑 **{desc}** | **{dt_str}** |\n"
            else:
                fb_table_md += f"| {desc} | {dt_str} |\n"
                
        st.markdown(fb_table_md)

# -----------------------------------------------------------------------------------------
# DOWNLOADS AND FOOTERS
# -----------------------------------------------------------------------------------------
# Update download summary to represent sorted v5.0 contents
summary_text = f"""FLORIDA REAL ESTATE CONTRACT DEADLINE CHRONOLOGICAL SUMMARY (V5.0)
Effective Date: {eff_date}
Scheduled Closing Date: {closing_date}

================================-----------------------------------
NABOR CONTRACT CHRONOLOGICAL ROADMAP:
================================-----------------------------------
"""
for idx, (desc, dt) in enumerate(sorted_nab, 1):
    summary_text += f"{idx}. {desc}: {dt.strftime('%A, %b %d, %Y')}\n"

summary_text += """
================================-----------------------------------
FAR/BAR CONTRACT CHRONOLOGICAL ROADMAP:
================================-----------------------------------
"""
for idx, (desc, dt) in enumerate(sorted_fb, 1):
    summary_text += f"{idx}. {desc}: {dt.strftime('%A, %b %d, %Y')}\n"

st.sidebar.download_button(
    label="📥 Download Chronological Schedule Summary",
    data=summary_text,
    file_name="florida-contract-deadlines-schedule-v5.txt",
    mime="text/plain"
)
