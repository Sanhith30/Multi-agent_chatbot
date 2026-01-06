from typing import Dict, Any, Optional
from datetime import datetime
import json

from .sales_agent import SalesAgent
from .verification_agent import VerificationAgent
from .underwriting_agent import UnderwritingAgent
from .sanction_letter_agent import SanctionLetterAgent

class MasterAgent:
    def __init__(self, session_id: str, crm_service, credit_service, session_manager):
        self.session_id = session_id
        self.crm_service = crm_service
        self.credit_service = credit_service
        self.session_manager = session_manager
        
        # Initialize worker agents
        self.sales_agent = SalesAgent()
        self.verification_agent = VerificationAgent(crm_service)
        self.underwriting_agent = UnderwritingAgent(credit_service)
        self.sanction_letter_agent = SanctionLetterAgent()
        
        # Conversation state
        self.conversation_state = "greeting"
        self.user_context = {}
        
    async def start_conversation(self) -> Dict[str, Any]:
        """Initialize conversation with welcome message"""
        self.conversation_state = "greeting"
        
        welcome_message = """
👋 Hi there! I'm Sanhith, your personal loan advisor from Tata Capital.

I'm here to help you get the loan you need - whether it's for your dream home renovation, that special wedding, or any other important goal in your life! 

✨ Here's what I can do for you today:
• Get you instant approval (often in under 5 minutes!)
• Offer competitive rates starting at just 10.99%
• Minimal paperwork - we keep it simple
• Quick fund transfer to your account

So, are you looking to get a personal loan today? I'd love to help make it happen for you! 😊
        """.strip()
        
        return {
            "content": welcome_message,
            "suggestions": [
                "Yes, I need a personal loan",
                "Tell me about interest rates", 
                "What documents do I need?",
                "How much can I get?"
            ]
        }
    
    async def process_message(self, user_message: str) -> Dict[str, Any]:
        """Main orchestration logic"""
        
        # Update conversation context
        self.user_context["last_message"] = user_message
        self.user_context["timestamp"] = datetime.now().isoformat()
        
        # Handle greetings at any time
        if self._is_greeting(user_message) and not self.user_context.get("name"):
            return await self._handle_greeting()
        
        # Handle name collection after greeting
        if self.conversation_state == "collecting_name":
            return await self._collect_name(user_message)
        
        # Determine intent and route to appropriate agent
        intent = await self._analyze_intent(user_message)
        
        if self.conversation_state == "greeting":
            if intent in ["yes", "interested", "loan_inquiry"]:
                self.conversation_state = "sales"
                result = await self.sales_agent.start_sales_process()
                # Don't override suggestions if they already exist
                return result
            elif intent == "rates":
                return await self._explain_rates()
            elif intent == "documents":
                return await self._explain_documents()
            elif intent == "eligibility":
                return await self._explain_eligibility()
            else:
                return await self._handle_objection(user_message)
                
        elif self.conversation_state == "sales":
            result = await self.sales_agent.process_message(user_message, self.user_context)
            
            # Only add suggestions if they don't already exist
            if isinstance(result, dict) and not result.get("suggestions"):
                step = result.get("metadata", {}).get("step")
                if step == "tenure":
                    result["suggestions"] = ["1 year", "2 years", "3 years", "5 years"]
                elif step == "purpose":
                    result["suggestions"] = ["Home renovation", "Wedding", "Medical emergency", "Education", "Business", "Travel"]
                elif step == "phone":
                    result["suggestions"] = ["9876543210 (Demo - Instant Approval)", "9876543211 (Demo - Salary Required)", "9876543212 (Demo - Rejection)"]
            
            if result.get("next_action") == "verification":
                self.conversation_state = "verification"
                self.user_context.update(result["collected_data"])
                verification_result = await self.verification_agent.start_verification(self.user_context)
                # Only add OTP suggestions if they don't already exist
                if isinstance(verification_result, dict) and not verification_result.get("suggestions"):
                    otp = verification_result.get("metadata", {}).get("otp")
                    if otp:
                        verification_result["suggestions"] = [otp, "Resend OTP", "Change number"]
                return verification_result
            else:
                return result
                
        elif self.conversation_state == "verification":
            result = await self.verification_agent.process_message(user_message, self.user_context)
            
            # Only add suggestions if they don't already exist
            if isinstance(result, dict) and not result.get("suggestions"):
                step = result.get("metadata", {}).get("step")
                if step == "kyc_confirmation":
                    result["suggestions"] = ["Yes, correct", "No, update details", "Looks good"]
            
            # If customer data is returned, update context
            if result.get("customer_data"):
                self.user_context.update(result["customer_data"])
            
            if result.get("next_action") == "underwriting":
                self.conversation_state = "underwriting"
                
                try:
                    # Automatically evaluate the loan after verification
                    evaluation_result = await self.underwriting_agent.evaluate_loan(self.user_context)
                    
                    if evaluation_result.get("decision") == "approved":
                        self.conversation_state = "sanction"
                        sanction_result = await self.sanction_letter_agent.generate_sanction_letter(self.user_context)
                        # Add final suggestions
                        if isinstance(sanction_result, dict):
                            sanction_result["suggestions"] = ["Download letter", "Apply for another loan", "Thank you", "Contact support"]
                        return sanction_result
                    elif evaluation_result.get("decision") == "rejected":
                        rejection_result = await self._handle_rejection(evaluation_result.get("reason", "Unknown reason"))
                        if isinstance(rejection_result, dict):
                            rejection_result["suggestions"] = ["Apply for smaller amount", "Improve credit score", "Add co-applicant", "Contact support"]
                        return rejection_result
                    else:
                        # Add suggestions for salary upload
                        if isinstance(evaluation_result, dict):
                            evaluation_result["suggestions"] = ["Upload salary slip", "Try smaller amount", "Contact support"]
                        return evaluation_result
                except Exception as e:
                    # Return a simple error message and try to continue
                    return {
                        "content": f"There was an issue processing your application. Error: {str(e)}. Let me try a different approach.",
                        "metadata": {"error": True},
                        "suggestions": ["Try again", "Contact support", "Start over"]
                    }
            else:
                return result
                
        elif self.conversation_state == "underwriting":
            # This state should rarely be reached since we auto-evaluate after verification
            result = await self.underwriting_agent.process_message(user_message, self.user_context)
            return result
                
        elif self.conversation_state == "sanction":
            return {
                "content": "Your loan has been approved! You should receive the sanction letter shortly. Is there anything else I can help you with?",
                "metadata": {"conversation_complete": True},
                "suggestions": ["Download letter", "Apply for another loan", "Thank you", "Contact support"]
            }
    
    async def _analyze_intent(self, message: str) -> str:
        """Analyze user intent using LLM"""
        prompt = f"""
        Analyze the user's intent from this message: "{message}"
        
        Return one of these intents:
        - yes: User is interested/agreeing
        - no: User is declining/not interested  
        - loan_inquiry: User asking about loans
        - rates: User asking about interest rates
        - documents: User asking about required documents
        - eligibility: User asking about loan eligibility
        - objection: User has concerns/objections
        - information: User asking for information
        - ready: User ready to proceed
        
        Intent:
        """
        
        # Mock intent analysis - in production use OpenAI
        message_lower = message.lower()
        if any(word in message_lower for word in ["yes", "sure", "okay", "interested", "need a loan"]):
            return "yes"
        elif any(word in message_lower for word in ["no", "not interested", "maybe later"]):
            return "no"
        elif any(word in message_lower for word in ["rate", "interest", "percentage", "%"]):
            return "rates"
        elif any(word in message_lower for word in ["document", "papers", "paperwork", "requirements"]):
            return "documents"
        elif any(word in message_lower for word in ["eligible", "qualify", "how much", "maximum", "limit"]):
            return "eligibility"
        elif any(word in message_lower for word in ["loan", "money", "borrow", "credit"]):
            return "loan_inquiry"
        else:
            return "information"
    
    def _is_greeting(self, message: str) -> bool:
        """Check if message is a greeting"""
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "namaste"]
        return any(greeting in message.lower() for greeting in greetings)
    
    async def _handle_greeting(self) -> Dict[str, Any]:
        """Handle user greeting and ask for name"""
        self.conversation_state = "collecting_name"
        
        message = """
Hello! 👋 It's so wonderful to meet you! 

I'm Sanhith, your personal loan advisor from Tata Capital, and I'm absolutely delighted you're here today! 😊

Before we get started, I'd love to know your name so I can assist you better. What should I call you?
        """.strip()
        
        return {
            "content": message,
            "suggestions": ["My name is...", "Call me...", "I'm...", "Skip name"]
        }
    
    async def _collect_name(self, user_message: str) -> Dict[str, Any]:
        """Collect user's name and personalize the experience"""
        # Extract name from message
        name = self._extract_name(user_message)
        
        if name and name.lower() != "skip":
            self.user_context["name"] = name
            self.conversation_state = "greeting"
            
            message = f"""
{name}! What a lovely name! 😊 It's such a pleasure to meet you, {name}!

I'm here to help you get the perfect personal loan for whatever you need - whether it's for home renovation, a wedding, medical expenses, or any other important goal in your life!

✨ Here's what I can do for you today:
• Get you instant approval (often in under 5 minutes!)
• Offer competitive rates starting at just 10.99%
• Minimal paperwork - we keep it simple
• Quick fund transfer to your account

So {name}, are you looking to get a personal loan today? I'd love to help make it happen for you! 🎉
            """.strip()
            
            return {
                "content": message,
                "suggestions": [
                    "Yes, I need a personal loan",
                    "Tell me about interest rates",
                    "What documents do I need?",
                    "How much can I get?"
                ]
            }
        else:
            # If name extraction failed or user wants to skip
            self.conversation_state = "greeting"
            
            message = """
No problem at all! I'm happy to help you regardless! 😊

I'm here to help you get the perfect personal loan for whatever you need - whether it's for home renovation, a wedding, medical expenses, or any other important goal in your life!

✨ Here's what I can do for you today:
• Get you instant approval (often in under 5 minutes!)
• Offer competitive rates starting at just 10.99%
• Minimal paperwork - we keep it simple
• Quick fund transfer to your account

So, are you looking to get a personal loan today? I'd love to help make it happen for you! 🎉
            """.strip()
            
            return {
                "content": message,
                "suggestions": [
                    "Yes, I need a personal loan",
                    "Tell me about interest rates",
                    "What documents do I need?",
                    "How much can I get?"
                ]
            }
    
    def _extract_name(self, message: str) -> str:
        """Extract name from user message"""
        import re
        
        # Common patterns for name introduction
        patterns = [
            r"my name is (\w+)",
            r"i'm (\w+)",
            r"i am (\w+)",
            r"call me (\w+)",
            r"(\w+) here",
            r"this is (\w+)"
        ]
        
        message_lower = message.lower()
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                return match.group(1).title()
        
        # If no pattern matches, try to extract first word that looks like a name
        words = message.split()
        for word in words:
            if word.isalpha() and len(word) > 2 and word.lower() not in ["the", "and", "for", "you", "are", "can", "will", "have", "this", "that", "with", "from", "they", "been", "have", "their", "said", "each", "which", "what", "where", "when", "skip"]:
                return word.title()
        
        return None
    
    async def _explain_rates(self) -> Dict[str, Any]:
        """Explain interest rates"""
        user_name = self.user_context.get("name", "")
        greeting = f"{user_name}, " if user_name else ""
        
        message = f"""
{greeting}Great question! Let me break down our interest rates for you! 💰

🏷️ **Our Personal Loan Interest Rates:**

✅ **Starting Rate**: 10.99% per annum (for excellent credit profiles)
✅ **Typical Range**: 10.99% - 24.99% per annum
✅ **Rate Type**: Reducing balance (you pay interest only on outstanding amount)

🎯 **What determines your rate?**
• Your credit score (higher score = lower rate)
• Your income and employment stability
• Loan amount and tenure
• Your relationship with Tata Capital

📊 **Rate Examples:**
• Credit Score 750+: 10.99% - 15.99%
• Credit Score 700-749: 16.99% - 20.99%
• Credit Score 650-699: 21.99% - 24.99%

The good news? Most of our customers get rates much better than credit cards (which charge 18-36%!)

Would you like me to check what rate you'd qualify for? It's completely free and takes just 2 minutes! 😊
        """.strip()
        
        return {
            "content": message,
            "suggestions": [
                "Check my rate",
                "Yes, let's apply",
                "Tell me more",
                "What documents needed?"
            ]
        }
    
    async def _explain_documents(self) -> Dict[str, Any]:
        """Explain required documents"""
        user_name = self.user_context.get("name", "")
        greeting = f"{user_name}, " if user_name else ""
        
        message = f"""
{greeting}I love this question because our documentation is SO simple! 📄

🎯 **Basic Documents (Required for everyone):**
✅ **Aadhaar Card** - for identity verification
✅ **PAN Card** - for income tax verification

📱 **That's it for most loans!** Seriously, just these two!

📋 **Additional Documents (only if needed):**
• **Latest Salary Slip** - if loan amount is high
• **Bank Statement** - for income verification (3 months)
• **Employment Letter** - sometimes for new jobs

🚀 **Why so few documents?**
• We use advanced AI to verify your details
• Direct integration with government databases
• Your credit score tells us most of what we need
• Tata Capital believes in keeping things simple!

💡 **Pro tip**: Have digital copies on your phone - makes the process super fast!

Most customers are amazed at how little paperwork we need. Ready to see how simple it can be?
        """.strip()
        
        return {
            "content": message,
            "suggestions": [
                "Yes, let's start",
                "I have these documents",
                "Check my eligibility",
                "What about income proof?"
            ]
        }
    
    async def _explain_eligibility(self) -> Dict[str, Any]:
        """Explain loan eligibility"""
        user_name = self.user_context.get("name", "")
        greeting = f"{user_name}, " if user_name else ""
        
        message = f"""
{greeting}Excellent question! Let me tell you about our eligibility criteria - you might be surprised by how much you can get! 🎯

💰 **Loan Amount Range:**
• **Minimum**: ₹50,000
• **Maximum**: ₹40,00,000 (40 lakhs!)

👤 **Basic Eligibility:**
✅ **Age**: 21-65 years
✅ **Income**: ₹25,000+ per month (salaried)
✅ **Credit Score**: 650+ (we're quite flexible!)
✅ **Employment**: 1+ year current job

🏆 **How much can YOU get?**
• **Good credit (750+)**: Up to 20-25x your monthly salary
• **Average credit (700-749)**: Up to 15-20x your monthly salary  
• **Fair credit (650-699)**: Up to 10-15x your monthly salary

📊 **Quick Examples:**
• ₹50,000 salary → Up to ₹12.5 lakhs loan
• ₹75,000 salary → Up to ₹18.75 lakhs loan
• ₹1,00,000 salary → Up to ₹25 lakhs loan

🎉 **Special Categories (Higher eligibility):**
• Government employees
• PSU employees  
• Top private company employees
• Existing Tata Capital customers

Want me to check your exact eligibility? It's free and takes just 2 minutes! 😊
        """.strip()
        
        return {
            "content": message,
            "suggestions": [
                "Check my eligibility",
                "Yes, let's apply",
                "I earn ₹50,000",
                "I earn ₹1,00,000"
            ]
        }
    
    async def _handle_objection(self, message: str) -> Dict[str, Any]:
        """Handle user objections with persuasive responses"""
        
        user_name = self.user_context.get("name", "")
        greeting = f"{user_name}, " if user_name else ""
        
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["not interested", "no", "maybe later"]):
            response = f"""
{greeting}I totally understand! Taking a loan is a big decision and you want to be sure it's right for you. 

But here's the thing - I've helped thousands of customers just like you, and many were initially hesitant too. What if I told you that:

🎯 You can check your eligibility in just 2 minutes with NO commitment
💰 Our rates are often 5-8% lower than credit cards
🚀 Most customers are surprised by how much they qualify for

Would you be open to just seeing what you're eligible for? No pressure at all - think of it as getting a free financial health check! 

What do you say? 😊
            """
            suggestions = ["Check eligibility", "Tell me more", "What's the process?", "Maybe later"]
            
        elif any(word in message_lower for word in ["interest", "rate", "expensive"]):
            response = f"""
{greeting}I hear you on the interest rates - that's always a smart thing to ask about! 

Here's some good news: our rates start from just 10.99%, which is typically much lower than:
• Credit cards (18-36% annually) 
• Other personal loan providers
• Emergency borrowing options

Plus, with your profile, you might qualify for our best rates! The exact rate depends on your credit score and income, but I've seen customers get rates as low as 10.99%.

Want me to check what rate you'd qualify for? It takes just a minute and there's no obligation! 
            """
            suggestions = ["Check my rate", "Tell me more about rates", "Yes, let's proceed", "Compare with others"]
            
        elif any(word in message_lower for word in ["documents", "paperwork", "hassle"]):
            response = f"""
{greeting}Oh, I'm so glad you asked! This is actually one of my favorite things about Tata Capital - we've made it super simple! 

All you need is:
📱 Your Aadhaar (for identity)
💳 Your PAN card (for verification)
📄 Latest salary slip (if needed)

That's it! No running around, no complicated forms. Most of our customers are amazed at how easy we've made it.

In fact, many loans get approved with just Aadhaar and PAN. Should we check if yours can be one of them? 😊
            """
            suggestions = ["Yes, let's try", "I have these documents", "What about income proof?", "Sounds simple"]
            
        else:
            response = f"""
{greeting}I completely understand your concern! You know what? In my experience helping customers, the best way to address any doubts is to simply see what options are available to you.

Here's what I suggest - let me quickly check your eligibility. It's:
✅ Completely free
✅ No impact on your credit score  
✅ No commitment required
✅ Takes under 2 minutes

If you like what you see, great! If not, no worries at all. At least you'll know exactly where you stand.

Sound fair? Let's give it a try! 😊
            """
            suggestions = ["Okay, let's try", "Tell me more", "What's the process?", "I'm not sure"]
        
        return {
            "content": response.strip(),
            "metadata": {"objection_handled": True},
            "suggestions": suggestions
        }
    
    async def _handle_rejection(self, reason: str) -> Dict[str, Any]:
        """Handle loan rejection gracefully"""
        user_name = self.user_context.get("name", "")
        greeting = f"{user_name}, " if user_name else ""
        
        rejection_message = f"""
{greeting}I'm sorry, but we're unable to approve your loan application at this time due to: {reason}

However, don't worry! Here are some options:
✅ Improve your credit score and reapply in 3 months
✅ Consider a smaller loan amount
✅ Add a co-applicant to strengthen your application

Would you like me to help you with any of these options?
        """.strip()
        
        return {
            "content": rejection_message,
            "metadata": {"loan_rejected": True, "reason": reason},
            "suggestions": ["Apply for smaller amount", "Improve credit score", "Add co-applicant", "Contact support"]
        }
    
    async def process_salary_slip(self, file_path: str) -> str:
        """Process uploaded salary slip"""
        # Mock salary extraction - in production use OCR
        extracted_salary = 75000  # Mock extracted amount
        
        self.user_context["salary"] = extracted_salary
        
        # Continue with underwriting
        result = await self.underwriting_agent.evaluate_with_salary(self.user_context)
        
        return result["content"]