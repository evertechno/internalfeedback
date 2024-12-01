import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Create a SQLite database to store complaints
def create_db():
    conn = sqlite3.connect('complaints.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_text TEXT,
        category TEXT,
        sentiment TEXT,
        urgency TEXT,
        date TIMESTAMP
    )
    conn.commit()
    conn.close()

# Function to store complaint in the database
def store_complaint(complaint_text, category, sentiment, urgency):
    conn = sqlite3.connect('complaints.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO complaints (complaint_text, category, sentiment, urgency, date)
    VALUES (?, ?, ?, ?, ?)
    ''', (complaint_text, category, sentiment, urgency, datetime.now()))
    conn.commit()
    conn.close()

# Function to get complaint history
def get_complaint_history():
    conn = sqlite3.connect('complaints.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM complaints ORDER BY date DESC')
    history = cursor.fetchall()
    conn.close()
    return history

# Initialize the database
create_db()

# Streamlit App UI
st.title("Internal Complaint Tracker with AI Categorization & Sentiment Analysis")
st.write("This app securely collects and categorizes internal complaints, analyzes sentiment, and tracks urgency.")

# Input form to collect complaint
complaint = st.text_area("Enter your complaint:", height=200)

# Dropdown to select category (initially empty, can be updated based on AI's suggestion)
category_options = ["Select category", "Technical Issue", "Human Resources", "Managerial", "Operations", "Other"]
selected_category = st.selectbox("Select or let AI categorize:", category_options)

# Dropdown for urgency
urgency_options = ["Select urgency", "High", "Medium", "Low"]
selected_urgency = st.selectbox("Select urgency level:", urgency_options)

# Button to submit complaint
if st.button("Submit Complaint"):
    if not complaint:
        st.error("Please enter a complaint.")
    else:
        try:
            # Categorize the complaint using Gemini AI
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Prepare the prompt to categorize complaint and analyze sentiment
            prompt = f"Please categorize the following complaint into appropriate departments like 'Technical Issue', 'HR', 'Managerial', etc. Also analyze the sentiment and urgency of the complaint:\n{complaint}"
            
            # Generate response from Gemini AI
            response = model.generate_content(prompt)
            result = response.text.strip()
            
            # Split the result into category, sentiment, and urgency (simple parsing)
            category = result.split("\n")[0].strip() if "category" in result.lower() else "Uncategorized"
            sentiment = result.split("\n")[1].strip() if "sentiment" in result.lower() else "Neutral"
            urgency = result.split("\n")[2].strip() if "urgency" in result.lower() else "Medium"
            
            # If user did not select a category, show the AI-generated one
            if selected_category == "Select category":
                selected_category = category

            # Store the complaint in the database
            store_complaint(complaint, selected_category, sentiment, selected_urgency)

            # Display the result
            st.write(f"Complaint Submitted: \n{complaint}")
            st.write(f"Categorization Result: {selected_category}")
            st.write(f"Sentiment: {sentiment}")
            st.write(f"Urgency: {urgency}")

        except Exception as e:
            st.error(f"Error: {e}")

# Show complaint history
st.subheader("Complaint History")
history = get_complaint_history()

# Display the history in a table
if history:
    st.write("Recent Complaints:")
    for entry in history:
        st.write(f"Complaint ID: {entry[0]}, Date: {entry[5]}")
        st.write(f"Complaint: {entry[1]}")
        st.write(f"Category: {entry[2]}")
        st.write(f"Sentiment: {entry[3]}")
        st.write(f"Urgency: {entry[4]}")
        st.write("-" * 50)

