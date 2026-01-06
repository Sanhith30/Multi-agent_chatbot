from typing import Dict, Any, Optional
import json

class CRMService:
    def __init__(self):
        # Mock customer database
        self.customers = {
            "9876543210": {
                "customer_id": "TC1001",
                "name": "Rahul Sharma", 
                "age": 32,
                "city": "Bangalore",
                "phone": "9876543210",
                "credit_score": 780,
                "preapproved_limit": 500000,
                "salary": 80000,
                "existing_loans": ["Car Loan"]
            },
            "9876543211": {
                "customer_id": "TC1002", 
                "name": "Priya Patel",
                "age": 28,
                "city": "Mumbai",
                "phone": "9876543211", 
                "credit_score": 720,
                "preapproved_limit": 300000,
                "salary": 60000,
                "existing_loans": []
            },
            "9876543212": {
                "customer_id": "TC1003",
                "name": "Amit Kumar",
                "age": 35,
                "city": "Delhi", 
                "phone": "9876543212",
                "credit_score": 650,
                "preapproved_limit": 200000,
                "salary": 45000,
                "existing_loans": ["Personal Loan"]
            },
            "9876543213": {
                "customer_id": "TC1004",
                "name": "Sneha Reddy",
                "age": 30,
                "city": "Hyderabad",
                "phone": "9876543213",
                "credit_score": 800,
                "preapproved_limit": 800000,
                "salary": 120000,
                "existing_loans": []
            },
            "9876543214": {
                "customer_id": "TC1005",
                "name": "Vikram Singh",
                "age": 40,
                "city": "Pune",
                "phone": "9876543214", 
                "credit_score": 690,
                "preapproved_limit": 250000,
                "salary": 55000,
                "existing_loans": ["Home Loan"]
            },
            "9876543215": {
                "customer_id": "TC1006",
                "name": "Anita Gupta",
                "age": 26,
                "city": "Chennai",
                "phone": "9876543215",
                "credit_score": 750,
                "preapproved_limit": 400000, 
                "salary": 70000,
                "existing_loans": []
            },
            "9876543216": {
                "customer_id": "TC1007",
                "name": "Rajesh Agarwal", 
                "age": 45,
                "city": "Kolkata",
                "phone": "9876543216",
                "credit_score": 680,
                "preapproved_limit": 150000,
                "salary": 40000,
                "existing_loans": ["Car Loan", "Personal Loan"]
            },
            "9876543217": {
                "customer_id": "TC1008",
                "name": "Deepika Joshi",
                "age": 29,
                "city": "Ahmedabad", 
                "phone": "9876543217",
                "credit_score": 770,
                "preapproved_limit": 600000,
                "salary": 95000,
                "existing_loans": []
            },
            "9876543218": {
                "customer_id": "TC1009",
                "name": "Suresh Nair",
                "age": 38,
                "city": "Kochi",
                "phone": "9876543218",
                "credit_score": 710,
                "preapproved_limit": 350000,
                "salary": 65000,
                "existing_loans": ["Home Loan"]
            },
            "9876543219": {
                "customer_id": "TC1010", 
                "name": "Kavya Iyer",
                "age": 31,
                "city": "Bangalore",
                "phone": "9876543219",
                "credit_score": 790,
                "preapproved_limit": 700000,
                "salary": 110000,
                "existing_loans": []
            }
        }
    
    def get_customer_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Fetch customer data by phone number"""
        return self.customers.get(phone)
    
    def get_customer_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Fetch customer data by customer ID"""
        for customer in self.customers.values():
            if customer["customer_id"] == customer_id:
                return customer
        return None
    
    def update_customer(self, phone: str, updates: Dict[str, Any]) -> bool:
        """Update customer information"""
        if phone in self.customers:
            self.customers[phone].update(updates)
            return True
        return False
    
    def create_customer(self, customer_data: Dict[str, Any]) -> str:
        """Create new customer record"""
        phone = customer_data["phone"]
        customer_id = f"TC{len(self.customers) + 1001}"
        
        customer_data["customer_id"] = customer_id
        self.customers[phone] = customer_data
        
        return customer_id
    
    def get_all_customers(self) -> Dict[str, Dict[str, Any]]:
        """Get all customer records"""
        return self.customers
    
    def search_customers(self, **criteria) -> list:
        """Search customers by criteria"""
        results = []
        
        for customer in self.customers.values():
            match = True
            for key, value in criteria.items():
                if key in customer and customer[key] != value:
                    match = False
                    break
            
            if match:
                results.append(customer)
        
        return results