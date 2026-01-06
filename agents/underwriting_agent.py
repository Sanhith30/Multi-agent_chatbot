from typing import Dict, Any

class UnderwritingAgent:
    def __init__(self, credit_service):
        self.credit_service = credit_service
        
    async def evaluate_loan(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main underwriting logic"""
        
        # Get customer data
        credit_score = context.get("credit_score", 0)
        loan_amount = context.get("loan_amount", 0)
        preapproved_limit = context.get("preapproved_limit", 0)
        
        # Apply underwriting rules
        decision = self._apply_underwriting_rules(credit_score, loan_amount, preapproved_limit)
        
        if decision["status"] == "rejected":
            return {
                "content": self._format_rejection_message(decision["reason"]),
                "decision": "rejected",
                "reason": decision["reason"],
                "metadata": {"underwriting_complete": True}
            }
            
        elif decision["status"] == "approved":
            return {
                "content": self._format_approval_message(context),
                "decision": "approved",
                "metadata": {"underwriting_complete": True}
            }
            
        elif decision["status"] == "salary_required":
            return {
                "content": self._request_salary_slip(context),
                "decision": "pending",
                "metadata": {"salary_required": True}
            }
    
    def _apply_underwriting_rules(self, credit_score: int, loan_amount: int, preapproved_limit: int) -> Dict[str, Any]:
        """Apply Tata Capital underwriting rules"""
        
        # Rule 1: Credit score check
        if credit_score < 700:
            return {"status": "rejected", "reason": "credit_score_low"}
        
        # Rule 2: Within pre-approved limit
        if loan_amount <= preapproved_limit:
            return {"status": "approved"}
        
        # Rule 3: Up to 2x pre-approved limit (need salary verification)
        if loan_amount <= (2 * preapproved_limit):
            return {"status": "salary_required"}
        
        # Rule 4: Above 2x limit
        return {"status": "rejected", "reason": "amount_too_high"}
    
    async def evaluate_with_salary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate loan with salary information"""
        
        salary = context.get("salary", 0)
        loan_amount = context.get("loan_amount", 0)
        tenure = context.get("tenure", 12)
        
        # Calculate EMI
        emi = self._calculate_emi(loan_amount, tenure)
        
        # Check EMI to salary ratio (should be <= 50%)
        emi_ratio = (emi / salary) * 100
        
        if emi_ratio <= 50:
            return {
                "content": self._format_approval_message(context),
                "decision": "approved"
            }
        else:
            return {
                "content": self._format_rejection_message("high_emi_ratio"),
                "decision": "rejected",
                "reason": "high_emi_ratio"
            }
    
    async def process_message(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process underwriting related messages"""
        
        # This agent mainly provides decisions, minimal user interaction
        return {
            "content": "Processing your application... Please wait.",
            "metadata": {"processing": True}
        }
    
    def _calculate_emi(self, amount: int, tenure: int) -> int:
        """Calculate EMI"""
        rate = 0.15 / 12  # 15% annual rate
        emi = amount * rate * (1 + rate)**tenure / ((1 + rate)**tenure - 1)
        return int(emi)
    
    def _format_approval_message(self, context: Dict[str, Any]) -> str:
        """Format loan approval message"""
        amount = context.get("loan_amount", 0)
        tenure = context.get("tenure", 12)
        name = context.get("name", "").split()[0] if context.get("name") else "there"
        emi = self._calculate_emi(amount, tenure)
        
        return f"""
🎊 **CONGRATULATIONS {name.upper()}!** 🎊

**YOUR LOAN IS APPROVED!** 

I am SO excited to share this news with you! 🥳 This is honestly one of my favorite parts of the job - seeing people get approved for their dreams!

✅ **Your Approved Loan Details:**
💰 **Amount**: ₹{amount:,} *(Exactly what you asked for!)*
🏷️ **Interest Rate**: 12.99% per annum *(Great rate for your profile!)*
📅 **Tenure**: {tenure} months ({tenure//12} years {f'{tenure%12} months' if tenure%12 > 0 else ''})
💳 **Monthly EMI**: ₹{emi:,} *(Fits perfectly in your budget!)*
🚀 **Processing Fee**: ₹999 + GST *(Very reasonable!)*

🌟 **What happens next?**
• I'm generating your official sanction letter right now
• Funds will be in your account within 24 hours
• Welcome to the Tata Capital family!

You've made an excellent choice, and I'm confident this loan is going to help you achieve exactly what you set out to do! 

*Generating your official sanction letter now... almost there!* ✨
        """.strip()
    
    def _format_rejection_message(self, reason: str) -> str:
        """Format loan rejection message"""
        
        rejection_messages = {
            "credit_score_low": """
❌ **Application Status: Not Approved**

Unfortunately, we cannot approve your loan at this time due to your current credit score being below our minimum requirement of 700.

🔄 **What you can do:**
• Improve your credit score by paying bills on time
• Clear any outstanding dues
• Reapply after 3-6 months

💡 **Alternative Options:**
• Consider a smaller loan amount
• Add a co-applicant with good credit
• Explore our secured loan products

Would you like me to help you with any of these options?
            """,
            
            "amount_too_high": """
❌ **Application Status: Not Approved**

The requested loan amount exceeds our lending policy for your profile.

💡 **Suggested Options:**
• Reduce loan amount to ₹{} or less
• Consider applying after 6 months with improved profile
• Add a co-applicant to increase eligibility

Would you like to apply for a smaller amount?
            """,
            
            "high_emi_ratio": """
❌ **Application Status: Not Approved**

Your EMI would exceed 50% of your monthly income, which is beyond our policy limits.

💡 **Options Available:**
• Increase loan tenure to reduce EMI
• Apply for a smaller loan amount
• Reapply when your income increases

Would you like to explore these options?
            """
        }
        
        return rejection_messages.get(reason, "Unfortunately, we cannot approve your loan at this time.")
    
    def _request_salary_slip(self, context: Dict[str, Any]) -> str:
        """Request salary slip for verification"""
        
        return """
📋 **Additional Verification Required**

Your loan amount is higher than your pre-approved limit. To process this, I need to verify your income.

📎 **Please upload your latest salary slip** (PDF/JPG format)

This will help me:
✅ Confirm your monthly income
✅ Calculate accurate EMI affordability  
✅ Provide instant final decision

Click the upload button below to share your salary slip.
        """.strip()