# Agentic AI-Powered Personal Loan Sales Chatbot for Tata Capital

## Project Overview
Design and implement a full Agentic AI system where a Master Agent manages conversation orchestration and multiple Worker AI Agents perform specialized tasks to complete the entire personal loan journey within a single chat session.

## Business Context (BFSI - NBFC)
Tata Capital wants a human-like AI Sales Chatbot to:
- Engage users landing via ads/emails
- Understand loan needs
- Perform verification and underwriting
- Instantly approve or reject loans
- Generate automated sanction letters

## System Architecture

### Master Agent (Orchestrator)
- **Role**: Brain of the system
- **Responsibilities**: 
  - Start conversation
  - Maintain user context & memory
  - Understand intent & readiness
  - Decide which Worker Agent to invoke
  - Handle edge cases (rejection, negotiation)
  - End conversation gracefully

### Worker Agents

#### 1. Sales Agent
- **Purpose**: Convert user into loan applicant
- **Tasks**: Ask loan details, explain rates, persuade like human sales executive

#### 2. Verification Agent
- **Purpose**: KYC & identity confirmation
- **Tasks**: Fetch KYC data, verify phone/address/city, validate age eligibility

#### 3. Underwriting Agent
- **Purpose**: Credit decision logic
- **Rules**:
  - IF credit score < 700 → Reject
  - ELSE IF loan ≤ pre-approved limit → Instant approval
  - ELSE IF loan ≤ 2× pre-approved limit → Request salary slip
  - ELSE → Reject

#### 4. Sanction Letter Generator Agent
- **Purpose**: Generate official PDF sanction letter
- **Output**: Branded PDF with customer details, loan terms, approval ID

## Technical Stack
- **Frontend**: React.js with Tailwind CSS
- **Backend**: FastAPI with LangGraph
- **AI Models**: OpenAI GPT-4
- **Database**: Mock JSON data
- **PDF Generation**: Python libraries

## Key Features
- Real-time chat interface
- File upload for salary slips
- Instant loan decisions
- PDF sanction letter generation
- Edge case handling

## Success Metrics
- Higher lead-to-loan conversion
- Reduced manual underwriting cost
- Faster TAT (minutes vs days)
- Scalable 24×7 sales engine