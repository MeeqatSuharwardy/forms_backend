import os
from flask import Flask, render_template, request, send_from_directory, jsonify, redirect, url_for, send_file
import pdfkit
from flask import current_app
from PIL import Image
import base64
import io
from datetime import datetime
from selenium import webdriver
import img2pdf
from io import BytesIO
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS, cross_origin
from flask import send_from_directory

app = Flask(__name__)
cors = CORS(app)

with app.app_context():
    # Now you are inside the application context
    pdf_folder = os.path.join(current_app.root_path, 'application_for_employment')
    pdf_folder_2 = os.path.join(current_app.root_path, 'emergency_contacts_final')
    pdf_folder_3 = os.path.join(current_app.root_path, 'anti_harassment_discrimination_final')
    pdf_folder_4 = os.path.join(current_app.root_path, 'submit_employment_payroll')
    pdf_folder_5 = os.path.join(current_app.root_path, 'receipt_of_company_property')
    pdf_folder_6 = os.path.join(current_app.root_path, 'hippa_agreement')
    os.makedirs(pdf_folder, exist_ok=True)
    os.makedirs(pdf_folder_2, exist_ok=True)
    os.makedirs(pdf_folder_3, exist_ok=True)
    os.makedirs(pdf_folder_4, exist_ok=True)
    os.makedirs(pdf_folder_5, exist_ok=True)
    os.makedirs(pdf_folder_6, exist_ok=True)

@app.route('/')
@cross_origin()
def index():
    return 'Welcome to the PDF Generator App!'


@app.route('/application_for_employment')
@cross_origin()
def application_for_employment_form():
    return render_template('Application_for_employment.html')

@app.route('/emergency_contacts_final')
@cross_origin()
def emergency_contacts_form():
    return render_template('emergency_contacts_final.html')

@app.route('/anti_harassment_discrimination_final')
@cross_origin()
def anti_harassment_discrimination_final_form():
    return render_template('anti_harassment_discrimination_final.html')

@app.route('/submit_employment_payroll')
@cross_origin()
def submit_employment_payroll_form():
    return render_template('employee_payroll_information.html')

@app.route('/receipt_of_company_property')
@cross_origin()
def receipt_of_company_property_form():
    return render_template('receipt_of_company_property.html')

@app.route('/hippa_agreement')
@cross_origin()
def hippa_agreement():
    return render_template('hippa_agreement.html')


