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
    if base_date is None or days is None or days == "-":
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
st.set_page_config(page_title="Florida Real Estate Deadline Calculator v8", layout="wide")

st.title("🌴 Florida Real Estate Contract Deadline Calculator v8.0")
st.markdown("""
An advanced, customizable deadline calculator featuring **Cash vs. Financing toggles**, **AS-IS vs. Standard Inspection toggles**, **Buyer's Additional Deposit**, and **dispute-specific inspection timelines** under **NABOR** and **FAR/BAR** rules. 

**This edition allows you to isolate a single contract type (NABOR or FAR/BAR) or compare them side-by-side.**
""")

# Setup Sidebar Sections
st.sidebar.header("🏢 Section 1: Active Workspace")
active_view = st.sidebar.selectbox(
    "Select Active Contract Form", 
    ["🏢 NABOR (Collier/Lee County)", "⚖️ FAR/BAR (Statewide Standard)", "📊 Comparative View (Both)"],
    index=2,
    help="Isolate NABOR-only, FAR/BAR-only, or show both side-by-side."
)

st.sidebar.markdown("---")
st.sidebar.header("📅 Section 2: Key Base Dates")

# Set default dates to match the user's example for instant verification
eff_date = st.sidebar.date_input("Effective Date (Day 0)", datetime.date.today()) # Default to today's date
closing_date = st.sidebar.date_input("Scheduled Closing Date", value=None)  #This keeps the field empty until a date is selected

# Options and Toggles for contract terms
st.sidebar.subheader("⚙️ Contract Options")
funding_type = st.sidebar.selectbox("Funding Type", ["Financing", "Cash"], index=1, help="If Cash is selected, Loan Application and Financing Contingency are omitted.") # Cash by default to match example
has_inspection = st.sidebar.selectbox("Inspection Option", ["Yes", "No"], index=0, help="If No is selected, all inspection-related deadlines are omitted.")

# Contract style applies differently depending on active view
is_nabor_active = active_view == "NABOR (Collier/Lee County)" or active_view == "📊 Comparative View (Both)"
is_fb_active = active_view == "FAR/BAR (Statewide Standard)" or active_view == "📊 Comparative View (Both)"

contract_style = "AS-IS"
if is_nabor_active:
    contract_style = st.sidebar.selectbox("Contract Style", ["AS-IS", "Standard"], index=0, help="NABOR Standard triggers the structured 5-10-5 repair dispute steps. AS-IS contracts omit these steps.")

# Deposit amounts
st.sidebar.subheader("💰 Escrow Deposit Amounts")
initial_dep_val = st.sidebar.number_input("Initial Deposit Amount ($)", value=5000, step=1000, help="Used to customize the chronological timelines.")
additional_dep_val = st.sidebar.number_input("Additional Deposit Amount ($)", value=1500, step=1000, help="Used to customize the chronological timelines.")

# Optional inputs (with toggles)
enable_condo = st.sidebar.checkbox("Include Condo Documents Timelines", value=True)
condo_date = None
if enable_condo:
    condo_date = st.sidebar.date_input("Condo Docs Delivery Date", datetime.date.today()) # Default to today's date

enable_assoc = st.sidebar.checkbox("Include HOA/Association Timeline", value=True)
assoc_date = None
if enable_assoc:
    assoc_date = st.sidebar.date_input(
        "Association App Receipt Date", 
        value=None,  # This keeps the field empty until a date is selected
        help="Select the date the buyer received the homeowner association application package."
    )
enable_dispute = has_inspection == "Yes" and contract_style == "Standard" and is_nabor_active
election_date = None
seller_resp_date = None
if enable_dispute:
    election_date = st.sidebar.date_input("Inspection Election Delivery Date", value=None)  #This keeps the field empty until a date is selected
    seller_resp_date = st.sidebar.date_input("Seller Response to Election Date", value=None)  #This keeps the field empty until a date is selected

