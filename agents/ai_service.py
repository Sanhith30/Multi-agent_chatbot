"""
Real AI Service Integration for Production
"""
import openai
from typing import Dict, Any, List
import os
from datetime import datetime
import json

class AIService:
    def __init__(self):
        # Initialize OpenAI client
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4"  # or "gpt-3.5-turbo" for cost optimization
        
    async def analyze_intent(self, message: str, context: Dict[str, Any]) -> str:
        """
        Real intent analysis using GPT-4
        """
        system_prompt = """
        You are an expert intent classifier for a loan application system.
        Analyze the user's message and return one of these intents:
        - greeting: User is saying hello or starting conversation
        - loan_inquiry: User wants to apply for a loan
        - amount_query: User is specifying loan amount
        - tenure_query: User is specifying loan tenure
        - document_query: User asking about required documents
        - rate_query: User asking about interest rates
        - objection: User has concerns or objections
        - confirmation: User is confirming or agreeing
        - rejection: User is declining or not interested
        
        Return only the intent name, nothing else.
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Message: {message}\nContext: {json.dumps(context)}"}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip().lower()
        except Exception as e:
            # Fallback to rule-based intent detection
            return self._fallback_intent_analysis(message)
    
    async def generate_response(self, intent: str, user_message: str, context: Dict[str, Any]) -> str:
        """
        Generate contextual responses using GPT-4
        """
        user_name = context.get('name', 'there')
        conversation_history = context.get('conversation_history', [])
        
        system_prompt = f"""
        You are Sanhith, a professional loan advisor at Tata Capital. You are helpful, friendly, and knowledgeable about personal loans.
        
        Current context:
        - User name: {user_name}
        - Conversation stage: {context.get('conversation_state', 'greeting')}
        - Intent: {intent}
        
        Guidelines:
        - Be conversational and human-like
        - Use the user's name when appropriate
        - Provide specific loan information when asked
        - Keep responses concise but informative
        - Always maintain a professional yet friendly tone
        - If discussing loan terms, mention Tata Capital's competitive rates
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history for context
        for msg in conversation_history[-5:]:  # Last 5 messages for context
            messages.append({
                "role": "user" if msg['sender'] == 'user' else "assistant",
                "content": msg['content']
            })
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"I apologize, but I'm experiencing some technical difficulties. Let me help you with your loan inquiry in a moment."
    
    def _fallback_intent_analysis(self, message: str) -> str:
        """Fallback rule-based intent analysis"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["hi", "hello", "hey"]):
            return "greeting"
        elif any(word in message_lower for word in ["loan", "borrow", "money"]):
            return "loan_inquiry"
        elif any(word in message_lower for word in ["lakh", "thousand", "₹"]):
            return "amount_query"
        elif any(word in message_lower for word in ["year", "month", "tenure"]):
            return "tenure_query"
        elif any(word in message_lower for word in ["rate", "interest", "%"]):
            return "rate_query"
        elif any(word in message_lower for word in ["document", "papers"]):
            return "document_query"
        elif any(word in message_lower for word in ["yes", "ok", "sure"]):
            return "confirmation"
        elif any(word in message_lower for word in ["no", "not interested"]):
            return "rejection"
        else:
            return "general_query"

# Usage in agents
ai_service = AIService()