@app.route('/submit-emergency-contact-form', methods=['POST'])
@cross_origin()
def submit_emergency_contact_form():
    form_data = request.form.to_dict(flat=False)
    name_in_form = form_data.get('employeeName', ['Unknown_Name'])[0].replace(' ', '_')
    filename = f"Emergency_Contacts_{name_in_form}.pdf"
    template_name = 'pdf_emergency_contacts_final.html'

    # Prepare the path for signatures and create unique file name
    signatures_path = os.path.join(current_app.root_path, 'static', 'signatures')
    os.makedirs(signatures_path, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    signature_filename = f'signature_{name_in_form}_{timestamp}.png'
    signature_full_path = os.path.join(signatures_path, signature_filename)

    signature_data = form_data.get('signatureImageData', [''])[0]
    if signature_data:
        signature_image_data = signature_data.split(",")[1]
        image_data = base64.b64decode(signature_image_data)
        with open(signature_full_path, 'wb') as f:
            f.write(image_data)
        signature_web_path = url_for('static', filename=f'signatures/{signature_filename}')
        signature_fs_path = os.path.join(current_app.root_path, 'static', 'signatures', signature_filename)

    else:
        signature_web_path = None

    # Prepare the context with all necessary data
    print(signature_web_path)
    context = {
        'employee_name': form_data.get('employeeName', [''])[0],
        'phone_number': form_data.get('phoneNumber', [''])[0],
        'address': form_data.get('address', [''])[0],
        'primary_name': form_data.get('primaryName', [''])[0],
        'primary_relationship': form_data.get('primaryRelationship', [''])[0],
        'primary_phone': form_data.get('primaryPhone', [''])[0],
        'primary_alt_phone': form_data.get('primaryAltPhone', [''])[0],
        'secondary_name': form_data.get('secondaryName', [''])[0],
        'secondary_relationship': form_data.get('secondaryRelationship', [''])[0],
        'secondary_phone': form_data.get('secondaryPhone', [''])[0],
        'secondary_alt_phone': form_data.get('secondaryAltPhone', [''])[0],
        'doctor_name': form_data.get('doctorName', [''])[0],
        'doctor_phone': form_data.get('doctorPhone', [''])[0],
        'doctor_address': form_data.get('doctorAddress', [''])[0],
        'date_signed': form_data.get('dateSigned', [''])[0],
        'signature_image_path': signature_fs_path,
    }

    logo_path = os.path.join(current_app.root_path, 'static', 'assets', 'Psychiatry_logo.jpg')
    form_data['logo_path'] = logo_path
    pdf_path = os.path.join(pdf_folder_2, filename)
    html_content = render_template(template_name, **context)
    options = {
        'quiet': '',
        'load-error-handling': 'ignore',
        'enable-local-file-access': ''

    }
    pdfkit.from_string(html_content, pdf_path, options=options)
    return jsonify({"success": True, "message": "Form successfully submitted and PDF generated.",
                    "pdf_url": url_for('static', filename=f'pdfs/{filename}')})


@app.route('/submit-employment-form', methods=['POST'])
@cross_origin()
def submit_employment_form():
    form_data = request.form.to_dict(flat=False)  # Use flat=False to keep multiple values for the same key in lists
    form_type = form_data.get('form_type', ['unknown_form'])[0]  # Get the first item if list exists

    hours_available = form_data.get('hours', [])
    days_available = form_data.get('days', [])
    authorized = form_data.get('authorized', ['No'])[0]

    if form_type == 'employment_application':
        name_in_form = form_data.get('name', ['Unknown_Name'])[0].replace(' ', '_')
        filename = f"Application_for_Employment_{name_in_form}.pdf"
        template_name = 'pdf_Application_for_employment.html'

        form_data['hours_available'] = ", ".join(hours_available)
        form_data['days_available'] = ", ".join(days_available)
        form_data['authorized'] = authorized
        # Handling qualifications as list of dictionaries
        qualifications = [{'school_name': name, 'degree': deg}
                          for name, deg in zip(form_data.get('school_name[]', []), form_data.get('degree[]', []))]
        form_data['qualifications'] = qualifications

        work_history = [
            {
                'job_title': title,
                'start_date': start,
                'end_date': end,
                'company_name': company,
                'supervisor_name': supervisor,
                'phone_number': phone,
                'city': city,
                'state': state,
                'zip': zip_code,
                'duties': duties,
                'reason_for_leaving': reason,
                'starting_salary': start_salary,
                'ending_salary': end_salary
            }
            for
            title, start, end, company, supervisor, phone, city, state, zip_code, duties, reason, start_salary, end_salary
            in zip(
                form_data.get('job_titles[]', []),
                form_data.get('start_dates[]', []),
                form_data.get('end_dates[]', []),
                form_data.get('company_names[]', []),
                form_data.get('supervisor_names[]', []),
                form_data.get('phone_numbers[]', []),
                form_data.get('cities[]', []),
                form_data.get('states[]', []),
                form_data.get('zips[]', []),
                form_data.get('duties[]', []),
                form_data.get('reasons_for_leaving[]', []),
                form_data.get('starting_salaries[]', []),
                form_data.get('ending_salaries[]', [])
            )
        ]

        form_data['work_history'] = work_history

        references = [{
            'name': name,
            'phone': phone,
            'relationship': relationship
        } for name, phone, relationship in zip(
            form_data.get('reference_name[]', []),
            form_data.get('reference_phone[]', []),
            form_data.get('reference_relationship[]', [])
        )]
        form_data['references'] = references

    else:
        return "Unknown form type", 400

    pdf_path = os.path.join(pdf_folder, filename)

    # Absolute path for the logo
    logo_path = os.path.join(current_app.root_path, 'static', 'assets', 'Psychiatry_logo.jpg')
    form_data['logo_path'] = logo_path

    # Render the correct template
    html_content = render_template(template_name, **form_data)

    # Configure pdfkit options
    options = {
        'quiet': '',
        'load-error-handling': 'ignore',
        'enable-local-file-access':'',
        # Add more options as needed
    }

    # Generate PDF
    pdfkit.from_string(html_content, pdf_path, options=options)

    # Send the PDF file directly as an attachment
    return jsonify({"success": True, "message": "Form successfully submitted and PDF generated.",
                    "pdf_url": url_for('static', filename=f'pdfs/{filename}')})


@app.route('/anti_harassment_discrimination_final', methods=['POST'])
@cross_origin()
def anti_harassment_discrimination_final():
    form_data = request.form.to_dict(flat=False)
    name_in_form = form_data.get('printedName', ['Unknown_Name'])[0].replace(' ', '_')
    filename = f"anti_harassment_discrimination_final_{name_in_form}.pdf"
    template_name = 'pdf_anti_harassment_discrimination_final.html'
    logo_path = os.path.join(current_app.root_path, 'static', 'assets', 'Psychiatry_logo.jpg')
    form_data['logo_path'] = logo_path

    signatures_path = os.path.join(current_app.root_path, 'static', 'signatures')
    os.makedirs(signatures_path, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    signature_filename = f'signature_{name_in_form}_{timestamp}.png'
    signature_full_path = os.path.join(signatures_path, signature_filename)

    signature_data = form_data.get('signatureImageData', [''])[0]
    if signature_data:
        signature_image_data = signature_data.split(",")[1]
        image_data = base64.b64decode(signature_image_data)
        with open(signature_full_path, 'wb') as f:
            f.write(image_data)
        signature_fs_path = os.path.join(current_app.root_path, 'static', 'signatures', signature_filename)
    else:
        signature_fs_path = None

    context = {
        'printedName': form_data.get('printedName', ''),
        'date_signed': form_data.get('date', [''])[0],
        'signature_image_path': signature_fs_path if signature_data else None,
    }


    pdf_path = os.path.join(pdf_folder_3, filename)
    html_content = render_template(template_name, **context)
    options = {
        'quiet': '',
        'load-error-handling': 'ignore',
        'enable-local-file-access': ''
    }
    pdfkit.from_string(html_content, pdf_path, options=options)
    return jsonify({"success": True, "message": "Form successfully submitted and PDF generated.",
                    "pdf_url": url_for('static', filename=f'pdfs/{filename}')})


@app.route('/submit_employment_payroll', methods=['POST'])
@cross_origin()
def submit_employment_payroll():
    form_data = request.form.to_dict(flat=False)
    print(form_data)
    name_in_form = form_data.get('employeeName', ['Unknown_Name'])[0].replace(' ', '_')
    filename = f"Employee_Payroll_Information_{name_in_form}.pdf"
    template_name = 'pdf_employee_payroll_information.html'

    # Prepare the path for signatures and create a unique file name
    signatures_path = os.path.join(current_app.root_path, 'static', 'signatures')
    os.makedirs(signatures_path, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    signature_filename = f'signature_{name_in_form}_{timestamp}.png'
    signature_full_path = os.path.join(signatures_path, signature_filename)

    signature_data = form_data.get('signature', [''])[0]
    if signature_data:
        signature_image_data = signature_data.split(",")[1]
        image_data = base64.b64decode(signature_image_data)
        with open(signature_full_path, 'wb') as f:
            f.write(image_data)
        signature_fs_path = os.path.join(current_app.root_path, 'static', 'signatures', signature_filename)
    else:
        signature_fs_path = None

    # Prepare the context with all necessary data
    context = {
        'employee_name': form_data.get('employeeName', [''])[0],
        'date_of_hire': form_data.get('dateOfHire', [''])[0],
        'original_position': form_data.get('originalPosition', [''])[0],
        'change_position_date': form_data.get('changePositionDate', [''])[0],
        'pay_type': form_data.get('payType', [''])[0],
        'pay_frequency': form_data.get('payFrequency', [''])[0],
        'hire_pay_rate': form_data.get('hirePayRate', [''])[0],
        'effective_date': form_data.get('effectiveDate', [''])[0],
        'approval_date': form_data.get('approvalDate', [''])[0],
        'date_signed': form_data.get('dateSigned', [''])[0],
        'signature_image_path': signature_fs_path,
    }

    logo_path = os.path.join(current_app.root_path, 'static', 'assets', 'Psychiatry_logo.jpg')
    context['logo_path'] = logo_path
    pdf_path = os.path.join(pdf_folder_4, filename)
    html_content = render_template(template_name, **context)
    options = {
        'quiet': '',
        'load-error-handling': 'ignore',
        'enable-local-file-access': ''
    }
    pdfkit.from_string(html_content, pdf_path, options=options)
    return jsonify({"success": True, "message": "Form successfully submitted and PDF generated.",
                    "pdf_url": url_for('static', filename=f'pdfs/{filename}')})


@app.route('/receipt_of_company_property', methods=['POST'])
@cross_origin()
def receipt_of_company_property():
    form_data = request.form.to_dict()
    name_in_form = form_data.get('name', 'Unknown_Name').replace(' ', '_')
    filename = f"Receipt_of_Property_{name_in_form}.pdf"
    template_name = 'pdf_receipt_of_company_property.html'

    # Convert Base64 signature data to images and save
    signatures_path = os.path.join(current_app.root_path, 'static', 'signatures')
    os.makedirs(signatures_path, exist_ok=True)
    employee_signature_data = form_data.get('employeeSignatureData').split(",")[1]
    manager_signature_data = form_data.get('managerSignatureData').split(",")[1]

    employee_signature_path = save_signature(employee_signature_data, 'employee', name_in_form, signatures_path)
    manager_signature_path = save_signature(manager_signature_data, 'manager', name_in_form, signatures_path)

    # Prepare the context for PDF rendering
    context = {
        'logo_path': os.path.join(current_app.root_path, 'static', 'assets', 'Psychiatry_logo.jpg'),
        'employee_name': form_data['name'],
        'current_date': form_data['date'],
        'equipment_description': form_data['description'],
        'employee_signature_placeholder': employee_signature_path,
        'manager_signature_placeholder': manager_signature_path,
        'employee_signed_date': form_data['employeeDate'],
        'manager_signed_date': form_data['managerDate'],
        'current_year': datetime.now().year
    }

    # Render HTML content
    html_content = render_template(template_name, **context)
    pdf_path = os.path.join(pdf_folder_5, filename)
    options = {
        'quiet': '',
        'load-error-handling': 'ignore',
        'enable-local-file-access': True
    }
    pdfkit.from_string(html_content, pdf_path, options=options)
    return jsonify({"success": True, "message": "Form successfully submitted and PDF generated.",
                    "pdf_url": url_for('static', filename=f'pdfs/{filename}')})


def save_signature(data, role, name, path):

    """Saves a base64-encoded image as a PNG file and returns the file path."""
    image_data = base64.b64decode(data)
    img = Image.open(BytesIO(image_data))

    # Check if the image has an 'alpha' channel; if so, convert it properly
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
        img = background

    signature_file_path = os.path.join(path, f"{role}_signature_{name}.png")
    img.save(signature_file_path, 'PNG')
    return signature_file_path


@app.route('/submit_confidentiality_agreement', methods=['POST'])
@cross_origin()
def submit_confidentiality_agreement():
    form_data = request.form
    employee_name = form_data.get('employeeName', 'Unknown_Name').replace(' ', '_')
    agreement_date = form_data.get('agreementDate', '')
    agreement_month = form_data.get('agreementMonth', '')
    agreement_year = form_data.get('agreementYear', '')
    filename = f"confidentiality_agreement_{employee_name}.pdf"
    template_name = 'pdf_hippa_agreement.html'

    signatures_path = os.path.join(app.root_path, 'static', 'signatures')
    os.makedirs(signatures_path, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    signature_filename = f'signature_{employee_name}_{timestamp}.png'
    signature_full_path = os.path.join(signatures_path, signature_filename)

    signature_data = form_data.get('signatureImageData')
    if signature_data:
        signature_image_data = signature_data.split(",")[1]
        image_data = base64.b64decode(signature_image_data)
        with open(signature_full_path, 'wb') as f:
            f.write(image_data)

    context = {
        'employeeName': employee_name,
        'agreementDate': agreement_date,
        'agreementMonth': agreement_month,
        'agreementYear': agreement_year,
        'signature_image_path': signature_full_path
    }

    pdf_folder = os.path.join(app.root_path, 'static', 'pdfs')
    os.makedirs(pdf_folder, exist_ok=True)
    pdf_path = os.path.join(pdf_folder, filename)
    html_content = render_template(template_name, **context)
    options = {
        'quiet': '',
        'load-error-handling': 'ignore',
        'enable-local-file-access': ''
    }
    pdfkit.from_string(html_content, pdf_path, options=options)
    return jsonify({
        "success": True,
        "message": "Form successfully submitted and PDF generated.",
        "pdf_url": url_for('static', filename=f'pdfs/{filename}')
    })

@app.route('/list-pdfs')
@cross_origin()
def list_pdfs():
    directories = {
        'ApplicationForEmployment': os.path.join(current_app.root_path, 'application_for_employment'),
        'EmergencyContacts': os.path.join(current_app.root_path, 'emergency_contacts_final'),
        'AntiHarassmentDiscrimination': os.path.join(current_app.root_path, 'anti_harassment_discrimination_final'),
        'EmploymentPayroll': os.path.join(current_app.root_path, 'submit_employment_payroll'),
        'ReceiptOfProperty': os.path.join(current_app.root_path, 'receipt_of_company_property')
    }

    all_pdfs = []
    errors = []

    for key, folder in directories.items():
        try:
            # Ensure the directory exists and can be accessed
            os.makedirs(folder, exist_ok=True)
            files = os.listdir(folder)
            pdf_files = [f for f in files if f.endswith('.pdf')]
            if pdf_files:
                all_pdfs.append({
                    "category": key,
                    "files": pdf_files
                })
        except FileNotFoundError:
            errors.append(f"{key}: Directory not found")
        except Exception as e:
            errors.append(f"{key}: {str(e)}")

    if errors:
        return jsonify({'errors': errors}), 404
    return jsonify({'categories': all_pdfs})

# Dictionary to map category to directory path
DIRECTORY_MAP = {
    'ApplicationForEmployment': 'application_for_employment',
    'EmergencyContacts': 'emergency_contacts_final',
    'AntiHarassmentDiscrimination': 'anti_harassment_discrimination_final',
    'EmploymentPayroll': 'submit_employment_payroll',
    'ReceiptOfProperty': 'receipt_of_company_property'
}

@app.route('/pdfs/<category>/<filename>')
@cross_origin()
def serve_pdf(category, filename):
    download = request.args.get('download', default='no', type=str)
    directory = DIRECTORY_MAP.get(category)
    if directory:
        full_path = os.path.join(current_app.root_path, directory)
        try:
            if download == 'yes':
                # Send the file with Content-Disposition: attachment which forces a download
                return send_from_directory(full_path, filename, as_attachment=True)
            else:
                # Serve the file to be opened in the browser
                return send_from_directory(full_path, filename)
        except FileNotFoundError:
            return jsonify({'error': 'File not found'}), 404
    else:
        return jsonify({'error': 'Invalid category'}), 400

@app.route('/delete-pdf/<category>/<filename>', methods=['DELETE'])
@cross_origin()
def delete_pdf(category, filename):
    directory = DIRECTORY_MAP.get(category)
    if directory:
        try:
            file_path = os.path.join(current_app.root_path, directory, filename)
            os.remove(file_path)  # Remove the file
            return jsonify({'message': 'File deleted successfully'}), 200
        except FileNotFoundError:
            return jsonify({'error': 'File not found'}), 404
        except Exception as e:
            return jsonify({'error': 'An error occurred', 'details': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid category'}), 400
if __name__ == '__main__':
    app.run(debug=True)
