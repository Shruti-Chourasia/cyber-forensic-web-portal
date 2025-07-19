from fastapi import FastAPI, APIRouter, HTTPException, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, date
import json


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get("MONGO_URL")
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Cyber Forensic Portal API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EvidenceDetails(BaseModel):
    evidence_type: str
    make_model: str
    serial_number: str
    storage_capacity: str
    quantity: int
    condition: str

class ChainOfCustody(BaseModel):
    date_time: datetime
    person_handing_over: str
    person_receiving: str
    signature_both: str
    remarks: str

class EvidenceSubmission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # Case Information
    case_title: str
    case_type: str
    date_of_submission: date
    time_of_submission: str
    investigation_officer: str
    organization: str
    contact_number: str
    email: str
    
    # Evidence Details
    evidence_details: List[EvidenceDetails]
    
    # Description
    description: str
    
    # Source & Seizure Details
    seized_by: str
    designation: str
    place_of_seizure: str
    seizure_datetime: datetime
    authority_of_seizure: str
    
    # Chain of Custody
    chain_of_custody: List[ChainOfCustody]
    
    # Lab Section
    evidence_received_by: str
    lab_designation: str
    receipt_datetime: datetime
    assigned_lab_case_id: str
    initial_assessment: str
    lab_signature: str
    receipt_issued: bool
    
    # Declaration
    declaration_signature: str
    declaration_name: str
    declaration_designation: str
    declaration_date: date
    
    # Terms accepted
    terms_accepted: bool
    
    # Metadata
    submitter_email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SimpleUser(BaseModel):
    name: str
    email: str

class LabUpdate(BaseModel):
    lab_case_id: str
    evidence_received_by: str
    lab_designation: str
    receipt_datetime: datetime
    assigned_lab_case_id: str
    initial_assessment: str
    lab_signature: str
    receipt_issued: bool

# Helper functions
async def save_to_sheets(submission: EvidenceSubmission):
    """Save evidence submission to Google Sheets - placeholder"""
    try:
        logging.info(f"Saving submission {submission.id} to Google Sheets")
        # Placeholder for Google Sheets integration
        return True
    except Exception as e:
        logging.error(f"Failed to save to Google Sheets: {e}")
        return False

# Routes
@api_router.post("/simple-login")
async def simple_login(user: SimpleUser):
    """Simple login with name and email"""
    try:
        # Check if user exists
        user_doc = await db.users.find_one({"email": user.email})
        if not user_doc:
            # Create new user
            new_user = User(
                email=user.email,
                name=user.name
            )
            await db.users.insert_one(new_user.dict())
        
        return {
            "message": "Login successful",
            "user": {
                "email": user.email,
                "name": user.name
            }
        }
    except Exception as e:
        logging.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@api_router.post("/submit-evidence", response_model=Dict[str, Any])
async def submit_evidence(submission: EvidenceSubmission):
    """Submit evidence form data - no authentication required"""
    try:
        data = submission.dict()

        # 🔧 Convert all `date` fields to `datetime`
        for field in ['date_of_submission', 'declaration_date']:
            if field in data:
                data[field] = datetime.combine(data[field], datetime.min.time())

        # Save to MongoDB
        result = await db.evidence_submissions.insert_one(data)

        # Save to Google Sheets (placeholder)
        sheets_success = await save_to_sheets(submission)

        return {
            "success": True,
            "message": "Evidence submitted successfully",
            "submission_id": submission.id,
            "mongo_id": str(result.inserted_id),
            "sheets_saved": sheets_success
        }
    except Exception as e:
        logging.error(f"Error submitting evidence: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit evidence")

@api_router.get("/evidence/{submission_id}")
async def get_evidence(submission_id: str):
    """Get evidence submission by ID"""
    submission = await db.evidence_submissions.find_one({"id": submission_id})
    if not submission:
        raise HTTPException(status_code=404, detail="Evidence submission not found")
    
    # Remove MongoDB ObjectId for JSON serialization
    submission.pop("_id", None)
    return submission

@api_router.get("/evidence")
async def get_all_evidence():
    """Get all evidence submissions"""
    submissions = await db.evidence_submissions.find().to_list(1000)
    
    # Remove MongoDB ObjectId for JSON serialization
    for submission in submissions:
        submission.pop("_id", None)
    
    return {"submissions": submissions}

@api_router.put("/evidence/{submission_id}/lab-update")
async def update_lab_info(submission_id: str, lab_update: LabUpdate):
    """Update lab section information"""
    update_data = {
        "evidence_received_by": lab_update.evidence_received_by,
        "lab_designation": lab_update.lab_designation,
        "receipt_datetime": lab_update.receipt_datetime,
        "assigned_lab_case_id": lab_update.assigned_lab_case_id,
        "initial_assessment": lab_update.initial_assessment,
        "lab_signature": lab_update.lab_signature,
        "receipt_issued": lab_update.receipt_issued,
        "updated_at": datetime.utcnow()
    }
    
    result = await db.evidence_submissions.update_one(
        {"id": submission_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Evidence submission not found")
    
    return {"message": "Lab information updated successfully"}

@api_router.get("/")
async def root():
    return {"message": "Cyber Forensic Portal API is running"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["https://cyber-forensic-portal.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
