import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Team Portal", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { font-weight: bold; font-size: 16px; }
    .stProgress > div > div > div > div { background-color: #28a745; }
    </style>
""", unsafe_allow_html=True)

# --- 2. GOOGLE SHEET CONNECTION ---
@st.cache_resource
def connect_to_sheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("key.json", scope)
        client = gspread.authorize(creds)
        # APNI SHEET KA NAAM YAHAN LIKHEIN
        sheet = client.open("Team_App_Data") 
        return sheet
    except Exception as e:
        st.error(f"something gone wrong")

db_sheet = connect_to_sheet()

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'language' not in st.session_state:
    st.session_state['language'] = "English"

# --- 4. SIDEBAR MENU ---
st.sidebar.title("Main Menu")

if not st.session_state['logged_in']:
    menu = st.sidebar.radio("Login Required", ["Login Tab"])
else:
    menu = st.sidebar.radio("Navigation", [
        "Meetings", "Teams", "Planning vs Reality", 
        "Reports", "Notice Board", "Settings"
    ])
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

def save_data(tab_name, data_list):
    if db_sheet:
        try:
            worksheet = db_sheet.worksheet(tab_name)
            worksheet.append_row(data_list)
            st.success("Data Google Sheet me save ho gaya!")
        except Exception as e:
            st.error(f"Sheet '{tab_name}' nahi mili. Kripya Google Sheet me tab banayein.")
    else:
        st.error("Google Sheet connect nahi hai. Kripya key.json check karein.")

# --- TABS LOGIC ---

if menu == "Login Tab":
    st.title("Employee Login")
    emp_id = st.text_input("Employee ID")
    password = st.text_input("Password", type="password")
    if st.button("Login Now"):
        if emp_id == "admin" and password == "1234":  
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Galat ID ya Password!")

elif menu == "Meetings":
    st.title("Meetings Portal")
    t1, t2, t3 = st.tabs(["Attendance", "Meeting Polls", "Final Decision"])
    
    with t1:
        st.subheader("Meeting Attendance")
        date_val = st.date_input("Date")
        attending = st.radio("Are you attending?", ["Yes", "No"])
        reason = st.text_area("Reason (If No)")
        if st.button("Submit Attendance"):
            save_data("Meeting_Attendance", [str(date_val), attending, reason])
            
    with t2:
        st.subheader("Meeting Decision Form")
        m_name = st.text_input("Name")
        m_fname = st.text_input("Father's Name")
        m_place = st.text_input("Place")
        m_date = st.date_input("Meeting Date")
        m_day = st.text_input("Day")
        m_time = st.time_input("Time")
        m_agenda = st.text_area("Agenda")
        
        st.write("📊 **Voting Progress (Live Example)**")
        st.progress(70, text="Friday (70%)")
        st.progress(20, text="Sunday (20%)")
        
        if st.button("Submit Meeting Info"):
            save_data("Meeting_Polls", [m_name, m_fname, m_place, str(m_date), m_day, str(m_time), m_agenda])
            
    with t3:
        st.subheader("Decision Result")
        final_dec = st.text_area("Final Approved Decision")
        if st.button("Publish Decision"):
            save_data("Meeting_Decisions", [final_dec])

elif menu == "Teams":
    st.title("Teams Data Entry")
    team = st.selectbox("Select Team", ["Jury Team", "Task Team", "Monitoring Team", "Data Team"])
    
    name = st.text_input("1. Name & Father's Name")
    
    if team == "Jury Team":
        action = st.selectbox("2. Rule Action", ["Purpose a new rule", "Remove an old rule", "Amend a rule"])
        detail = st.text_area("3. Details of the rule")
        reason = st.text_area("4. Reason and arguments")
        need = st.text_area("5. Need of this rule")
        if st.button("Save Jury Data"):
            save_data("Jury_Team", [name, action, detail, reason, need])
            
    elif team == "Task Team":
        task_type = st.selectbox("2. Task Type", ["Demand for something", "Voice against evil", "Social welfare", "Masjid and deen"])
        detail = st.text_area("3. Details of task")
        challenges = st.text_area("4. Challenges in completion")
        achieve = st.text_area("5. Achievement")
        if st.button("Save Task Data"):
            save_data("Task_Team", [name, task_type, detail, challenges, achieve])
            
    elif team == "Monitoring Team":
        action = st.selectbox("2. Action", ["Appraisal", "Complaint"])
        detail = st.text_area("3. Details")
        decision = st.text_area("4. Decision")
        remarks = st.text_area("5. Other remarks")
        if st.button("Save Monitoring Data"):
            save_data("Monitoring_Team", [name, action, detail, decision, remarks])
            
    elif team == "Data Team":
        d_date = st.date_input("2. Date")
        m_num = st.text_input("3. Meeting number")
        m_agenda = st.text_area("4. Meeting agenda")
        conclusion = st.text_area("5. Conclusion")
        if st.button("Save Data Team Info"):
            save_data("Data_Team", [name, str(d_date), m_num, m_agenda, conclusion])

elif menu == "Planning vs Reality":
    st.title("Planning vs Reality")
    plan = st.text_area("1. Plan")
    how_much = st.text_area("2. How much has completed")
    pending = st.text_area("3. Pending")
    wip = st.text_area("4. Work in Progress")
    prog = st.slider("Completion %", 0, 100, 50)
    st.progress(prog, text=f"Progress: {prog}%")
    if st.button("Save Progress"):
        save_data("Planning", [plan, how_much, pending, wip, prog])

elif menu == "Reports":
    st.title("Performance Reports")
    filter_type = st.radio("Select duration:", ["Last 15 Days", "Last 30 Days", "Up to 6 Months"])
    
    if db_sheet:
        st.write("Fetching real data from Google Sheets...")
        try:
            task_sheet = db_sheet.worksheet("Task_Team").get_all_records()
            if len(task_sheet) > 0:
                df = pd.DataFrame(task_sheet)
                st.bar_chart(df['Task Type'].value_counts())
            else:
                st.info("Sheet me abhi koi data nahi hai charts banane ke liye.")
        except:
            st.warning("Data load nahi ho paya. Tabs check karein.")
    else:
        st.error("Google Sheet connect nahi hai. Data nahi dikh sakta.")

elif menu == "Notice Board":
    st.title("Notice Board")
    t_name = st.text_input("Team Name")
    notice = st.text_area("Important Notice")
    if st.button("Post Notice"):
        save_data("Notices", [t_name, notice])

elif menu == "Settings":
    st.title("App Settings")
    st.write("Current User: Admin")
    new_lang = st.radio("Choose App Language / भाषा चुनें", ["English", "Hindi"], index=0 if st.session_state['language']=="English" else 1)
    if st.button("Apply Language"):
        st.session_state['language'] = new_lang
        st.success(f"Language set to {new_lang}.")
        st.rerun()