# 🏦 Tata Capital Agentic AI Loan Chatbot

## 🎯 Project Overview

A comprehensive Agentic AI system for Tata Capital that manages the entire personal loan journey through intelligent conversation orchestration and specialized AI agents.

### 🧠 Agentic AI Architecture

- **Master Agent**: Orchestrates conversation flow and manages context
- **Sales Agent**: Converts users into loan applicants with persuasive dialogue
- **Verification Agent**: Handles KYC and identity confirmation
- **Underwriting Agent**: Makes credit decisions using business rules
- **Sanction Letter Agent**: Generates official PDF approval documents

## 🚀 Quick Start

### Backend Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the backend server:**
```bash
python run_backend.py
```

The backend will start on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install Node.js dependencies:**
```bash
npm install
```

3. **Start the React development server:**
```bash
npm start
```

The frontend will start on `http://localhost:3000`

## 🎮 Demo Instructions

### Test Scenarios

#### Scenario 1: Instant Approval (Existing Customer)
- **Phone**: `9876543210`
- **Expected**: Rahul Sharma, Credit Score 780, ₹5L pre-approved
- **Loan Amount**: ₹3,00,000 (within limit)
- **Result**: Instant approval + sanction letter

#### Scenario 2: Salary Verification Required
- **Phone**: `9876543211` 
- **Expected**: Priya Patel, Credit Score 720, ₹3L pre-approved
- **Loan Amount**: ₹5,00,000 (above limit, needs salary verification)
- **Result**: Salary slip upload → Approval

#### Scenario 3: Credit Score Rejection
- **Phone**: `9876543212`
- **Expected**: Amit Kumar, Credit Score 650 (below 700)
- **Result**: Polite rejection with improvement suggestions

### Conversation Flow

1. **Greeting**: Bot welcomes and asks about loan interest
2. **Sales**: Collects loan amount, tenure, purpose, phone number
3. **Verification**: OTP verification + KYC data fetch
4. **Underwriting**: Credit decision based on business rules
5. **Sanction**: PDF generation for approved loans

## 🏗️ System Architecture

```
Web Chat UI (React)
         ↓
Master Agent (LLM Orchestrator)
         ↓
-------------------------------------------------
| Sales Agent | Verification Agent | Underwriting Agent | Sanction Letter Agent |
-------------------------------------------------
         ↓
Mock APIs + Dummy Databases
         ↓
Loan Decision + PDF Sanction Letter
```

## 🧪 Mock Data

### Customer Database (10 synthetic customers)
- **TC1001**: Rahul Sharma (Score: 780, Limit: ₹5L)
- **TC1002**: Priya Patel (Score: 720, Limit: ₹3L)
- **TC1003**: Amit Kumar (Score: 650, Limit: ₹2L)
- **TC1004**: Sneha Reddy (Score: 800, Limit: ₹8L)
- **TC1005**: Vikram Singh (Score: 690, Limit: ₹2.5L)
- And 5 more...

### Underwriting Rules
1. **Credit Score < 700**: Automatic rejection
2. **Loan ≤ Pre-approved Limit**: Instant approval
3. **Loan ≤ 2× Pre-approved Limit**: Salary verification required
4. **EMI > 50% Salary**: Rejection
5. **Loan > 2× Pre-approved Limit**: Rejection

## 📊 Business Impact

- **Higher Conversion**: Automated sales process increases lead-to-loan conversion
- **Reduced Costs**: Eliminates manual underwriting for standard cases
- **Faster TAT**: Minutes instead of days for loan decisions
- **24×7 Availability**: Scalable sales engine without human intervention

## 🔧 Technical Features

- **Real-time WebSocket Communication**
- **File Upload Support** (salary slips)
- **PDF Generation** (sanction letters)
- **Session Management** with conversation memory
- **Responsive Chat UI** with typing indicators
- **Edge Case Handling** (rejections, objections)

## 📱 API Endpoints

- `GET /health` - Health check
- `WS /ws/{session_id}` - WebSocket chat connection
- `POST /upload-salary-slip/{session_id}` - File upload
- `GET /docs` - Interactive API documentation

## 🎨 UI Features

- **Tata Capital Branding**
- **ChatGPT-style Interface**
- **File Upload Widget**
- **Download Buttons** for sanction letters
- **Typing Indicators**
- **Mobile Responsive Design**

## 🏆 Hackathon Winning Elements

✅ **True Agentic AI** (not just chatbot)  
✅ **Real BFSI Decision Logic**  
✅ **End-to-end Automation**  
✅ **Clear ROI for Tata Capital**  
✅ **Production-ready Architecture**  

## 📄 Generated Documents

Approved loans automatically generate official sanction letters with:
- Customer details and loan terms
- Tata Capital branding
- Approval ID and dates
- Terms and conditions
- Contact information

---

**Built for Tata Capital Hackathon 2024** 🚀