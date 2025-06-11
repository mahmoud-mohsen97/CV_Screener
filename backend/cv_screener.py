"""
Core CV screening logic.
Handles PDF processing, image conversion, and result compilation.
"""

import os
import io
import zipfile
import magic
import pandas as pd
from PIL import Image
import base64
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class CVScreener:
    def __init__(self, role_data: Dict):
        """Initialize the CV screener with role data."""
        self.role_data = role_data
        self.results = []
        self.processed_count = 0
        self.total_count = 0
        self.current_status = "Initializing"

    async def process_zip(self, zip_file: bytes) -> str:
        """
        Process a ZIP file containing CVs.
        
        Args:
            zip_file: Bytes of the ZIP file
            
        Returns:
            Path to the generated Excel report
        """
        try:
            # Reset counters
            self.processed_count = 0
            self.results = []
            
            # Create temporary directory
            temp_dir = "temp"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extract and validate ZIP contents
            pdf_files = self._extract_zip(zip_file, temp_dir)
            self.total_count = len(pdf_files)
            
            # Process each PDF
            for pdf_path in pdf_files:
                try:
                    await self._process_single_cv(pdf_path)
                except Exception as e:
                    print(f"Error processing {pdf_path}: {str(e)}")
                    self.results.append({
                        "filename": os.path.basename(pdf_path),
                        "error": str(e)
                    })
                finally:
                    self.processed_count += 1
                    
            # Generate report
            return self._generate_excel_report()
            
        finally:
            # Cleanup
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    os.remove(os.path.join(temp_dir, file))
                os.rmdir(temp_dir)

    def _extract_zip(self, zip_file: bytes, extract_path: str) -> List[str]:
        """Extract and validate ZIP contents."""
        pdf_files = []
        
        with zipfile.ZipFile(io.BytesIO(zip_file)) as zf:
            for file in zf.namelist():
                if not file.lower().endswith('.pdf'):
                    continue
                    
                # Extract the PDF
                zf.extract(file, extract_path)
                pdf_path = os.path.join(extract_path, file)
                
                # Validate PDF
                if self._is_valid_pdf(pdf_path):
                    pdf_files.append(pdf_path)
                else:
                    os.remove(pdf_path)
                    
        return pdf_files

    def _is_valid_pdf(self, file_path: str) -> bool:
        """Validate if file is a proper PDF."""
        try:
            mime = magic.Magic(mime=True)
            file_type = mime.from_file(file_path)
            return file_type == 'application/pdf'
        except Exception:
            return False

    async def _process_single_cv(self, pdf_path: str):
        """Process a single CV file."""
        self.current_status = f"Processing {os.path.basename(pdf_path)}"
        
        # Convert PDF to images
        images = self._pdf_to_images(pdf_path)
        
        # Convert images to base64
        base64_images = []
        for img in images:
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            base64_images.append(f"data:image/png;base64,{img_str}")
            
        # Get AI analysis
        from .api_client import GeminiAIClient
        client = GeminiAIClient(os.getenv("PORTKEY_API_KEY"))
        analysis = await client.analyze_cv(base64_images, self.role_data)
        
        # Store results
        self.results.append({
            "filename": os.path.basename(pdf_path),
            **analysis
        })

    def _pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """Convert PDF pages to images."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            images = []
            
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(img)
                
            return images
            
        except Exception as e:
            raise ValueError(f"Failed to convert PDF to images: {str(e)}")

    def _generate_excel_report(self) -> str:
        """Generate Excel report from results."""
        try:
            # Create results directory
            os.makedirs("results", exist_ok=True)
            
            # Prepare data for Excel
            df = pd.DataFrame(self.results)
            
            # Add metadata
            metadata = {
                "Position": self.role_data["position"],
                "Required Skills": ", ".join(self.role_data["requirements_must_have"]),
                "Preferred Skills": ", ".join(self.role_data["requirements_nice_to_have"]),
                "Generated At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Total CVs Processed": len(self.results)
            }
            
            # Create Excel writer
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"results/cv_analysis_{timestamp}.xlsx"
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Write metadata
                pd.DataFrame([metadata]).T.to_excel(writer, sheet_name='Metadata')
                
                # Write results
                df.to_excel(writer, sheet_name='Analysis Results', index=False)
                
            return output_path
            
        except Exception as e:
            raise ValueError(f"Failed to generate Excel report: {str(e)}")

    def get_progress(self) -> Dict:
        """Get current processing progress."""
        return {
            "processed": self.processed_count,
            "total": self.total_count,
            "status": self.current_status,
            "percentage": (self.processed_count / self.total_count * 100) 
                if self.total_count > 0 else 0
        } 