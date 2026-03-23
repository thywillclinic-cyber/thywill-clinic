import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 1. SYSTEM CONFIG & STYLING ---
st.set_page_config(page_title="Uganda Clinic Pro", layout="wide")

# Initialize Session Data
if 'db' not in st.session_state:
    st.session_state.db = {
        "patients": [],
        "lab_orders": [],
        "inventory": pd.DataFrame([
            {"Item": "Coartem", "Stock": 50, "Price": 5000, "Cost": 3000, "Expiry": "2025-06-01"},
            {"Item": "Amoxicillin", "Stock": 10, "Price": 2000, "Cost": 1200, "Expiry": "2024-08-15"}
        ]),
        "sales": [],
        "expenses": [],
        "attendance": [],
        "leave_requests": [],
        "messages": []
    }

# --- 2. AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login_page():
    st.title("🏥 Clinic Management System")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.subheader("Attendant Login")
        phone = st.text_input("Mobile Phone Number")
        pwd = st.text_input("Password", type="password")
        if st.button("Access System", use_container_width=True):
            if phone == "256772475760" and pwd == "96985255":
                st.session_state.logged_in = True
                st.session_state.user = "Admin"
                # Auto-Attendance
                st.session_state.db["attendance"].append({"Staff": phone, "Date": date.today(), "Time": datetime.now().strftime("%H:%M")})
                st.rerun()
            else:
                st.error("Access Denied: Incorrect credentials")

# --- 3. MAIN APP MODULES ---
def main():
    st.sidebar.title("UG Clinic Pro")
    st.sidebar.info(f"User: {st.session_state.user} | UGX")
    
    menu = ["Reception", "Nursing (Triage)", "Consultation", "Laboratory", "Pharmacy (POS)", 
            "Family Planning/Maternity", "Inventory", "Accounts & Expenses", "Staff & Chat"]
    choice = st.sidebar.radio("Navigate Department", menu)

    # --- RECEPTION ---
    if choice == "Reception":
        st.header("Patient Registration")
        with st.form("reg_form"):
            name = st.text_input("Patient Name")
            contact = st.text_input("Phone Number")
            reason = st.selectbox("Reason", ["Checkup", "Antenatal", "Lab Tests", "Emergency"])
            if st.form_submit_button("Register Patient"):
                st.session_state.db["patients"].append({"name": name, "contact": contact, "status": "Triage", "vitals": {}})
                st.success("Patient Registered Successfully")

    # --- CONSULTATION ---
    elif choice == "Consultation":
        st.header("Medical Consultation")
        if not st.session_state.db["patients"]: st.warning("No patients in queue")
        else:
            p_idx = st.selectbox("Select Patient", range(len(st.session_state.db["patients"])), format_func=lambda x: st.session_state.db["patients"][x]["name"])
            patient = st.session_state.db["patients"][p_idx]
            
            st.write(f"**Vitals History:** {patient['vitals']}")
            history = st.text_area("Patient History & Examination")
            diagnosis = st.text_input("Diagnosis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Lab Request")
                tests = st.multiselect("Select Tests", ["Malaria RDT", "CBC", "Urinalysis", "HCG"])
                if st.button("Send to Lab"):
                    st.session_state.db["lab_orders"].append({"patient": patient['name'], "tests": tests, "status": "Pending", "results": ""})
            
            with col2:
                st.subheader("Prescription")
                presc = st.multiselect("Drugs", st.session_state.db["inventory"]["Item"])
                if st.button("Send to Pharmacy"):
                    st.success("Prescription Sent")

    # --- LABORATORY ---
    elif choice == "Laboratory":
        st.header("Laboratory Services")
        for i, order in enumerate(st.session_state.db["lab_orders"]):
            with st.expander(f"Order for {order['patient']}"):
                st.write(f"Tests: {order['tests']}")
                res = st.text_area("Input Results", key=f"lab_{i}")
                if st.button("Submit Results", key=f"btn_{i}"):
                    order['results'] = res
                    order['status'] = "Completed"
                    st.success("Results updated for doctor")

    # --- PHARMACY POS ---
    elif choice == "Pharmacy (POS)":
        st.header("Pharmacy Point of Sale")
        col1, col2 = st.columns([2,1])
        with col1:
            item = st.selectbox("Select Drug", st.session_state.db["inventory"]["Item"])
            qty = st.number_input("Quantity", 1)
            disc = st.number_input("Discount (UGX)", 0)
            price = st.session_state.db["inventory"].loc[st.session_state.db["inventory"]["Item"] == item, "Price"].values[0]
            cost = st.session_state.db["inventory"].loc[st.session_state.db["inventory"]["Item"] == item, "Cost"].values[0]
            total = (qty * price) - disc
            if st.button("Complete Sale (UGX " + str(total) + ")"):
                st.session_state.db["sales"].append({"item": item, "total": total, "profit": total - (qty * cost), "date": date.today()})
                st.balloons()
        
        with col2:
            st.subheader("Stock Alerts")
            low_stock = st.session_state.db["inventory"][st.session_state.db["inventory"]["Stock"] < 15]
            st.dataframe(low_stock)

    # --- MATERNITY & FP ---
    elif choice == "Family Planning/Maternity":
        st.header("Maternity & Family Planning (UCG Guidelines)")
        tab1, tab2 = st.tabs(["ANC & Delivery", "Family Planning"])
        with tab1:
            st.write("Uganda Clinical Guidelines 2023 - Monitoring Tool")
            st.number_input("Gestation Weeks", 0, 42)
            st.selectbox("ANC Visit Number", [1, 2, 3, 4, 5, 6, 7, 8])
            st.text_area("Partograph Progress Note")
            st.button("Request Maternity Lab Panel")
        with tab2:
            st.selectbox("Method", ["Sayana Press", "Implant", "IUD", "Pills"])
            st.button("Record Service")

    # --- STAFF MANAGEMENT & CHAT ---
    elif choice == "Staff & Chat":
        st.header("Staff Management")
        t1, t2, t3 = st.tabs(["Chat & Announcements", "Attendance", "Leave/Off"])
        with t1:
            msg = st.text_input("Post Announcement")
            if st.button("Send"): st.session_state.db["messages"].append(msg)
            for m in st.session_state.db["messages"]: st.info(m)
        with t2:
            st.table(st.session_state.db["attendance"])
        with t3:
            st.subheader("Apply for Leave/Off")
            st.date_input("Start Date")
            st.selectbox("Type", ["Annual Leave", "Sick Leave", "Off Day"])
            if st.button("Submit Request"): st.success("Request sent to Admin")

    # --- ACCOUNTS ---
    elif choice == "Accounts & Expenses":
        st.header("Financial Reports (UGX)")
        sales_df = pd.DataFrame(st.session_state.db["sales"])
        total_rev = sales_df["total"].sum() if not sales_df.empty else 0
        total_prof = sales_df["profit"].sum() if not sales_df.empty else 0
        
        st.metric("Total Revenue", f"UGX {total_rev:,}")
        st.metric("Net Profit", f"UGX {total_prof:,}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- RUN APP ---
if not st.session_state.logged_in:
    login_page()
else:
    main()
