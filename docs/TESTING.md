# Testing Guide

## Testing Each Feature

### Feature 1: JD Generation
1. Navigate to the frontend UI (`/new-role`).
2. Enter a role brief and submit.
3. Verify that a comprehensive job description is generated and saved.

### Feature 2: Sourcing & Screening
1. Use an existing `job_id` (from JD Generation).
2. Go to the Sourcing Dashboard.
3. Click "Start Sourcing" to trigger semantic matching.
4. Verify candidates appear in the Shortlisted or Pending tabs.

### Feature 3: Outreach
- Tested externally (handled by outreach service teammates). Check integration points at `/api/v1/feature3/`.

### Feature 4: Evaluation & Offer
1. Navigate to `/feature4/[job_id]` using a valid `job_id`.
2. Ensure candidate scorecards appear with evaluation criteria.
3. Click on a "Strong Hire" candidate and click "Generate Offer".
4. A modal should pop up with the generated offer letter, which can be downloaded or copied.

## API Examples

### Get Candidate Evaluation
```bash
curl -X GET http://localhost:8000/api/v1/feature4/evaluation/{job_id}
```

### Generate Offer Letter
```bash
curl -X POST http://localhost:8000/api/v1/feature4/offer/{candidate_id}
```
