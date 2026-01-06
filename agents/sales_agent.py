from typing import Dict, Any

class SalesAgent:
    def __init__(self):
        self.collected_data = {}
        self.current_step = "loan_amount"
        
    async def start_sales_process(self) -> Dict[str, Any]:
        """Start the sales conversation"""
        message = """
Fantastic! I'm so excited to help you get the perfect loan! 🎉

You know what? I love this part of my job - helping people achieve their goals. Whether it's renovating your home, planning a wedding, or handling an unexpected expense, the right loan can make all the difference.

Let's start with the basics:

💰 **How much are you looking to borrow?**

You can get anywhere from ₹50,000 to ₹40 lakhs with us. Just tell me the amount that would work for your needs - you can say something like "5 lakhs" or "500000", whatever feels natural to you!

Don't worry about being exact right now - we can always adjust it based on what you qualify for. What amount do you have in mind? 😊
        """.strip()
        
        return {
            "content": message,
            "metadata": {"step": "loan_amount"},
            "suggestions": ["₹2 lakhs", "₹5 lakhs", "₹10 lakhs", "₹20 lakhs"]
        }
    
    async def process_message(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process sales conversation step by step"""
        
        if self.current_step == "loan_amount":
            amount = self._extract_amount(user_message)
            if amount:
                self.collected_data["loan_amount"] = amount
                self.current_step = "tenure"
                result = await self._ask_tenure(amount)
                result["next_action"] = "continue"
                return result
            else:
                result = self._ask_amount_clarification()
                result["next_action"] = "continue"
                return result
                
        elif self.current_step == "tenure":
            tenure = self._extract_tenure(user_message)
            if tenure:
                self.collected_data["tenure"] = tenure
                self.current_step = "purpose"
                result = await self._ask_purpose()
                result["next_action"] = "continue"
                return result
            else:
                result = self._ask_tenure_clarification()
                result["next_action"] = "continue"
                return result
                
        elif self.current_step == "purpose":
            purpose = user_message.strip()
            self.collected_data["purpose"] = purpose
            self.current_step = "phone"
            result = await self._ask_phone()
            result["next_action"] = "continue"
            return result
            
        elif self.current_step == "phone":
            phone = self._extract_phone(user_message)
            if phone:
                self.collected_data["phone"] = phone
                return await self._complete_sales()
            else:
                result = self._ask_phone_clarification()
                result["next_action"] = "continue"
                return result
    
    def _extract_amount(self, message: str) -> int:
        """Extract loan amount from user message"""
        import re
        
        # Look for numbers with lakh/lakhs
        lakh_pattern = r'(\d+(?:\.\d+)?)\s*(?:lakh|lakhs?)'
        lakh_match = re.search(lakh_pattern, message.lower())
        if lakh_match:
            return int(float(lakh_match.group(1)) * 100000)
        
        # Look for plain numbers
        number_pattern = r'(\d+(?:,\d+)*)'
        number_match = re.search(number_pattern, message)
        if number_match:
            amount = int(number_match.group(1).replace(',', ''))
            if 50000 <= amount <= 4000000:  # Valid range
                return amount
        
        return None
    
    def _extract_tenure(self, message: str) -> int:
        """Extract tenure from user message"""
        import re
        
        # Look for numbers with years/months
        year_pattern = r'(\d+)\s*(?:year|years|yr)'
        year_match = re.search(year_pattern, message.lower())
        if year_match:
            return int(year_match.group(1)) * 12
        
        month_pattern = r'(\d+)\s*(?:month|months|mon)'
        month_match = re.search(month_pattern, message.lower())
        if month_match:
            return int(month_match.group(1))
        
        # Look for plain numbers (assume months)
        number_pattern = r'(\d+)'
        number_match = re.search(number_pattern, message)
        if number_match:
            tenure = int(number_match.group(1))
            if 12 <= tenure <= 84:  # 1-7 years
                return tenure
        
        return None
    
    def _extract_phone(self, message: str) -> str:
        """Extract phone number from user message"""
        import re
        
        phone_pattern = r'(\d{10})'
        phone_match = re.search(phone_pattern, message)
        if phone_match:
            return phone_match.group(1)
        
        return None
    
    async def _ask_tenure(self, amount: int) -> Dict[str, Any]:
        """Ask for loan tenure"""
        emi_12 = self._calculate_emi(amount, 12)
        emi_24 = self._calculate_emi(amount, 24)
        emi_36 = self._calculate_emi(amount, 36)
        
        message = f"""
Perfect choice! ₹{amount:,} - that's a great amount that can really help you achieve your goals! 👍

Now, let's talk about how you'd like to repay it. I always tell my customers - choose a tenure that feels comfortable for your monthly budget. Here are some popular options:

📅 **Repayment Options:**
• **1 Year** (12 months) - EMI: ₹{emi_12:,} 
  ↳ *Higher EMI, but you'll be debt-free quickly!*
  
• **2 Years** (24 months) - EMI: ₹{emi_24:,}
  ↳ *Good balance of EMI and total interest*
  
• **3 Years** (36 months) - EMI: ₹{emi_36:,}
  ↳ *Lower EMI, more breathing room in your budget*

You can actually choose anywhere from 1 to 7 years. Most of my customers go with 2-3 years as it gives them flexibility without paying too much extra interest.

What feels right for your situation? You can say something like "2 years" or "24 months" - whatever works for you! 😊
        """.strip()
        
        return {
            "content": message,
            "metadata": {"step": "tenure", "amount": amount},
            "suggestions": ["1 year", "2 years", "3 years", "5 years"]
        }
    
    async def _ask_purpose(self) -> Dict[str, Any]:
        """Ask for loan purpose"""
        message = """
Excellent choice on the tenure! You're making really smart decisions here! 👏

Now, I'm curious - what's this loan going to help you achieve? I love hearing about people's plans and dreams!

🎯 **What will you use this loan for?**

I see all kinds of purposes, and they're all equally important:
• 🏠 **Home renovation** - making your space perfect
• 💒 **Wedding expenses** - for that special day  
• 🏥 **Medical emergency** - health comes first
• 🎓 **Education** - investing in your future
• 💳 **Debt consolidation** - simplifying your finances
• 💼 **Business needs** - growing your venture
• ✈️ **Travel** - creating memories
• 🎯 **Other** - whatever matters to you!

Just tell me in a few words what this loan will help you with. It actually helps me process your application faster, and I genuinely love knowing how we're helping people! 😊

What's your purpose?
        """.strip()
        
        return {
            "content": message,
            "metadata": {"step": "purpose"},
            "suggestions": ["Home renovation", "Wedding", "Medical emergency", "Education", "Business", "Travel"]
        }
    
    async def _ask_phone(self) -> Dict[str, Any]:
        """Ask for phone number"""
        message = """
That's wonderful! I can already see how this loan is going to make a real difference for you! 🌟

Alright, we're almost done with the basic details. Now I need your mobile number for a quick verification - it's just a security thing to make sure everything is safe and secure.

📱 **Please share your mobile number**

Here's what I'll use it for:
✅ **Instant OTP verification** (takes 30 seconds)
✅ **Loan updates** - I'll keep you posted on progress
✅ **Customer support** - in case you need any help later

Just type your 10-digit mobile number, like 9876543210. 

Don't worry - we never spam or share your number with anyone. It's just for your loan process and important updates! 😊

What's your mobile number?
        """.strip()
        
        return {
            "content": message,
            "metadata": {"step": "phone"},
            "suggestions": ["9876543210 (Demo - Instant Approval)", "9876543211 (Demo - Salary Required)", "9876543212 (Demo - Rejection)"]
        }
    
    async def _complete_sales(self) -> Dict[str, Any]:
        """Complete sales process and move to verification"""
        amount = self.collected_data["loan_amount"]
        tenure = self.collected_data["tenure"]
        purpose = self.collected_data["purpose"]
        emi = self._calculate_emi(amount, tenure)
        
        message = f"""
Perfect! Let me just summarize everything to make sure we're on the same page! 📋

🎉 **Here's your loan summary:**

💰 **Loan Amount**: ₹{amount:,}
📅 **Tenure**: {tenure} months ({tenure//12} years {tenure%12 if tenure%12 > 0 else ''} months)
💳 **Monthly EMI**: ₹{emi:,}
🎯 **Purpose**: {purpose.title()}
🏷️ **Interest Rate**: 10.99% - 24.99%* (depends on your profile)
🚀 **Processing Fee**: ₹999 + GST

*Don't worry about the rate range - with your profile, I'm confident you'll get a great rate!

This looks fantastic! You're going to love how smooth this process is. 

Now, let me quickly verify your details so we can get you that instant approval! This is the exciting part - it usually takes just 30 seconds! 

Ready? Let's do this! 🚀
        """.strip()
        
        return {
            "content": message,
            "next_action": "verification",
            "collected_data": self.collected_data,
            "metadata": {"sales_complete": True}
        }
    
    def _calculate_emi(self, amount: int, tenure: int) -> int:
        """Calculate EMI using standard formula"""
        rate = 0.15 / 12  # 15% annual rate
        emi = amount * rate * (1 + rate)**tenure / ((1 + rate)**tenure - 1)
        return int(emi)
    
    def _ask_amount_clarification(self) -> Dict[str, Any]:
        """Ask for amount clarification"""
        return {
            "content": "Hmm, I didn't quite catch the loan amount there! 😅 Could you help me out? Just tell me how much you're looking to borrow - you can say something like '5 lakhs' or '500000'. Whatever feels natural to you!",
            "metadata": {"clarification": "amount"},
            "next_action": "continue",
            "suggestions": ["₹2 lakhs", "₹5 lakhs", "₹10 lakhs", "₹20 lakhs"]
        }
    
    def _ask_tenure_clarification(self) -> Dict[str, Any]:
        """Ask for tenure clarification"""
        return {
            "content": "I want to make sure I get this right! Could you tell me how long you'd like to take to repay the loan? You can say something like '2 years' or '24 months' - whatever works for you! 😊",
            "metadata": {"clarification": "tenure"},
            "next_action": "continue",
            "suggestions": ["1 year", "2 years", "3 years", "5 years"]
        }
    
    def _ask_phone_clarification(self) -> Dict[str, Any]:
        """Ask for phone clarification"""
        return {
            "content": "Oops! I need a valid 10-digit mobile number to proceed. Could you double-check and share your mobile number again? Something like 9876543210. Thanks! 😊",
            "metadata": {"clarification": "phone"},
            "next_action": "continue",
            "suggestions": ["9876543210 (Demo - Instant Approval)", "9876543211 (Demo - Salary Required)", "9876543212 (Demo - Rejection)"]
        }