import PyPDF2
import xml.etree.ElementTree as ET

# Function to extract form data from the PDF
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

# Paths
pdf_path = "./PAT Family Review Tool 2024.pdf"  # Path to your PDF
xml_output_path = "./output_form_data.xml"      # Output XML file

# Process
form_data = extract_form_data(pdf_path)
if form_data:
    form_data_to_xml(form_data, xml_output_path)
else:
    print("No form data found.")