# Custom Offsets
st.sidebar.markdown("---")
st.sidebar.header("Section 3: Custom Milestone Offsets")

with st.sidebar.expander("Escrow & Financing Offsets"):
    dep_offset = st.number_input("Initial Deposit (Days after)", value=3, min_value=0)
    add_dep_offset = st.number_input("Additional Deposit (Days after)", value=15, min_value=0) # Default to 8 to match example
    loan_app_offset = st.number_input("Loan Application (Days after)", value=5, min_value=0)
    nab_fin_offset = st.number_input("NABOR Financing (Days after)", value=45, min_value=0)
    fb_fin_offset = st.number_input("FAR/BAR Financing (Days after)", value=30, min_value=0)

with st.sidebar.expander("Inspection & Dispute Offsets"):
    insp_offset = st.number_input("Inspection Period (Days after)", value=15, min_value=0) # Default to 7 to match example
    election_offset = st.number_input("Buyer Election (Days after Inspection end)", value=5, min_value=0)
    seller_offset = st.number_input("Seller Response (Days after Buyer Election)", value=10, min_value=0)
    terminate_offset = st.number_input("Buyer Terminate Right (Days after Seller Response)", value=5, min_value=0)

with st.sidebar.expander("🏢Association & Condo Offsets"):
    assoc_app_offset = st.number_input("Association Filing (Days after receipt)", value=10, min_value=0)
    condo_resciss_offset = st.number_input("Condo Rescission Period (Business Days)", value=7, min_value=0)

with st.sidebar.expander("Title & Survey Offsets (Backward-looking)"):
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

# Financing (Omit if CASH)
nab_loan_app, nab_loan_note = None, "N/A - Cash Transaction"
fb_loan_app, fb_loan_note = None, "N/A - Cash Transaction"
nab_fin, nab_fin_note = None, "N/A - Cash Transaction"
fb_fin, fb_fin_note = None, "N/A - Cash Transaction"

if funding_type == "Financing":
    nab_loan_app, nab_loan_note = calculate_deadline(eff_date, loan_app_offset, "forward", holidays_cache)
    fb_loan_app, fb_loan_note = calculate_deadline(eff_date, loan_app_offset, "forward", holidays_cache)
    nab_fin, nab_fin_note = calculate_deadline(eff_date, nab_fin_offset, "forward", holidays_cache)
    fb_fin, fb_fin_note = calculate_deadline(eff_date, fb_fin_offset, "forward", holidays_cache)

# Inspection Deadlines
nab_insp_date, nab_insp_note = None, "N/A - No Inspection"
fb_insp_date, fb_insp_note = None, "N/A - No Inspection"
nab_election, nab_election_note = None, "N/A"
fb_election, fb_election_note = None, "N/A"
nab_seller_resp, nab_seller_note = None, "N/A"
fb_seller_resp, fb_seller_note = None, "N/A"
nab_terminate, nab_terminate_note = None, "N/A"
fb_terminate, fb_terminate_note = None, "N/A"

if has_inspection == "Yes":
    nab_insp_date, nab_insp_note = calculate_deadline(eff_date, insp_offset, "forward", holidays_cache)
    fb_insp_date, fb_insp_note = calculate_deadline(eff_date, insp_offset, "forward", holidays_cache)
    
    # If AS-IS, we do not trigger the repair dispute elections
    if contract_style == "Standard":
        nab_election, nab_election_note = calculate_deadline(nab_insp_date, election_offset, "forward", holidays_cache)
        fb_election, fb_election_note = calculate_deadline(fb_insp_date, election_offset, "forward", holidays_cache)
        
        nab_seller_resp, nab_seller_note = calculate_deadline(election_date, seller_offset, "forward", holidays_cache)
        fb_seller_resp, fb_seller_note = (None, "N/A")
        
        nab_terminate, nab_terminate_note = calculate_deadline(seller_resp_date, terminate_offset, "forward", holidays_cache)
        fb_terminate, fb_terminate_note = (None, "N/A")
    else:
        nab_election_note = "N/A - AS-IS Contract"
        fb_election_note = "N/A (Submit during inspection)"

