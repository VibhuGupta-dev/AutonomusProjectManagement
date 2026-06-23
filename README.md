# Autonomous Product Manager

An AI-driven Agile Product Management tool that automatically converts Requirements Documents (PDF/DOCX) into Sprints and User Stories using Google's Gemini AI, and syncs them seamlessly to Jira Software.

## Features
- **AI Document Analysis**: Upload any PDF or DOCX file to instantly extract business goals and stakeholders.
- **Automated Agile Workflows**: Generates structured Sprints and User Stories (with story points and priorities).
- **Jira Integration**: Directly pushes generated Sprints and Stories to your Jira Software cloud boards.
- **Modern UI**: Dark-themed, dynamic dashboard built with Next.js, Tailwind CSS, and Clerk Authentication.

---

## Prerequisites

Before starting, make sure you have the following installed on your machine:
- [Node.js](https://nodejs.org/en) (v18+)
- [Python](https://www.python.org/) (v3.10+)
- [PostgreSQL](https://www.postgresql.org/) (Running on default port `5432` or update `.env`)

---

## 1. Backend Setup (FastAPI & Prisma)

The backend handles the Gemini AI integrations, database models, and Jira API calls.

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create a Python Virtual Environment**:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the `backend/` folder and add:
   ```env
   DATABASE_URL="postgresql://postgres:postgres@localhost:5432/autonomouspm"
   GEMINI_API_KEY="your_google_gemini_api_key_here"
   ```
   *(Make sure to update the Database credentials if yours are different!)*

5. **Initialize the Database**:
   Push the Prisma schema to your Postgres database:
   ```bash
   prisma db push
   prisma generate
   ```

6. **Start the Backend Server**:
   ```bash
   python -m uvicorn app.main:app --reload --port 8001
   ```
   The backend will be running at `http://localhost:8001`.

---

## 2. Frontend Setup (Next.js)

The frontend is the user-facing web dashboard.

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node modules**:
   ```bash
   npm install
   ```

3. **Environment Variables**:
   Create a `.env.local` file in the `frontend/` folder and configure Clerk Authentication:
   ```env
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
   CLERK_SECRET_KEY=sk_test_...

   NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
   NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
   NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/
   NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/
   ```

4. **Start the Frontend Server**:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`.

---

## 3. How to use Jira Sync

1. Login to the application at `localhost:3000`.
2. Go to the **Settings** page from the sidebar.
3. Enter your Jira Domain (e.g. `https://your-company.atlassian.net`), Atlassian Email, and generate an API Token from your [Atlassian Security Settings](https://id.atlassian.com/manage-profile/security/api-tokens).
4. Click **Fetch Projects/Boards** and select your target Project and Board.
   - **Crucial**: To use the Sprints feature, you MUST select a board that is a `(scrum)` board. `(kanban)` and `(simple)` boards only support syncing tickets, not grouping them into sprints!
5. Save the settings. Next time you view an AI-analyzed document, click **Open in Jira**!
