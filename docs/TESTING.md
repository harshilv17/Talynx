# Testing Guide

## Feature 1: JD Generation API
1. Navigate to `http://localhost:3000/new-role`.
2. Fill out the intake form (Title, Skills, Salary).
3. Submit the form to trigger the LangGraph pipeline.
4. Wait for generation, review the JD, and click **Approve & Publish**.

## Feature 2: Sourcing & Screening Pipeline
*Automatically runs after Feature 1 JD is published.*
- Verify in MongoDB (`sourcing_candidates` collection) that candidates have been populated.
- Alternatively, check via API:
```bash
curl http://localhost:8000/api/v1/feature2/candidates/{job_id}
```
Candidates should have a `status` (pending, rejected, shortlisted) and a `score`.

## Feature 4: Evaluation & Offer UI
1. Navigate to `http://localhost:3000/feature4/<job_id>`.
2. Review the list of candidates and their Evaluation Scorecards.
3. Expand a candidate to see their Decision (Hire/No Hire).
4. Click **Generate Offer** for an eligible candidate.
5. Verify the Offer Modal opens with the correctly mapped compensation and text.

## API Validation
Test the Offer API directly:
```bash
curl -X POST http://localhost:8000/api/v1/feature4/offer/<candidate_id>
```
**Expected Response:**
```json
{
  "success": true,
  "message": "Offer generated and sent",
  "offer_text": "Dear Candidate..."
}
```