# Condo Rescission (Business Days)
nab_condo, nab_condo_note = calculate_business_days_deadline(condo_date, condo_resciss_offset, holidays_cache) if enable_condo else (None, "")
fb_condo, fb_condo_note = calculate_business_days_deadline(condo_date, condo_resciss_offset, holidays_cache) if enable_condo else (None, "")

# Association Application Filing
nab_assoc, nab_assoc_note = calculate_deadline(assoc_date, assoc_app_offset, "forward", holidays_cache) if enable_assoc else (None, "")
fb_assoc, fb_assoc_note = calculate_deadline(assoc_date, assoc_app_offset, "forward", holidays_cache) if enable_assoc else (None, "")

# Title & Survey (Backward-looking relative to actual Closing)
nab_title, nab_title_note = calculate_deadline(rolled_closing_nab, title_offset, "backward", holidays_cache)
fb_title, fb_title_note = calculate_deadline(rolled_closing_fb, title_offset, "backward", holidays_cache)

nab_survey, nab_survey_note = calculate_deadline(rolled_closing_nab, survey_offset, "backward", holidays_cache)
fb_survey, fb_survey_note = calculate_deadline(rolled_closing_fb, survey_offset, "backward", holidays_cache)

# -----------------------------------------------------------------------------------------
# DEFINE TABS FOR DETAILED VS CLIENT VIEW
# -----------------------------------------------------------------------------------------
tab_title_1 = "🎛️ Detailed Comparative Calculator"
tab_title_2 = "📋 Simplified Client Summaries"

if active_view == "🏢 NABOR (Collier/Lee County)":
    tab_title_1 = "NABOR Detailed Calculator"
    tab_title_2 = "📋 NABOR Client Roadmap"
elif active_view == "⚖️ FAR/BAR (Statewide Standard)":
    tab_title_1 = "FAR/BAR Detailed Calculator"
    tab_title_2 = "📋 FAR/BAR Client Roadmap"

tab1, tab2 = st.tabs([tab_title_1, tab_title_2])

