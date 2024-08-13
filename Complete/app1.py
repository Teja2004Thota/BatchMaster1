import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Title of the Streamlit app
st.title("Student Group Assignment")

# File uploader to upload an Excel file
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

def generate_pdf(batches):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "Student Group Assignments")
    
    # Draw batch assignments
    y_position = height - 100
    c.setFont("Helvetica", 12)
    for i, batch in enumerate(batches):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, y_position, f"Batch {i + 1}:")
        y_position -= 20
        
        c.setFont("Helvetica", 12)
        for member in batch:
            role = member['Role']
            roll_no = member['Student']['Roll No']
            name = member['Student']['Student Full Name']
            c.drawString(120, y_position, f"{role}: {name} (Roll No: {roll_no})")
            y_position -= 20

        y_position -= 10  # Space between batches
        if y_position < 50:  # Check if we need to create a new page
            c.showPage()
            y_position = height - 50

    c.save()
    buffer.seek(0)
    return buffer

if uploaded_file:
    # Read the data into a DataFrame
    df = pd.read_excel(uploaded_file)
    
    # Data processing
    df['Backlogs'] = df['Backlogs'].fillna(0).astype(int)
    group_leads = df[df['Backlogs'] == 0].dropna(subset=['CGPA without backlogs'])
    group_leads = group_leads.sort_values(by='CGPA without backlogs', ascending=False).reset_index(drop=True)
    group_leads.index = group_leads.index + 1
    
    remaining_students = df[df['Backlogs'] > 0]
    remaining_students = remaining_students.sort_values(by=['CGPA without backlogs', 'Backlogs'], ascending=[False, False]).reset_index(drop=True)
    remaining_students.index = remaining_students.index + 1

    num_students = len(df)
    num_batches = num_students // 4
    batches = [[] for _ in range(num_batches)]
    
    # Assign group leaders
    for i, (index, leader) in enumerate(group_leads.head(num_batches).iterrows()):
        batches[i].append({'Student': leader, 'Role': 'Leader'})
    
    # Assign remaining students with backlogs
    for i, (index, student) in enumerate(remaining_students.head(num_batches).iterrows()):
        batch_index = i if i < num_batches else 2 * num_batches - 1 - i
        batches[batch_index].append({'Student': student, 'Role': 'Member'})
    
    # Assign remaining group leads
    group_leads_remaining = group_leads.iloc[num_batches:]
    for i, (index, student) in enumerate(group_leads_remaining.iterrows()):
        batch_index = (num_batches - 1 - i) if i < num_batches else i - num_batches
        batches[batch_index].append({'Student': student, 'Role': 'Member'})
    
    # Assign remaining students with backlogs
    remaining_students_rest = remaining_students.iloc[num_batches:]
    for i, (index, student) in enumerate(remaining_students_rest.iterrows()):
        batch_index = (num_batches - 1 - i) if i < num_batches else i - num_batches
        batches[batch_index].append({'Student': student, 'Role': 'Member'})
    
    # Generate PDF
    pdf_buffer = generate_pdf(batches)
    
    # Provide download link for PDF
    st.download_button(
        label="Download PDF",
        data=pdf_buffer,
        file_name="batch_assignments.pdf",
        mime="application/pdf"
    )

else:
    st.write("Upload an Excel file to get started.")
