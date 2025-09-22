import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image as KivyImage
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.gridlayout import GridLayout
import qrcode
from PIL import Image as PilImage
from pyzbar.pyzbar import decode
import os
import datetime
import json

# Set the window size for desktop testing (Optional)
Window.size = (400, 700)

# --- Ensure necessary directories exist ---
if not os.path.exists("qr_codes"):
    os.makedirs("qr_codes")
if not os.path.exists("data"):
    os.makedirs("data")

# --- Core Functions ---

def create_qr_code_and_save_data(patient_info):
    """
    Creates QR code and saves patient data to a JSON file.
    Returns the path to the saved QR code image.
    """
    patient_id = patient_info['id']
    
    # Create QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(patient_id)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_image_path = os.path.join("qr_codes", f"{patient_id}.png")
    qr_img.save(qr_image_path)
    
    # Save data to JSON file
    data_file_path = os.path.join("data", f"{patient_id}.json")
    with open(data_file_path, 'w') as f:
        json.dump(patient_info, f, indent=4)
        
    return qr_image_path

def load_patient_details(patient_id):
    """
    Loads patient data from a JSON file.
    """
    data_file_path = os.path.join("data", f"{patient_id}.json")
    if not os.path.exists(data_file_path):
        return None
    
    with open(data_file_path, 'r') as f:
        return json.load(f)

# --- Kivy App Class ---
class PatientApp(App):
    def build(self):
        # Main Layout
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Input fields
        self.entry_name = TextInput(hint_text="Name", multiline=False)
        self.entry_age = TextInput(hint_text="Age", multiline=False)
        self.entry_mobile = TextInput(hint_text="Mobile", multiline=False)
        self.entry_symptoms = TextInput(hint_text="Symptoms")
        self.entry_diagnosis = TextInput(hint_text="Diagnosis")
        self.entry_prescription = TextInput(hint_text="Prescription")
        
        self.main_layout.add_widget(self.entry_name)
        self.main_layout.add_widget(self.entry_age)
        self.main_layout.add_widget(self.entry_mobile)
        self.main_layout.add_widget(self.entry_symptoms)
        self.main_layout.add_widget(self.entry_diagnosis)
        self.main_layout.add_widget(self.entry_prescription)
        
        # Buttons
        self.save_button = Button(text="Save Patient Data", size_hint=(1, 0.1))
        self.save_button.bind(on_press=self.save_data_button_press)
        
        self.scan_button = Button(text="Scan QR Code", size_hint=(1, 0.1))
        self.scan_button.bind(on_press=self.scan_qr_button_press)
        
        self.main_layout.add_widget(self.save_button)
        self.main_layout.add_widget(self.scan_button)
        
        return self.main_layout

    def save_data_button_press(self, instance):
        """Called when Save button is pressed."""
        patient_name = self.entry_name.text
        if not patient_name:
            self.show_popup("Error", "Name field cannot be empty.")
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        patient_id = f"{patient_name.replace(' ', '_').lower()}_{timestamp}"
        
        patient_info = {
            "id": patient_id,
            "name": patient_name,
            "age": self.entry_age.text,
            "mobile": self.entry_mobile.text,
            "symptoms": self.entry_symptoms.text,
            "diagnosis": self.entry_diagnosis.text,
            "prescription": self.entry_prescription.text
        }
        
        qr_image_path = create_qr_code_and_save_data(patient_info)
        self.show_popup("Success", f"Data and QR code saved successfully.")
        
        # Display the generated QR code
        self.show_qr_code_popup(qr_image_path)
        
        # Clear fields
        self.entry_name.text = ""
        self.entry_age.text = ""
        self.entry_mobile.text = ""
        self.entry_symptoms.text = ""
        self.entry_diagnosis.text = ""
        self.entry_prescription.text = ""

    def scan_qr_button_press(self, instance):
        """Called when Scan button is pressed. Opens a file chooser popup."""
        self.filechooser_popup = Popup(title="Select QR Code Image", size_hint=(0.9, 0.9))
        content = BoxLayout(orientation='vertical')
        
        filechooser = FileChooserIconView(filters=['*.png', '*.jpg', '*.jpeg'])
        content.add_widget(filechooser)
        
        select_button = Button(text="Select", size_hint=(1, 0.1))
        select_button.bind(on_press=lambda btn: self.scan_selected_file(filechooser.selection))
        content.add_widget(select_button)
        
        self.filechooser_popup.content = content
        self.filechooser_popup.open()

    def scan_selected_file(self, selection):
        """Scans the selected QR code image."""
        if not selection:
            self.show_popup("Error", "No file selected.")
            return
            
        self.filechooser_popup.dismiss()
        
        file_path = selection[0]
        try:
            pil_image = PilImage.open(file_path)
            decoded_objects = decode(pil_image)
            
            if decoded_objects:
                patient_id = decoded_objects[0].data.decode('utf-8')
                self.show_patient_details(patient_id)
            else:
                self.show_popup("Error", "No QR code found in the image.")
        except Exception as e:
            self.show_popup("Error", f"Failed to scan QR code: {e}")

    def show_patient_details(self, patient_id):
        """Shows patient details in a popup."""
        patient_info = load_patient_details(patient_id)
        if not patient_info:
            self.show_popup("Error", f"Patient data for {patient_id} not found.")
            return
        
        details_text = (
            f"ID: {patient_info.get('id', 'N/A')}\n"
            f"Name: {patient_info.get('name', 'N/A')}\n"
            f"Age: {patient_info.get('age', 'N/A')}\n"
            f"Mobile: {patient_info.get('mobile', 'N/A')}\n"
            f"Symptoms: {patient_info.get('symptoms', 'N/A')}\n"
            f"Diagnosis: {patient_info.get('diagnosis', 'N/A')}\n"
            f"Prescription: {patient_info.get('prescription', 'N/A')}"
        )

        self.show_popup("Patient Details", details_text)

    def show_popup(self, title, message):
        """A generic function to show a popup message."""
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

    def show_qr_code_popup(self, qr_image_path):
        """Shows the generated QR code image in a popup."""
        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        qr_image = KivyImage(source=qr_image_path)
        popup_content.add_widget(qr_image)
        
        # Add a close button
        close_button = Button(text="Close", size_hint=(1, 0.2))
        popup_content.add_widget(close_button)
        
        qr_popup = Popup(title="Generated QR Code", content=popup_content, size_hint=(0.8, 0.8))
        close_button.bind(on_press=qr_popup.dismiss)
        
        qr_popup.open()

if __name__ == '__main__':
    PatientApp().run()
