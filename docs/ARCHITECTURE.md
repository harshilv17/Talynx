# Architecture

## System Design
ATA follows a decoupled micro-architecture:
- **Frontend**: Next.js 14 providing the UI layer, consuming standard REST APIs.
- **Backend**: FastAPI providing modular routes for each feature, communicating directly with LLMs and the database.

## Flow (JD → Offer)
1. **Intake API (`feature1`)** parses raw text into structured JSON.
2. **JD Generator (`feature1`)** expands JSON into an enterprise-grade JD.
3. **Sourcing Agent (`feature2`)** fetches matching resumes and generates embeddings.
4. **Outreach Agent (`feature3`)** initiates email pipelines.
5. **Evaluation Engine (`feature4`)** reads interview transcripts to generate candidate scorecards.
6. **Offer Generator (`feature4`)** creates conditional offer letters based on decision logic.

## MongoDB Usage
MongoDB is used as the primary data store:
- `jobs`: Stores the generated Job Descriptions and requirements.
- `candidates`: Stores resumes, semantic embeddings, and screening status.
- `evaluations`: Stores interview scorecards, pipeline states, and decision metadata.

## Agent Pipeline
The system utilizes multiple AI agents for discrete tasks:
- **Sourcing Agent**: Responsible for matching.
- **Evaluation Agent**: Analyzes interview notes and assigns scores.
- **Decision Agent**: Calculates final probabilities to output "hire", "moderate", or "no hire" signals.