with tab1:
    col1, col2 = st.columns(2)

    # Render columns depending on active_view
    show_nabor = active_view == "🏢 NABOR (Collier/Lee County)" or active_view == "📊 Comparative View (Both)"
    show_fb = active_view == "⚖️ FAR/BAR (Statewide Standard)" or active_view == "📊 Comparative View (Both)"

    if show_nabor:
        with (col1 if active_view == "📊 Comparative View (Both)" else st.container()):
            st.header("NABOR Contract Milestones")
            st.markdown("**Naples Area Board of Realtors Rules**")
            st.metric("Effective Date (Day 0)", eff_date.strftime("%A, %B %d, %Y"))
            
            st.subheader("🗓️ Calendar Milestones")
            
            st.write(f"🟢 **Initial Escrow Deposit**: {nab_dep_date.strftime('%A, %b %d, %Y')} *({dep_offset} days after)*")
            if nab_dep_note: st.caption(f"ℹ️ {nab_dep_note}")
            
            st.write(f"🔵 **Buyer's Additional Deposit**: {nab_add_dep_date.strftime('%A, %b %d, %Y')} *({add_dep_offset} days after)*")
            if nab_add_dep_note: st.caption(f"ℹ️ {nab_add_dep_note}")
            
            if funding_type == "Financing" and nab_loan_app:
                st.write(f"📝 **Buyer's Loan Application**: {nab_loan_app.strftime('%A, %b %d, %Y')} *({loan_app_offset} days after)*")
                if nab_loan_note: st.caption(f"ℹ️ {nab_loan_note}")
            else:
                st.write(f"📝 **Buyer's Loan Application**: 🚫 **{nab_loan_note}**")
            
            if has_inspection == "Yes" and nab_insp_date:
                st.write(f"🔍 **Inspection / Due Diligence Period**: {nab_insp_date.strftime('%A, %b %d, %Y')} *({insp_offset} days after)*")
                if nab_insp_note: st.caption(f"ℹ️ {nab_insp_note}")
                
                if contract_style == "Standard" and nab_election:
                    st.write(f"✏️ **Buyer Election of Defective Items**: {nab_election.strftime('%A, %b %d, %Y')} *({election_offset} days after inspection)*")
                    if nab_election_note: st.caption(f"ℹ️ {nab_election_note}")
                    
                    if nab_seller_resp:
                        st.write(f"🤝 **Seller's Response to Election**: {nab_seller_resp.strftime('%A, %b %d, %Y')} *({seller_offset} days after buyer election)*")
                        if nab_seller_note: st.caption(f"ℹ️ {nab_seller_note}")
                        
                    if nab_terminate:
                        st.write(f"❌ **Buyer's Right to Terminate**: {nab_terminate.strftime('%A, %b %d, %Y')} *({terminate_offset} days after seller response)*")
                        if nab_terminate_note: st.caption(f"ℹ️ {nab_terminate_note}")
                else:
                    st.write(f"✏️ **Inspection Repairs / Disputes**: 🚫 **{nab_election_note}**")
            else:
                st.write(f"🔍 **Inspection / Due Diligence**: 🚫 **{nab_insp_note}**")
                
            if enable_assoc and nab_assoc:
                st.write(f"📄 **Buyer Application for Association Approval**: {nab_assoc.strftime('%A, %b %d, %Y')} *({assoc_app_offset} days after receipt)*")
                if nab_assoc_note: st.caption(f"ℹ️ {nab_assoc_note}")
                
            if enable_condo and nab_condo:
                st.write(f"🏢 **Condominium Rescission Period**: {nab_condo.strftime('%A, %b %d, %Y')} *({condo_resciss_offset} Business Days after receipt)*")
                if nab_condo_note: st.caption(f"ℹ️ {nab_condo_note}")
                
            if funding_type == "Financing" and nab_fin:
                st.write(f"💰 **Financing Contingency**: {nab_fin.strftime('%A, %b %d, %Y')} *({nab_fin_offset} days after)*")
                if nab_fin_note: st.caption(f"ℹ️ {nab_fin_note}")
            else:
                st.write(f"💰 **Financing Contingency**: 🚫 **{nab_fin_note}**")
            
            st.write(f"📋 **Title Evidence**: {nab_title.strftime('%A, %b %d, %Y')} *({title_offset} days prior)*")
            if nab_title_note: st.caption(f"ℹ️ {nab_title_note}")
            
            st.write(f"📐 **Survey Deadline**: {nab_survey.strftime('%A, %b %d, %Y')} *({survey_offset} days prior)*")
            if nab_survey_note: st.caption(f"ℹ️ {nab_survey_note}")
            
            st.write(f"🚶 **Buyer Walk-through Inspection**: Prior to Closing Date / {rolled_closing_nab.strftime('%A, %b %d, %Y')} *(or possession if earlier)*")
            
            st.metric("🔒 Rolled Closing Date", rolled_closing_nab.strftime("%A, %B %d, %Y"))
            if closing_nab_note: st.caption(f"ℹ️ {closing_nab_note}")

    if show_fb:
        with (col2 if active_view == "📊 Comparative View (Both)" else st.container()):
            st.header("⚖️ FAR/BAR Contract Milestones")
            st.markdown("**Florida Realtors/Florida Bar Rules**")
            st.metric("Effective Date (Day 0)", eff_date.strftime("%A, %B %d, %Y"))
            
            st.subheader("🗓️ Calendar Milestones")
            
            st.write(f"🟢 **Initial Escrow Deposit**: {fb_dep_date.strftime('%A, %b %d, %Y')} *({dep_offset} days after)*")
            if fb_dep_note: st.caption(f"ℹ️ {fb_dep_note}")
            
            st.write(f"🔵 **Buyer's Additional Deposit**: {fb_add_dep_date.strftime('%A, %b %d, %Y')} *({add_dep_offset} days after)*")
            if fb_add_dep_note: st.caption(f"ℹ️ {fb_add_dep_note}")
            
            if funding_type == "Financing" and fb_loan_app:
                st.write(f"📝 **Buyer's Loan Application**: {fb_loan_app.strftime('%A, %b %d, %Y')} *({loan_app_offset} days after)*")
                if fb_loan_note: st.caption(f"ℹ️ {fb_loan_note}")
            else:
                st.write(f"📝 **Buyer's Loan Application**: 🚫 **{fb_loan_note}**")
            
            if has_inspection == "Yes" and fb_insp_date:
                st.write(f"🔍 **Inspection / Due Diligence Period**: {fb_insp_date.strftime('%A, %b %d, %Y')} *({insp_offset} days after)*")
                if fb_insp_note: st.caption(f"ℹ️ {fb_insp_note}")
                st.write(f"✏️ **Inspection Repairs / Disputes**: 🚫 *FAR/BAR does not support post-inspection multi-step dispute timelines. All negotiations/cancellations must be executed within the inspection period.*")
            else:
                st.write(f"🔍 **Inspection / Due Diligence**: 🚫 **{fb_insp_note}**")
                
            if enable_assoc and fb_assoc:
                st.write(f"📄 **Buyer Application for Association Approval**: {fb_assoc.strftime('%A, %b %d, %Y')} *({assoc_app_offset} days after receipt)*")
                if fb_assoc_note: st.caption(f"ℹ️ {fb_assoc_note}")
                
            if enable_condo and fb_condo:
                st.write(f"🏢 **Condominium Rescission Period**: {fb_condo.strftime('%A, %b %d, %Y')} *({condo_resciss_offset} Business Days after receipt)*")
                if fb_condo_note: st.caption(f"ℹ️ {fb_condo_note}")
                
            if funding_type == "Financing" and fb_fin:
                st.write(f"💰 **Financing Contingency**: {fb_fin.strftime('%A, %b %d, %Y')} *({fb_fin_offset} days after)*")
                if fb_fin_note: st.caption(f"ℹ️ {fb_fin_note}")
            else:
                st.write(f"💰 **Financing Contingency**: 🚫 **{fb_fin_note}**")
            
            st.write(f"📋 **Title Evidence**: {fb_title.strftime('%A, %b %d, %Y')} *({title_offset} days prior)*")
            if fb_title_note: st.caption(f"ℹ️ {fb_title_note}")
            
            st.write(f"📐 **Survey Deadline**: {fb_survey.strftime('%A, %b %d, %Y')} *({survey_offset} days prior)*")
            if fb_survey_note: st.caption(f"ℹ️ {fb_survey_note}")
            
            st.write(f"🚶 **Buyer Walk-through Inspection**: Prior to Closing Date / {rolled_closing_fb.strftime('%A, %b %d, %Y')} *(or possession if earlier)*")
            
            st.metric("🔒 Rolled Closing Date", rolled_closing_fb.strftime("%A, %B %d, %Y"))
            if closing_fb_note: st.caption(f"ℹ️ {closing_fb_note}")

    st.markdown("---")
    st.subheader("⚖️ Advanced Real Estate Rule Summary")
    if active_view == "🏢 NABOR (Collier/Lee County)":
        st.markdown("""
        - **Day Zero Rule**: Counting starts the day *after* the contract's Effective Date (meaning Day 1 is the day after).
        - **Condo Rescission**: Under Florida Statute § 718.503, the **7-day resale cancel period** counts strictly in **Business Days** (excluding weekends and federal holidays).
        - **NABOR Standard vs AS-IS**: Under a NABOR Standard contract, the inspection initiates a formal 5-10-5 day Repair/Dispute timeline (Buyer Election, Seller Response, Buyer right to terminate). Under a NABOR AS-IS contract, the buyer has a simple right to terminate *before* the Inspection Period expires, with no multi-step repair dispute processes.
        """)
    elif active_view == "⚖️ FAR/BAR (Statewide Standard)":
        st.markdown("""
        - **Day Zero Rule**: Counting starts the day *after* the contract's Effective Date (meaning Day 1 is the day after).
        - **Condo Rescission**: Under Florida Statute § 718.503, the **7-day resale cancel period** counts strictly in **Business Days** (excluding weekends and federal holidays).
        - **FAR/BAR Standard vs AS-IS**: Under FAR/BAR Standard, the seller has pre-agreed financial repair limits (usually 1.5%). Under FAR/BAR AS-IS, there are no seller repair obligations, and the buyer can simply terminate prior to inspection expiration.
        """)
    else:
        st.markdown("""
        - **Day Zero Rule**: Both contracts agree that counting starts the day *after* the contract's Effective Date (meaning Day 1 is the day after).
        - **Condo Rescission**: Under Florida Statute § 718.503, the **7-day resale cancel period** counts strictly in **Business Days** (excluding weekends and federal holidays).
        - **NABOR Standard vs AS-IS**: Under a NABOR Standard contract, the inspection initiates a formal 5-10-5 day Repair/Dispute timeline (Buyer Election, Seller Response, Buyer right to terminate). Under a NABOR AS-IS contract, the buyer has a simple right to terminate *before* the Inspection Period expires, with no multi-step repair dispute processes.
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
        nab_milestones.append((f"Escrow: Initial Escrow Deposit (${initial_dep_val:,.0f})", nab_dep_date))
    if nab_add_dep_date:
        nab_milestones.append((f"Escrow: Buyer's Additional Deposit (${additional_dep_val:,.0f})", nab_add_dep_date))
    if funding_type == "Financing" and nab_loan_app:
        nab_milestones.append(("Financing: Buyer's Loan Application Deadline", nab_loan_app))
    if has_inspection == "Yes" and nab_insp_date:
        nab_milestones.append(("Inspections: Inspection Period Expiration", nab_insp_date))
        if contract_style == "Standard" and nab_election:
            nab_milestones.append(("Inspections: Buyer Defective Items Notice Election", nab_election))
            if nab_seller_resp:
                nab_milestones.append(("Inspections: Seller Response to Defective Items", nab_seller_resp))
            if nab_terminate:
                nab_milestones.append(("Inspections: Buyer Right to Terminate Expiration", nab_terminate))
    if enable_assoc and nab_assoc:
        nab_milestones.append(("Association: Buyer Membership Filing Deadline", nab_assoc))
    if enable_condo and nab_condo:
        nab_milestones.append(("Condominium: 7-Business-Day Rescission Expiration", nab_condo))
    if funding_type == "Financing" and nab_fin:
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
        fb_milestones.append((f"Escrow: Initial Escrow Deposit (${initial_dep_val:,.0f})", fb_dep_date))
    if fb_add_dep_date:
        fb_milestones.append((f"Escrow: Buyer's Additional Deposit (${additional_dep_val:,.0f})", fb_add_dep_date))
    if funding_type == "Financing" and fb_loan_app:
        fb_milestones.append(("Financing: Buyer's Loan Application Deadline", fb_loan_app))
    if has_inspection == "Yes" and fb_insp_date:
        fb_milestones.append(("Inspections: Inspection / Due Diligence Expiration", fb_insp_date))
    if enable_assoc and fb_assoc:
        fb_milestones.append(("Association: Buyer Membership Filing Deadline", fb_assoc))
    if enable_condo and fb_condo:
        fb_milestones.append(("Condominium: 7-Business-Day Rescission Expiration", fb_condo))
    if funding_type == "Financing" and fb_fin:
        fb_milestones.append(("Financing: Financing Contingency Expiration", fb_fin))
    if fb_title:
        fb_milestones.append(("Title: Title Evidence Due Date", fb_title))
    if fb_survey:
        fb_milestones.append(("Survey: Boundary Survey Due Date", fb_survey))
    fb_milestones.append(("Walk-through: Pre-Closing Final Walk-through Inspection (Prior to)", rolled_closing_fb))
    fb_milestones.append(("Closing: Actual Closing & Ownership Transfer", rolled_closing_fb))

    sorted_fb = sorted([m for m in fb_milestones if m[1] is not None], key=lambda x: x[1])

    # Display summaries depending on selected active_view
    sum_col1, sum_col2 = st.columns(2)
    
    if show_nabor:
        with (sum_col1 if active_view == "📊 Comparative View (Both)" else st.container()):
            st.subheader("🏢 NABOR Milestones Schedule")
            st.markdown(f"**Funding Type:** `{funding_type}` | **Inspection:** `{has_inspection}` " + (f"| **Style:** `{contract_style}`" if has_inspection == "Yes" else ""))
            
            # Build Markdown Table for NABOR
            nab_table_md = "| Deadline Description | Milestone Date |\n| :--- | :--- |\n"
            for desc, dt in sorted_nab:
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
            
    if show_fb:
        with (sum_col2 if active_view == "📊 Comparative View (Both)" else st.container()):
            st.subheader("⚖️ FAR/BAR Milestones Schedule")
            st.markdown(f"**Funding Type:** `{funding_type}` | **Inspection:** `{has_inspection}`")
            
            # Build Markdown Table for FAR/BAR
            fb_table_md = "| Deadline Description | Milestone Date |\n| :--- | :--- |\n"
            for desc, dt in sorted_fb:
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
    # DYNAMIC PLAIN TEXT CLIENT TIMELINES (REPRESENTING THE EXACT FORMAT REQUESTED)
    # -----------------------------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📋 Plain Text Client Timelines (Copy & Paste Summary)")
    st.markdown("""
    These text summaries are generated using custom-aligned rows, **chronologically sorted in ascending order**, and formatted with your custom deposit amounts. 
    You can easily copy and paste them directly to your clients!
    """)

    # Helper function to format date exactly like user's format: MM/DD/YY (Day) mapping Thu -> Thur
    def client_date_formatter(dt):
        if dt is None:
            return "TBD"
        day_str = dt.strftime("%a")
        if day_str == "Thu":
            day_str = "Thur"
        return f"{dt.strftime('%m/%d/%y')} ({day_str})"

    # Generate milestones list for text block
    def build_text_list(calc_closing, is_nabor):
        t_list = []
        t_list.append(("Effective Date:", eff_date))
        t_list.append((f"Buyers' Initial Deposit (${initial_dep_val:,.0f}) {dep_offset} Days", nab_dep_date if is_nabor else fb_dep_date))
        
        if has_inspection == "Yes":
            t_list.append(("Inspection", None))
            t_list.append((f"Buyer's Due Diligence Period ({insp_offset} Days)", nab_insp_date if is_nabor else fb_insp_date))
            if is_nabor and contract_style == "Standard" and nab_election:
                t_list.append((f"Buyer Defective Items Notice Election ({election_offset} Days)", nab_election))
                if enable_dispute and nab_seller_resp:
                    t_list.append((f"Seller Response to Election ({seller_offset} Days)", nab_seller_resp))
                if enable_dispute and nab_terminate:
                    t_list.append((f"Buyer Right to Terminate ({terminate_offset} Days)", nab_terminate))
                    
        t_list.append((f"Buyer’s Additional Deposit (${additional_dep_val:,.0f}) {add_dep_offset} Days", nab_add_dep_date if is_nabor else fb_add_dep_date))
        
        if enable_condo:
            t_list.append((f"Condominium Doc Rescission Period ({condo_resciss_offset} Business Days)", nab_condo if is_nabor else fb_condo))
        if enable_assoc:
            t_list.append((f"Buyer Application for Association Approval ({assoc_app_offset} Days)", nab_assoc if is_nabor else fb_assoc))
        if funding_type == "Financing":
            t_list.append((f"Buyer's Loan Application Deadline ({loan_app_offset} Days)", nab_loan_app if is_nabor else fb_loan_app))
            t_list.append((f"Financing Contingency Expiration (" + (f"{nab_fin_offset}" if is_nabor else f"{fb_fin_offset}") + " Days)", nab_fin if is_nabor else fb_fin))
            
        t_list.append(("Buyer’s Walk-through:", None))
        t_list.append(("Closing Date:", calc_closing))
        return t_list

    nab_text_milestones = build_text_list(rolled_closing_nab, is_nabor=True)
    fb_text_milestones = build_text_list(rolled_closing_fb, is_nabor=False)

    # Chronological sort (TBDs at the bottom)
    sorted_nab_text = sorted(nab_text_milestones, key=lambda x: (x[1] is None, x[1] if x[1] is not None else datetime.date.max, x[0]))
    sorted_fb_text = sorted(fb_text_milestones, key=lambda x: (x[1] is None, x[1] if x[1] is not None else datetime.date.max, x[0]))

    # Construct the formatted text blocks
    nab_lines = []
    for label, dt in sorted_nab_text:
        d_str = client_date_formatter(dt)
        nab_lines.append(f"{label:<55} {d_str}")
    nab_summary_str = "\n".join(nab_lines)

    fb_lines = []
    for label, dt in sorted_fb_text:
        d_str = client_date_formatter(dt)
        fb_lines.append(f"{label:<55} {d_str}")
    fb_summary_str = "\n".join(fb_lines)

    # Display side-by-side or isolated
    copy_col1, copy_col2 = st.columns(2)
    
    if show_nabor:
        with (copy_col1 if active_view == "📊 Comparative View (Both)" else st.container()):
            st.markdown("#### 🏢 NABOR Client Timeline Summary")
            st.code(nab_summary_str, language="text")
            
    if show_fb:
        with (copy_col2 if active_view == "📊 Comparative View (Both)" else st.container()):
            st.markdown("#### ⚖️ FAR/BAR Client Timeline Summary")
            st.code(fb_summary_str, language="text")

# -----------------------------------------------------------------------------------------
# DOWNLOADS AND FOOTERS
# -----------------------------------------------------------------------------------------
# Update download summary to match isolated selection
summary_text = f"FLORIDA REAL ESTATE CONTRACT DEADLINE CHRONOLOGICAL SUMMARY (V8.0)\n"
summary_text += f"Effective Date: {eff_date}\n"
summary_text += f"Scheduled Closing Date: {closing_date}\n"
summary_text += f"Funding Type: {funding_type}\n"
summary_text += f"Inspection Option: {has_inspection}\n\n"

if show_nabor:
    summary_text += "===================================================================\n"
    summary_text += "🏢 NABOR CONTRACT CHRONOLOGICAL ROADMAP:\n"
    summary_text += "===================================================================\n"
    for idx, (desc, dt) in enumerate(sorted_nab, 1):
        summary_text += f"{idx}. {desc}: {dt.strftime('%A, %b %d, %Y')}\n"
    summary_text += "\n"
    summary_text += "NABOR PLAIN-TEXT FORMAT:\n"
    summary_text += nab_summary_str + "\n\n"

if show_fb:
    summary_text += "===================================================================\n"
    summary_text += "⚖️ FAR/BAR CONTRACT CHRONOLOGICAL ROADMAP:\n"
    summary_text += "===================================================================\n"
    for idx, (desc, dt) in enumerate(sorted_fb, 1):
        summary_text += f"{idx}. {desc}: {dt.strftime('%A, %b %d, %Y')}\n"
    summary_text += "\n"
    summary_text += "FAR/BAR PLAIN-TEXT FORMAT:\n"
    summary_text += fb_summary_str + "\n\n"

st.sidebar.download_button(
    label="📥 Download Chronological Schedule Summary",
    data=summary_text,
    file_name="florida-contract-deadlines-schedule-v8.txt",
    mime="text/plain"
)
