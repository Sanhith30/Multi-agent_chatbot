from typing import Dict, Any
from datetime import datetime, timedelta
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os

class SanctionLetterAgent:
    def __init__(self):
        self.template_path = "templates/"
        
    async def generate_sanction_letter(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate official sanction letter PDF"""
        
        # Generate approval details
        approval_id = f"TC{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
        approval_date = datetime.now().strftime("%B %d, %Y")
        disbursal_date = (datetime.now() + timedelta(days=1)).strftime("%B %d, %Y")
        
        # Create PDF
        pdf_filename = f"sanction_letter_{approval_id}.pdf"
        pdf_path = f"generated_docs/{pdf_filename}"
        
        # Ensure directory exists
        os.makedirs("generated_docs", exist_ok=True)
        
        # Generate PDF
        self._create_sanction_letter_pdf(pdf_path, context, approval_id, approval_date, disbursal_date)
        
        # Get customer name from context
        customer_name = context.get('name', 'Valued Customer')
        
        message = f"""
🎊 **IT'S OFFICIAL - YOUR SANCTION LETTER IS READY!** 🎊

{customer_name}, I'm absolutely thrilled for you! Your official loan sanction letter has been generated and it's ready for download! 

📄 **Your Official Documents:**

📋 **Loan Summary:**
• **Approval ID**: {approval_id} *(Keep this safe!)*
• **Approval Date**: {approval_date}
• **Expected Money in Account**: {disbursal_date}
• **Loan Amount**: ₹{context.get('loan_amount', 0):,}

📎 **👇 DOWNLOAD YOUR SANCTION LETTER 👇**
*(This is your official loan approval document - you'll need this!)*

🎉 **What an amazing milestone!** You've just been approved for ₹{context.get('loan_amount', 0):,}! 

**Here's what happens next:**
1. **Download and save** your sanction letter (click the link above!)
2. **Review and sign** the loan agreement (we'll send it soon)
3. **Submit any pending documents** (if needed)
4. **Get your money** - funds will hit your account within 24 hours!
5. **Start your EMI** from next month (we'll remind you!)

I'm so happy I could help make this happen for you! If you have any questions at all, just ask - I'm here to help! 

**Thank you for choosing Tata Capital!** 🏦💙

Is there anything else I can help you with today? 😊
        """.strip()
        
        return {
            "content": message,
            "metadata": {
                "sanction_letter_generated": True,
                "approval_id": approval_id,
                "pdf_path": pdf_path,
                "download_url": f"/download/{pdf_filename}"
            }
        }
    
    def _create_sanction_letter_pdf(self, pdf_path: str, context: Dict[str, Any], 
                                   approval_id: str, approval_date: str, disbursal_date: str):
        """Create the actual PDF sanction letter with professional format"""
        
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        
        # Header with Tata Capital branding
        c.setFillColorRGB(0.1, 0.2, 0.5)  # Dark blue color
        c.rect(0, height - 120, width, 120, fill=1)
        
        # Company Logo and Name
        c.setFillColorRGB(1, 1, 1)  # White text
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, height - 60, "TATA CAPITAL")
        c.setFont("Helvetica", 14)
        c.drawString(50, height - 80, "Financial Services Limited")
        c.drawString(50, height - 100, "CIN: U65923MH2007PLC169607")
        
        # Document title
        c.setFillColorRGB(0, 0, 0)  # Black text
        c.setFont("Helvetica-Bold", 18)
        title = "PERSONAL LOAN SANCTION LETTER"
        title_width = c.stringWidth(title, "Helvetica-Bold", 18)
        c.drawString((width - title_width) / 2, height - 160, title)
        
        # Reference details (right aligned)
        c.setFont("Helvetica", 10)
        c.drawRightString(width - 50, height - 140, f"Ref No: {approval_id}")
        c.drawRightString(width - 50, height - 155, f"Date: {approval_date}")
        
        # Customer Address Section
        y_pos = height - 200
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_pos, "To,")
        
        y_pos -= 20
        c.setFont("Helvetica", 11)
        customer_name = context.get('name', 'Valued Customer')
        c.drawString(50, y_pos, f"Mr./Ms. {customer_name}")
        
        y_pos -= 15
        customer_city = context.get('city', 'Your City')
        c.drawString(50, y_pos, f"{customer_city}")
        
        y_pos -= 15
        customer_phone = context.get('phone', 'N/A')
        c.drawString(50, y_pos, f"Mobile: {customer_phone}")
        
        # Salutation and main content
        y_pos -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_pos, f"Dear {customer_name.split()[0] if customer_name != 'Valued Customer' else 'Sir/Madam'},")
        
        y_pos -= 30
        c.setFont("Helvetica", 11)
        c.drawString(50, y_pos, "Subject: Approval of Personal Loan Application")
        
        y_pos -= 25
        c.drawString(50, y_pos, "We are pleased to inform you that your Personal Loan application has been")
        y_pos -= 15
        c.drawString(50, y_pos, "APPROVED. The loan is sanctioned subject to the terms and conditions mentioned below:")
        
        # Loan Details in a professional table format
        y_pos -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_pos, "LOAN SANCTION DETAILS:")
        
        # Draw table header
        y_pos -= 25
        c.setFillColorRGB(0.9, 0.9, 0.9)  # Light gray background
        c.rect(50, y_pos - 15, width - 100, 20, fill=1)
        
        c.setFillColorRGB(0, 0, 0)  # Black text
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, y_pos - 10, "PARTICULARS")
        c.drawString(300, y_pos - 10, "DETAILS")
        
        # Loan details data
        y_pos -= 25
        c.setFont("Helvetica", 10)
        
        loan_amount = context.get('loan_amount', 0)
        tenure_months = context.get('tenure', 12)
        tenure_years = tenure_months // 12
        tenure_remaining_months = tenure_months % 12
        tenure_display = f"{tenure_years} years" + (f" {tenure_remaining_months} months" if tenure_remaining_months > 0 else "")
        emi = self._calculate_emi(loan_amount, tenure_months)
        
        loan_details = [
            ("Applicant Name", customer_name),
            ("Customer ID", context.get('customer_id', 'N/A')),
            ("Loan Amount Sanctioned", f"₹ {loan_amount:,}"),
            ("Rate of Interest", "12.99% per annum (reducing balance)"),
            ("Loan Tenure", f"{tenure_months} months ({tenure_display})"),
            ("EMI Amount", f"₹ {emi:,}"),
            ("Processing Fee", "₹ 999 + GST (18%)"),
            ("Total Processing Fee", "₹ 1,178"),
            ("Credit Score", str(context.get('credit_score', 'N/A'))),
            ("Pre-approved Limit", f"₹ {context.get('preapproved_limit', 0):,}"),
            ("Loan Purpose", context.get('purpose', 'Personal use')),
            ("Disbursal Mode", "NEFT/RTGS to registered bank account"),
            ("Expected Disbursal Date", disbursal_date),
            ("First EMI Due Date", self._get_first_emi_date()),
        ]
        
        for i, (label, value) in enumerate(loan_details):
            # Alternate row colors
            if i % 2 == 0:
                c.setFillColorRGB(0.95, 0.95, 0.95)
                c.rect(50, y_pos - 12, width - 100, 15, fill=1)
            
            c.setFillColorRGB(0, 0, 0)
            c.drawString(60, y_pos - 8, label)
            c.drawString(300, y_pos - 8, str(value))
            y_pos -= 15
        
        # Important Terms and Conditions
        y_pos -= 20
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y_pos, "IMPORTANT TERMS & CONDITIONS:")
        
        y_pos -= 20
        c.setFont("Helvetica", 9)
        terms = [
            "1. This sanction letter is valid for 30 days from the date of issue.",
            "2. Loan disbursal is subject to completion of documentation and verification.",
            "3. Interest will be charged from the date of disbursal at the rate mentioned above.",
            "4. EMI will commence from the month following disbursal as per the schedule.",
            "5. Prepayment: Allowed after 6 months with 2% + GST charges on outstanding principal.",
            "6. Late Payment: Penal charges of 2% per month will be levied on overdue amounts.",
            "7. The loan is secured by post-dated cheques/ECS mandate for EMI payments.",
            "8. Any change in personal/employment details must be intimated immediately.",
            "9. This loan is governed by the terms of the loan agreement to be executed.",
            "10. For any queries, please contact our customer care at 1800-209-8800."
        ]
        
        for term in terms:
            if y_pos < 100:  # Check if we need a new page
                c.showPage()
                y_pos = height - 50
            c.drawString(50, y_pos, term)
            y_pos -= 12
        
        # Congratulations message
        y_pos -= 20
        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(0.1, 0.6, 0.1)  # Green color
        c.drawString(50, y_pos, "🎉 Congratulations on your loan approval!")
        
        # Footer section
        y_pos = 120
        c.setFillColorRGB(0, 0, 0)  # Black text
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y_pos, "For Tata Capital Financial Services Limited")
        
        y_pos -= 30
        c.drawString(50, y_pos, "Authorized Signatory")
        c.drawString(50, y_pos - 15, "Branch Manager")
        
        # Contact information (right side)
        c.drawString(350, y_pos + 15, "Customer Care: 1800-209-8800")
        c.drawString(350, y_pos, "Email: customercare@tatacapital.com")
        c.drawString(350, y_pos - 15, "Website: www.tatacapital.com")
        
        # Footer line
        c.setStrokeColorRGB(0.1, 0.2, 0.5)
        c.line(50, 50, width - 50, 50)
        
        c.setFont("Helvetica", 8)
        footer_text = "This is a computer generated document and does not require physical signature."
        footer_width = c.stringWidth(footer_text, "Helvetica", 8)
        c.drawString((width - footer_width) / 2, 35, footer_text)
        
        c.save()
    
    def _get_first_emi_date(self) -> str:
        """Calculate first EMI date (next month)"""
        from datetime import datetime, timedelta
        import calendar
        
        today = datetime.now()
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=5)
        else:
            next_month = today.replace(month=today.month + 1, day=5)
        
        return next_month.strftime("%B %d, %Y")
    
    def _calculate_emi(self, amount: int, tenure: int) -> int:
        """Calculate EMI for sanction letter"""
        rate = 0.1299 / 12  # 12.99% annual rate
        if amount == 0 or tenure == 0:
            return 0
        emi = amount * rate * (1 + rate)**tenure / ((1 + rate)**tenure - 1)
        return int(emi)