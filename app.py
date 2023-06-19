import streamlit as st
import PIL
import PIL.Image
from datetime import date
import os
import base64
import pandas_profiling
import streamlit.components.v1 as components
import pandas as pd
from fpdf import FPDF
from get_report import generateReport
from recgonise import get_result_for_single_image,get_result,append_to_patient_record_csv

df=pd.read_csv('out_csv.csv')
patient_id=list(df['PatientID'])





def predict():
    st.title("Diabetic Retinopathy Report Tool")
    st.write("Please provide the necessary information and upload an image.")

    # Add user input fields
    id = st.text_input("ID")
    sex = st.selectbox("Sex", ["Male", "Female"])
    age = st.slider("Age", 1, 100)
    selected_date = st.date_input("Select a date", date.today())
    eye_part = st.selectbox("Eye Part",['Left Eye','Right Eye'])

    # Add image upload option
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    # Check if an image has been uploaded
    if uploaded_image is not None:
        # Read the uploaded image
        image = PIL.Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Generate a random filename
        filename = id + ".png"

        # Save the image to the "imagedatabase" directory
        image.save(os.path.join("image Database", filename))
        st.write("Image saved successfully.")

        # Append the user input to the CSV file
        df=pd.read_csv('patient_record.csv')

        append_to_patient_record_csv( id, sex, selected_date, eye_part)
    if st.button("Predict"):
        get_result_for_single_image(id)
        response = generateReport(id)
        render_report(response)





def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download Report</a>'


def render_report(rep_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.multi_cell(300, 20, '            AI generated Diabetes Retinopathy Report', 0, 3)
    # pdf.multi_cell(300, 20, ' Hand X-ray Generated Report', 0,3, 'C')
    pdf.line(0, 30, pdf.w, 30)



    rep_image = rep_data.pop('image')
    pdf.image(rep_image, 150, 40, 50, type='png')
    for key, value in rep_data.items():
        text = key + '   :     ' + value
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(300, 15, text, 0, 1)

    base64_pdf = base64.b64encode(pdf.output(dest="S").encode("latin-1")).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

    html = create_download_link(pdf.output(dest="S").encode("latin-1"), "Report")
    st.markdown(html, unsafe_allow_html=True)



def report():
    st.header('Reports')
    st.write(' The Diabetes Retinopathy report generated by the AI Inference Engine can be viewed here and downloaded')
    rep_patientId = st.selectbox('Select Patient ID for generating the report',patient_id)

    if st.button('Get Report'):
        report = generateReport(rep_patientId)
        render_report(report)


def home():
    pass


def dashboard():
    st.title('Get Data Summary of all Images in Database')
    st.write('Generating a Batch summary and getting results of all images in database')
    runbatch=st.button("Run batch inference")
    if runbatch:
        get_result()
        data = pd.read_csv('out_csv.csv')  # Replace 'your_file.csv' with the path to your CSV file

        # Generate pandas profiling report
        report = pandas_profiling.ProfileReport(data, title='Data Visualisation Report')

        # Display the report in Streamlit
        st.title('Data Summary')
        print(report)
        components.html(report.to_html(), height=1000, width=800, scrolling=True)


def main():
    st.sidebar.image('template/nav.png')
    st.sidebar.write(' Welcome to AI Medical Imaging Application')
    opt = st.sidebar.selectbox("Go to page:",['Home','Prediction','Report','Dashboard'])
    st.image('template/main.png')
    st.title('AI  Medical Imaging Application   ')
    if opt=='Home':
        home()
    if opt=='Prediction':
        predict()
    if opt=='Report':
        report()
    if opt=='Dashboard':
        dashboard()




if __name__ == "__main__":
    main()

