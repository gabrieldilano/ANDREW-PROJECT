import tkinter as tk
from tkinter import filedialog, messagebox

import PyPDF2
import xml.etree.ElementTree as ET

import os

def browse_files():
    """Open file explorer to add more files."""
    file_paths = filedialog.askopenfilenames(
        title="Select Files",
        filetypes=(("PDF Files", "*.pdf"), ("All Files", "*.*"))
    )
    if file_paths:
        for file_path in file_paths:
            if file_path not in input_files:  # Avoid duplicates
                input_files.append(file_path)
        update_file_list_display()

def delete_file():
    """Delete the selected file from the input file list."""
    selected_items = listbox_files.curselection()
    if not selected_items:
        messagebox.showwarning("No Selection", "Please select a file to delete.")
        return
    for index in reversed(selected_items):  # Remove in reverse order to avoid index issues
        input_files.pop(index)
    update_file_list_display()

def select_output_folder():
    """Open file explorer to select an output folder."""
    folder_path = filedialog.askdirectory(title="Select Output Folder")
    if folder_path:
        global output_folder
        output_folder = folder_path
        label_output_folder.config(text=f"Output Folder: {output_folder}")

def convert_files():
    """Save output files to the selected folder."""
    if not input_files:
        messagebox.showwarning("Input Required", "Please select at least one input file!")
        return
    if not output_folder:
        messagebox.showwarning("Output Folder Required", "Please select an output folder!")
        return

    try:
        for file_path in input_files:
            # Extract form data from each file
            form_data = extract_form_data(file_path)
            if form_data:
                # Generate output XML path
                xml_output_path = os.path.join(output_folder, os.path.basename(file_path).replace('.pdf', '.xml'))
                form_data_to_xml(form_data, xml_output_path)
                print(f"File converted: {xml_output_path}")
        messagebox.showinfo("Success", "All files have been processed!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


def update_file_list_display():
    """Update the listbox with the current list of input files."""
    listbox_files.delete(0, tk.END)  # Clear the listbox
    for file in input_files:
        listbox_files.insert(tk.END, os.path.basename(file))

def extract_form_data(pdf_path):
    form_data = {}
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        # Assumes form data is in annotations
        for page in reader.pages:
            if '/Annots' in page:
                for annot in page['/Annots']:
                    annot_obj = annot.get_object()
                    if '/T' in annot_obj and '/V' in annot_obj:
                        field_name = annot_obj['/T']
                        field_value = annot_obj['/V']
                        form_data[field_name] = field_value
    return form_data

# Function to convert form data to XML
def form_data_to_xml(form_data, output_path):
    root = ET.Element("FormData")
    for key, value in form_data.items():
        field = ET.SubElement(root, "Field", name=key)
        field.text = str(value)

    # Write the XML to a file
    tree = ET.ElementTree(root)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"XML file saved to {output_path}")

# Initialize the Tkinter window
root = tk.Tk()
root.title("PDF to XML")
root.geometry("600x500")

# Global variables for file paths and output folder
input_files = []
output_folder = ""

# Input file selection
frame_files = tk.Frame(root)
frame_files.pack(pady=10)

button_browse_files = tk.Button(frame_files, text="Add PDF Files", font=("Arial", 12), command=browse_files)
button_browse_files.grid(row=0, column=0, padx=5)

button_delete_file = tk.Button(frame_files, text="Delete File", font=("Arial", 12), command=delete_file)
button_delete_file.grid(row=0, column=1, padx=5)

listbox_files = tk.Listbox(root, font=("Arial", 10), height=10, selectmode=tk.MULTIPLE, width=80)
listbox_files.pack(pady=10)

# Output folder selection
button_output_folder = tk.Button(root, text="Select Output Folder", font=("Arial", 12), command=select_output_folder)
button_output_folder.pack(pady=10)

label_output_folder = tk.Label(root, text="No output folder selected", font=("Arial", 10), wraplength=480, justify="left")
label_output_folder.pack(pady=10)

# Save files button
button_convert_files = tk.Button(root, text="Convert", font=("Arial", 12), command=convert_files)
button_convert_files.pack(pady=20)

# Run the Tkinter event loop
root.mainloop()
