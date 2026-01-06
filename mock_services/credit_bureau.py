from typing import Dict, Any
import random
from datetime import datetime, timedelta

class CreditBureauService:
    def __init__(self):
        # Mock credit bureau responses
        self.credit_data = {}
    
    def get_credit_score(self, phone: str, pan: str = None) -> Dict[str, Any]:
        """Fetch credit score from bureau"""
        
        # Mock credit score based on phone (for demo consistency)
        phone_last_digit = int(phone[-1]) if phone else 5
        
        # Generate consistent score based on phone
        base_score = 650 + (phone_last_digit * 15)
        
        # Add some randomness
        score = base_score + random.randint(-20, 50)
        score = max(300, min(900, score))  # Keep within valid range
        
        return {
            "credit_score": score,
            "score_date": datetime.now().strftime("%Y-%m-%d"),
            "bureau": "CIBIL",
            "factors": self._get_score_factors(score),
            "account_summary": self._get_account_summary(phone),
            "enquiries": self._get_recent_enquiries()
        }
    
    def _get_score_factors(self, score: int) -> Dict[str, str]:
        """Get factors affecting credit score"""
        
        if score >= 750:
            return {
                "payment_history": "Excellent",
                "credit_utilization": "Low", 
                "credit_age": "Good",
                "credit_mix": "Good",
                "recent_enquiries": "Low"
            }
        elif score >= 700:
            return {
                "payment_history": "Good",
                "credit_utilization": "Moderate",
                "credit_age": "Fair", 
                "credit_mix": "Fair",
                "recent_enquiries": "Moderate"
            }
        else:
            return {
                "payment_history": "Needs Improvement",
                "credit_utilization": "High",
                "credit_age": "Limited",
                "credit_mix": "Limited", 
                "recent_enquiries": "High"
            }
    
    def _get_account_summary(self, phone: str) -> Dict[str, Any]:
        """Generate mock account summary"""
        
        phone_last_digit = int(phone[-1]) if phone else 5
        
        return {
            "total_accounts": phone_last_digit + 2,
            "active_accounts": phone_last_digit + 1,
            "closed_accounts": 1,
            "credit_cards": min(3, phone_last_digit),
            "loans": {
                "home_loan": 1 if phone_last_digit > 5 else 0,
                "auto_loan": 1 if phone_last_digit > 3 else 0,
                "personal_loan": 1 if phone_last_digit > 7 else 0
            },
            "total_credit_limit": (phone_last_digit + 1) * 100000,
            "total_outstanding": (phone_last_digit + 1) * 25000
        }
    
    def _get_recent_enquiries(self) -> list:
        """Generate mock recent credit enquiries"""
        
        enquiries = []
        
        # Generate 0-3 recent enquiries
        for i in range(random.randint(0, 3)):
            enquiry_date = datetime.now() - timedelta(days=random.randint(1, 90))
            
            enquiries.append({
                "date": enquiry_date.strftime("%Y-%m-%d"),
                "enquiry_type": random.choice(["Credit Card", "Personal Loan", "Auto Loan"]),
                "institution": random.choice(["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank"])
            })
        
        return sorted(enquiries, key=lambda x: x["date"], reverse=True)
    
    def validate_pan(self, pan: str) -> Dict[str, Any]:
        """Validate PAN number format"""
        
        import re
        
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        
        if re.match(pan_pattern, pan):
            return {
                "valid": True,
                "pan": pan,
                "name_match": True,  # Mock - always true for demo
                "status": "Active"
            }
        else:
            return {
                "valid": False,
                "error": "Invalid PAN format"
            }
    
    def get_bureau_report(self, phone: str, pan: str = None) -> Dict[str, Any]:
        """Get comprehensive credit bureau report"""
        
        credit_score_data = self.get_credit_score(phone, pan)
        
        return {
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "personal_info": {
                "phone": phone,
                "pan": pan,
                "verification_status": "Verified"
            },
            "credit_score": credit_score_data,
            "risk_assessment": self._assess_risk(credit_score_data["credit_score"]),
            "recommendations": self._get_recommendations(credit_score_data["credit_score"])
        }
    
    def _assess_risk(self, credit_score: int) -> Dict[str, Any]:
        """Assess lending risk based on credit score"""
        
        if credit_score >= 750:
            return {
                "risk_level": "Low",
                "approval_probability": "High",
                "recommended_rate": "10.99% - 12.99%"
            }
        elif credit_score >= 700:
            return {
                "risk_level": "Medium",
                "approval_probability": "Good", 
                "recommended_rate": "12.99% - 16.99%"
            }
        elif credit_score >= 650:
            return {
                "risk_level": "Medium-High",
                "approval_probability": "Moderate",
                "recommended_rate": "16.99% - 20.99%"
            }
        else:
            return {
                "risk_level": "High",
                "approval_probability": "Low",
                "recommended_rate": "20.99%+"
            }
    
    def _get_recommendations(self, credit_score: int) -> list:
        """Get recommendations for credit improvement"""
        
        if credit_score >= 750:
            return [
                "Maintain excellent payment history",
                "Consider premium credit products",
                "Eligible for best interest rates"
            ]
        elif credit_score >= 700:
            return [
                "Continue timely payments",
                "Reduce credit utilization below 30%",
                "Avoid multiple credit enquiries"
            ]
        else:
            return [
                "Focus on timely bill payments",
                "Reduce outstanding debt",
                "Avoid new credit applications",
                "Consider credit counseling"
            ]