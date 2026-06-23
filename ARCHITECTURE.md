# Autonomous Product Manager - Architecture Document

This document provides a comprehensive overview of the **Autonomous Product Manager** application's architecture. It breaks down the technologies used, the core data flow, and how the different services interact with each other to automate agile product management tasks.

---

## 1. High-Level Architecture Overview

The system is built on a modern, decoupled architecture consisting of:
- **Client (Frontend)**: A Next.js application handling the User Interface, authentication, and user interactions.
- **Server (Backend)**: A Python FastAPI application providing RESTful APIs, orchestrating AI workflows, and handling third-party integrations (Jira).
- **Database**: A PostgreSQL database managed via Prisma ORM for persistent storage of projects, sprints, and user stories.
- **AI Engine**: Google's Gemini LLM used for extracting structured sprint data from unstructured documents.

---

## 2. Technology Stack

### Frontend (User Interface)
*   **Framework**: Next.js 15 (App Router) & React
*   **Styling**: Tailwind CSS for responsive, utility-first styling.
*   **Authentication**: Clerk (Provides secure sign-up, sign-in, and session management).
*   **UI Components**: Lucide-react (Icons) and react-hot-toast (Dynamic popup notifications).

### Backend (API & Processing)
*   **Framework**: FastAPI (Python) - Chosen for its high performance, asynchronous capabilities, and automatic OpenAPI documentation.
*   **ORM**: Prisma Client Python - Used to interact with PostgreSQL using strong typing and auto-generated queries.
*   **AI Integration**: `google-generativeai` SDK (Model: `gemini-2.5-flash`).
*   **Document Parsers**: `pypdf` (for PDF files) and `python-docx` (for Word documents).
*   **HTTP Client**: `httpx` (For asynchronous API calls to Jira).

### Infrastructure & Data
*   **Database**: PostgreSQL
*   **Storage**: Local file system (`secure_uploads/` directory) for temporarily storing uploaded requirement documents.

---

## 3. Core Modules & Data Flow

### A. Authentication Flow
1. User accesses the frontend.
2. Clerk middleware intercepts the request. If unauthenticated, the user is redirected to the Clerk hosted Sign-in/Sign-up page.
3. Upon successful login, the frontend receives an active session and renders the Dashboard.

### B. Document Upload & Processing Workflow
This is the core engine of the application where unstructured data is converted into agile tickets.

1. **Upload Phase**: 
   - User uploads a `.pdf` or `.docx` file from the frontend.
   - The frontend sends a `POST` request to `backend/api/v1/documents/upload`.
   - The backend saves the physical file and creates a `Document` record in PostgreSQL with a status of `PENDING`.
2. **Background Processing**:
   - FastAPI spawns an asynchronous background task (`run_workflow_background`).
   - The document status is updated to `PROCESSING`.
   - The backend uses `pypdf` or `python-docx` to extract raw text from the file.
3. **AI Generation (Gemini)**:
   - The extracted text is sent to the **Gemini 2.5 Flash** model with a strict system prompt.
   - The LLM acts as an expert Product Manager and outputs a highly structured JSON response containing:
     - Business Goals
     - Stakeholders
     - Sprint Plans (Goals and Timelines)
     - User Stories (Title, Description, Acceptance Criteria, Priority, and Story Points).
4. **Database Persistence**:
   - The backend parses the JSON and saves the extracted `Sprints` and `User Stories` into their respective PostgreSQL tables via Prisma.
   - The Document status is marked as `COMPLETED`.
5. **UI Update**:
   - The frontend polls or refetches the project details and dynamically renders the Sprint Board with the newly generated AI tickets.

### C. Jira Integration Architecture
The application acts as a bridge between the AI-generated backlog and the user's actual Jira workspace.

1. **Configuration**:
   - User inputs their Jira Domain, Atlassian Email, and API Token on the Settings page.
   - The backend exposes discovery APIs (`/api/v1/jira/projects` and `/api/v1/jira/boards`) to fetch available Jira projects and agile boards dynamically.
2. **Syncing Process**:
   - When the user clicks "Open in Jira", the frontend triggers a sync pipeline.
   - **Step 1 (Create Issues)**: The backend uses Jira's REST API (`POST /rest/api/2/issue`) to create tickets. It maps our internal "Priority" (Critical, High, Medium, Low) to Jira's default priorities and formats the description using Jira wiki markup.
   - *Fallback Mechanism*: If the Jira project does not support the "Story" issue type (e.g., Simple or Kanban projects), the backend automatically falls back to creating "Task" issue types to prevent complete failure.
   - **Step 2 (Create Sprints)**: The backend uses Jira's Agile API (`POST /rest/agile/1.0/sprint`) to create a new Sprint on the designated Scrum board.
   - **Step 3 (Assign Issues)**: The backend links the newly created issue keys to the newly created Sprint using `POST /rest/agile/1.0/sprint/{id}/issue`.
3. **Error Handling**:
   - Detailed error messages from the Jira API are propagated back to the frontend and displayed via `react-hot-toast` notifications.

---

## 4. Database Schema (Prisma)

The application uses a relational schema. Key entities include:

*   **Project**: The root entity container representing a specific product or initiative.
*   **Document**: Files uploaded under a project (1-to-many relationship with Project).
*   **RequirementAnalysis**: The AI's summary of business goals and stakeholders (1-to-1 with Document).
*   **SprintPlan**: AI-generated sprints (1-to-many with Project).
*   **UserStory**: Individual tickets representing work items (belongs to a Project and a SprintPlan). Includes fields for story points, priority, and status.

---

## 5. Security Considerations
- **API Keys**: The `GEMINI_API_KEY` is kept exclusively on the backend (`.env`).
- **Jira Tokens**: User Jira API tokens are stored securely in the browser's `localStorage` and transmitted via HTTPS to the backend only when syncing. They are never logged or stored in the database.
- **File Storage**: Uploaded files are stored in an isolated `secure_uploads` directory and are not publicly served over HTTP.
