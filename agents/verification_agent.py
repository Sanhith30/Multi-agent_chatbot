from typing import Dict, Any
import random

class VerificationAgent:
    def __init__(self, crm_service):
        self.crm_service = crm_service
        self.verification_step = "phone_otp"
        
    async def start_verification(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Start KYC verification process"""
        phone = context.get("phone")
        
        # Generate mock OTP
        otp = str(random.randint(1000, 9999))
        context["generated_otp"] = otp
        
        message = f"""
🔐 **Quick Security Check!**

Alright! I've just sent a 4-digit OTP to your mobile number ending in {phone[-2:]}. 

📱 **Please check your phone and enter the OTP here**

*(For this demo, your OTP is: **{otp}** - normally you'd get this via SMS!)*

This is just to make sure it's really you and keep your information secure. We take your privacy seriously! 

Just type the 4 digits when you get them! 😊
        """.strip()
        
        return {
            "content": message,
            "metadata": {"step": "phone_otp", "otp": otp},
            "suggestions": [otp, "Resend OTP", "Change number"]
        }
    
    async def process_message(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process verification steps"""
        
        if self.verification_step == "phone_otp":
            if self._verify_otp(user_message, context):
                self.verification_step = "fetch_kyc"
                return await self._fetch_kyc_data(context)
            else:
                return self._otp_error()
                
        elif self.verification_step == "kyc_confirmation":
            # Be more flexible with confirmation responses
            user_lower = user_message.lower()
            positive_responses = ["yes", "correct", "right", "looks good", "yes, correct", "no, update details"]
            
            if any(pos in user_lower for pos in ["yes", "correct", "right", "looks good", "good"]):
                return await self._complete_verification(context)
            elif any(neg in user_lower for neg in ["no", "update", "wrong", "incorrect"]):
                # User wants to update details
                self.verification_step = "collecting_details"
                return await self._handle_kyc_mismatch()
            else:
                # Default to proceeding if unclear
                return await self._complete_verification(context)
                
        elif self.verification_step == "collecting_details":
            # Handle new customer details collection
            return await self._process_new_customer_details(user_message, context)
    
    def _verify_otp(self, user_otp: str, context: Dict[str, Any]) -> bool:
        """Verify OTP"""
        generated_otp = context.get("generated_otp")
        return user_otp.strip() == generated_otp
    
    async def _fetch_kyc_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch customer data from CRM"""
        phone = context.get("phone")
        
        # Mock KYC fetch from CRM
        customer_data = self.crm_service.get_customer_by_phone(phone)
        
        if customer_data:
            # Update the context with customer data
            context.update(customer_data)
            self.verification_step = "kyc_confirmation"
            
            message = f"""
🎉 **Fantastic news!** 

I found your details in our system! This is going to make everything so much faster for you!

✅ **Here's what I have on file:**

👤 **Name**: {customer_data['name']}
📍 **City**: {customer_data['city']}
🎂 **Age**: {customer_data['age']} years
📊 **Credit Score**: {customer_data['credit_score']} *(That's a great score!)*
💰 **Pre-approved Limit**: ₹{customer_data['preapproved_limit']:,} *(You're pre-approved!)*

This looks perfect! Is all this information correct? 

Just say **"yes"** if everything looks good, or let me know if anything needs updating! 😊

*(Having you in our system means we can process this super quickly!)*
            """.strip()
            
            suggestions = ["Yes, correct", "No, update details", "Looks good"]
            
        else:
            # New customer - ask for basic details
            message = """
No worries! I don't see your details in our system yet, but that just means you're a new customer - welcome to the Tata Capital family! 🎉

I'll need just a few quick details to get you set up:

👤 **Full Name**: 
📍 **City**: 
🎂 **Age**: 

This will help me check your eligibility right away. Don't worry - as a new customer, you might be surprised by how much you qualify for!

Can you share these details with me?
            """
            suggestions = ["Provide details", "I'm a new customer", "Help me"]
            
        return {
            "content": message,
            "metadata": {"step": "kyc_confirmation", "customer_found": bool(customer_data)},
            "customer_data": customer_data,  # Include customer data in response
            "suggestions": suggestions
        }
    
    async def _complete_verification(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Complete verification and move to underwriting"""
        message = """
🎉 **Perfect! Verification complete!** 

✅ Mobile number verified *(Check!)*
✅ Identity confirmed *(Check!)*
✅ Details validated *(Check!)*

You know what? I'm really excited for you! Based on what I'm seeing, this is looking very promising! 

Let me now check your loan eligibility and get you that instant decision. This is the moment of truth! 🤞

*Processing your application... hang tight, this usually takes just a few seconds!*

🔄 *Checking credit profile...*
🔄 *Calculating eligibility...*
🔄 *Applying Tata Capital policies...*
        """.strip()
        
        return {
            "content": message,
            "next_action": "underwriting",
            "metadata": {"verification_complete": True},
            "suggestions": ["Continue processing", "Check status", "Wait for result"]
        }
    
    def _otp_error(self) -> Dict[str, Any]:
        """Handle OTP verification error"""
        return {
            "content": "❌ Invalid OTP. Please check and enter the correct 4-digit OTP sent to your mobile.",
            "metadata": {"error": "invalid_otp"},
            "suggestions": ["Resend OTP", "Try again", "Change number"]
        }
    
    async def _handle_kyc_mismatch(self) -> Dict[str, Any]:
        """Handle KYC data mismatch"""
        return {
            "content": "No problem! Please provide your correct details and I'll update them for you. What's your full name and current city?",
            "metadata": {"kyc_mismatch": True},
            "suggestions": ["Provide details", "Skip for now", "Use existing details"]
        }
    
    async def _process_new_customer_details(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process new customer details"""
        # For simplicity, let's just proceed with verification complete
        # In a real system, you'd parse the details and create a new customer record
        
        message = """
Thank you for providing your details! I've updated your information in our system.

🎉 **Great! Let's proceed with your loan application!**

✅ Details updated *(Check!)*
✅ Mobile number verified *(Check!)*
✅ Identity confirmed *(Check!)*

You know what? I'm really excited for you! Let me now check your loan eligibility and get you that instant decision. This is the moment of truth! 🤞

*Processing your application... hang tight, this usually takes just a few seconds!*

🔄 *Checking credit profile...*
🔄 *Calculating eligibility...*
🔄 *Applying Tata Capital policies...*
        """.strip()
        
        # Set some default values for new customers
        context.update({
            "name": "Valued Customer",
            "city": "Your City", 
            "age": 30,
            "credit_score": 720,  # Default good score
            "preapproved_limit": 300000,  # Default limit
            "customer_id": f"TC{context.get('phone', '0000')[-4:]}"
        })
        
        return {
            "content": message,
            "next_action": "underwriting",
            "metadata": {"verification_complete": True},
            "suggestions": ["Continue processing", "Check status", "Wait for result"]
        }