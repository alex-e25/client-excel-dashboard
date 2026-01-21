import streamlit as st
import pandas as pd
import os
import shutil
import datetime

# Directories for data and backups
DATA_DIR = "data"
BACKUP_DIR = "backups"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Function to get file path for a client
def get_client_file(client_id):
    return os.path.join(DATA_DIR, f"{client_id}.xlsx")

# Function to backup file
def backup_file(client_id):
    original_file = get_client_file(client_id)
    if os.path.exists(original_file):
        backup_subdir = os.path.join(BACKUP_DIR, client_id)
        os.makedirs(backup_subdir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_subdir, f"{client_id}_{timestamp}.xlsx")
        shutil.copy(original_file, backup_path)
        st.success(f"Backup created: {backup_path}")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Upload Excel", "Dashboard"])

if page == "Upload Excel":
    st.title("Upload Client Excel File")
    client_id = st.text_input("Client ID (unique identifier, e.g., client123)")
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
    
    if uploaded_file is not None and client_id:
        try:
            df = pd.read_excel(uploaded_file)
            file_path = get_client_file(client_id)
            
            # Backup if existing file
            if os.path.exists(file_path):
                backup_file(client_id)
            
            df.to_excel(file_path, index=False)
            st.success(f"File uploaded and saved for client: {client_id}")
            st.write("Preview:")
            st.dataframe(df)
            
            st.info(f"Shareable dashboard link: ?client={client_id}")
        except Exception as e:
            st.error(f"Error: {e}")

elif page == "Dashboard":
    st.title("Client Dashboard")
    
    # Get client_id from query params or input
    query_params = st.experimental_get_query_params()
    client_id = query_params.get("client", [None])[0]
    if not client_id:
        client_id = st.text_input("Enter Client ID")
    
    if client_id:
        file_path = get_client_file(client_id)
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            
            st.write(f"Dashboard for Client: {client_id}")
            st.write("Edit the statuses below and save changes.")
            
            # Editable dataframe
            edited_df = st.data_editor(df, num_rows="dynamic")
            
            if st.button("Save Changes"):
                try:
                    # Backup before saving
                    backup_file(client_id)
                    
                    edited_df.to_excel(file_path, index=False)
                    st.success("Changes saved successfully!")
                except Exception as e:
                    st.error(f"Error saving changes: {e}")
        else:
            st.error("No file found for this client. Please upload first.")
    else:
        st.warning("Please provide a Client ID.")
