import tkinter as tk
from tkinter import messagebox, filedialog
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode
import os
import datetime
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Ensure necessary directories exist
if not os.path.exists("qr_codes"):
    os.makedirs("qr_codes")
if not os.path.exists("data"):
    os.makedirs("data")
if not os.path.exists("patient_reports"):
    os.makedirs("patient_reports")

# --- Main Tkinter GUI setup ---
root = tk.Tk()
root.title("Patient Management System with QR Code")
root.geometry("800x700")

# Input labels and entries
tk.Label(root, text="Name:", font=("Arial", 12)).pack(pady=5)
entry_name = tk.Entry(root, width=50, font=("Arial", 12))
entry_name.pack(pady=2)

tk.Label(root, text="Age:", font=("Arial", 12)).pack(pady=5)
entry_age = tk.Entry(root, width=50, font=("Arial", 12))
entry_age.pack(pady=2)

tk.Label(root, text="Mobile:", font=("Arial", 12)).pack(pady=5)
entry_mobile = tk.Entry(root, width=50, font=("Arial", 12))
entry_mobile.pack(pady=2)

tk.Label(root, text="Symptoms:", font=("Arial", 12)).pack(pady=5)
entry_symptoms = tk.Entry(root, width=50, font=("Arial", 12))
entry_symptoms.pack(pady=2)

tk.Label(root, text="Diagnosis:", font=("Arial", 12)).pack(pady=5)
entry_diagnosis = tk.Entry(root, width=50, font=("Arial", 12))
entry_diagnosis.pack(pady=2)

tk.Label(root, text="Prescription:", font=("Arial", 12)).pack(pady=5)
entry_prescription = tk.Entry(root, width=50, font=("Arial", 12))
entry_prescription.pack(pady=2)

# --- Core Functions ---

def create_patient_pdf(patient_info, qr_code_path):
    """Creates a PDF report with patient info and QR code."""
    pdf_path = os.path.join("patient_reports", f"{patient_info['id']}.pdf")
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Patient Report")
    
    # Add QR code image to the PDF
    c.drawImage(qr_code_path, 450, 650, width=100, height=100)
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, f"Patient ID: {patient_info['id']}")
    c.drawString(100, 700, f"Name: {patient_info['name']}")
    c.drawString(100, 680, f"Age: {patient_info['age']}")
    c.drawString(100, 660, f"Mobile: {patient_info['mobile']}")
    c.drawString(100, 640, f"Symptoms: {patient_info['symptoms']}")
    c.drawString(100, 620, f"Diagnosis: {patient_info['diagnosis']}")
    c.drawString(100, 600, f"Prescription: {patient_info['prescription']}")
    
    c.save()
    messagebox.showinfo("Success", f"Report saved as {pdf_path}")

def save_patient_data():
    """Saves patient data, creates QR code and a PDF report."""
    try:
        patient_name = entry_name.get()
        if not patient_name:
            messagebox.showerror("Error", "Name field cannot be empty.")
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        patient_id = f"{patient_name.replace(' ', '_').lower()}_{timestamp}"

        patient_info = {
            "id": patient_id,
            "name": patient_name,
            "age": entry_age.get(),
            "mobile": entry_mobile.get(),
            "symptoms": entry_symptoms.get(),
            "diagnosis": entry_diagnosis.get(),
            "prescription": entry_prescription.get()
        }

        # 1. Create and save QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(patient_id)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        qr_image_path = os.path.join("qr_codes", f"{patient_id}.png")
        qr_img.save(qr_image_path)
        
        # 2. Save data to a JSON file
        data_file_path = os.path.join("data", f"{patient_id}.json")
        with open(data_file_path, 'w') as f:
            json.dump(patient_info, f, indent=4)
        
        # 3. Create PDF report
        create_patient_pdf(patient_info, qr_image_path)
        
        # 4. Clear entry fields
        entry_name.delete(0, tk.END)
        entry_age.delete(0, tk.END)
        entry_mobile.delete(0, tk.END)
        entry_symptoms.delete(0, tk.END)
        entry_diagnosis.delete(0, tk.END)
        entry_prescription.delete(0, tk.END)
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def show_patient_details(patient_id):
    """Loads and displays patient data from a JSON file."""
    data_file_path = os.path.join("data", f"{patient_id}.json")
    
    if not os.path.exists(data_file_path):
        messagebox.showerror("Error", f"No data found for ID: {patient_id}")
        return

    try:
        with open(data_file_path, 'r') as f:
            patient_info = json.load(f)
            
        details_window = tk.Toplevel(root)
        details_window.title("Patient Details")
        
        details_text = (
            f"ID: {patient_info.get('id', 'N/A')}\n"
            f"Name: {patient_info.get('name', 'N/A')}\n"
            f"Age: {patient_info.get('age', 'N/A')}\n"
            f"Mobile: {patient_info.get('mobile', 'N/A')}\n"
            f"Symptoms: {patient_info.get('symptoms', 'N/A')}\n"
            f"Diagnosis: {patient_info.get('diagnosis', 'N/A')}\n"
            f"Prescription: {patient_info.get('prescription', 'N/A')}"
        )

        details_label = tk.Label(details_window, text=details_text, font=("Arial", 12), justify=tk.LEFT)
        details_label.pack(padx=20, pady=20)
        
    except Exception as e:
        messagebox.showerror("Error", f"Could not load patient data: {e}")

def scan_qr_code():
    """Scans a QR code image and displays patient details."""
    file_path = filedialog.askopenfilename(
        title="Select QR Code Image",
        filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")]
    )
    
    if not file_path:
        return

    try:
        img = Image.open(file_path)
        decoded_objects = decode(img)
        
        if decoded_objects:
            patient_id = decoded_objects[0].data.decode('utf-8')
            show_patient_details(patient_id)
        else:
            messagebox.showerror("Error", "No QR code found in the image.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# --- GUI Buttons ---
save_button = tk.Button(root, text="Save Patient Data", command=save_patient_data, font=("Arial", 12))
save_button.pack(pady=10)

scan_qr_button = tk.Button(root, text="Scan QR Code", command=scan_qr_code, font=("Arial", 12))
scan_qr_button.pack(pady=10)

root.mainloop()
