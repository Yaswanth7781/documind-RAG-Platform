import os
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Project Source Code', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Directories and files to exclude
    exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'env', 'dist', 'build', 'data'}
    exclude_exts = {'.pdf', '.jpg', '.png', '.jpeg', '.gif', '.svg', '.sqlite3', '.pyc', '.zip', '.tar', '.gz', '.ico', '.woff', '.woff2', '.ttf'}

    project_dir = '.'
    
    for root, dirs, files in os.walk(project_dir):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in exclude_exts:
                continue
                
            filepath = os.path.join(root, file)
            
            # Skip this script itself and the output pdf
            if file == 'generate_pdf.py' or file == 'Project_Source_Code.pdf':
                continue

            # Add file header
            pdf.set_font("Arial", 'B', 12)
            pdf.ln(5)
            pdf.cell(0, 10, f"File: {filepath}", 0, 1)
            pdf.set_font("Courier", size=8)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Ensure we handle tabs appropriately
                content = content.replace('\t', '    ')
                # Replace unsupported characters for fpdf's standard latin-1 font
                content = content.encode('latin-1', 'replace').decode('latin-1')
                
                pdf.multi_cell(0, 4, content)
            except Exception as e:
                pdf.multi_cell(0, 4, f"<Error reading file: {e}>")

    pdf.output("Project_Source_Code.pdf")
    print("PDF generated successfully: Project_Source_Code.pdf")

if __name__ == "__main__":
    generate_pdf()
