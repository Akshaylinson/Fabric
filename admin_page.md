# Feature Request: Internal Admin Dashboard & AI Workflow Testing Console

## Objective

Build a comprehensive internal web-based Admin Dashboard for the Textile AI Platform.

This dashboard is **not customer-facing** and **not intended for textile shop staff**.

Its primary purpose is:

1. Internal platform administration.
2. Testing and validating all AI workflows.
3. Monitoring platform health.
4. Debugging AI pipelines.
5. Viewing analytics and usage statistics.
6. Managing templates, jobs, users, and generated outputs.
7. Serving as the primary QA/testing interface during development.

The dashboard will be used by:

* Platform Administrators
* Developers
* QA Engineers
* AI Engineers
* System Operators

The dashboard should be implemented as a separate frontend application communicating exclusively with backend APIs.

---

# Technology Stack

Frontend:

* React
* Next.js
* TypeScript
* Tailwind CSS
* ShadCN UI
* React Query
* Zustand

Charts:

* Recharts

Authentication:

* JWT-based authentication using existing Auth Service APIs.

---

# Core Requirements

The Admin Dashboard must provide a complete interface for testing and operating the platform.

---

# Module 1 — Authentication

Pages:

* Login
* Forgot Password
* Reset Password

Features:

* JWT Authentication
* Role-Based Access Control

Roles:

* Super Admin
* Admin
* AI Engineer
* Developer
* QA Engineer

---

# Module 2 — Dashboard Overview

Landing page after login.

Display:

## System Metrics

Cards:

* Total Users
* Total Templates
* Total Fabric Render Jobs
* Total Try-On Jobs
* Total Generated Images
* Active Jobs
* Failed Jobs
* Average Generation Time

---

## AI Metrics

Display:

* Workflow 1 Success Rate
* Workflow 2 Success Rate
* Workflow 3 Success Rate
* GPU Utilization
* Queue Length
* Average Processing Time

---

## Storage Metrics

Display:

* Total Storage Used
* Number of Uploaded Images
* Generated Outputs Count

---

## Recent Activity Feed

Examples:

* Template created.
* Fabric render completed.
* Try-on completed.
* User login.
* Failed job.

---

# Module 3 — Workflow Testing Console

This is the most important module.

Provide separate testing pages for each workflow.

---

# Workflow 1 Testing

Garment Template Creation Testing

Features:

Upload:

* Front image
* Back image
* Side image

Actions:

* Create Template
* Re-run Analysis
* View Metadata
* View Segmentation Masks

Display:

* Uploaded images
* Generated masks
* Generated metadata
* AI description
* Template package JSON

Developer tools:

* Raw API request
* Raw API response
* Processing logs

---

# Workflow 2 Testing

Fabric Mapping Testing

Inputs:

* Select Template
* Upload Fabric Image

Actions:

* Generate Render
* Compare Versions

Outputs:

* Generated garment image
* Metadata
* Processing logs

Developer tools:

* Raw API request
* Raw API response
* Timing information

---

# Workflow 3 Testing

Virtual Try-On Testing

Inputs:

* Upload Customer Photo
* Select Rendered Garment

Actions:

* Generate Preview

Outputs:

* Final preview image
* Job details
* Processing time
* Status history

Developer tools:

* Request payload
* Response payload
* Logs

---

# Module 4 — Template Management

Features:

* View Templates
* Search Templates
* Filter Templates
* Edit Template Metadata
* Delete Template
* Reprocess Template

Table columns:

* Template ID
* Name
* Type
* Created By
* Created Date
* Status

Template detail page:

* Images
* Metadata
* Masks
* AI Description
* Processing History

---

# Module 5 — AI Job Management

Display all AI jobs.

Job types:

* Template Creation
* Fabric Render
* Try-On

Features:

* Search Jobs
* Filter Jobs
* Retry Failed Job
* Cancel Running Job
* View Logs

Columns:

* Job ID
* Workflow
* Status
* Created At
* Duration
* User

Statuses:

* Pending
* Running
* Completed
* Failed
* Cancelled

---

# Module 6 — Generated Assets Library

Display all generated files.

Categories:

* Customer Images
* Fabric Images
* Templates
* Rendered Garments
* Try-On Results

Features:

* Preview
* Download
* Delete
* Search
* Filter

Grid-based gallery UI.

---

# Module 7 — User Management

Features:

* Create User
* Edit User
* Disable User
* Assign Role
* Reset Password

Fields:

* Name
* Email
* Role
* Status
* Last Login

---

# Module 8 — Analytics

Provide charts and reports.

Charts:

## Usage Analytics

* Jobs per day
* Jobs per month
* Active users

## Workflow Analytics

* Success rate by workflow
* Average processing duration
* Failure trends

## Storage Analytics

* Storage growth
* Image generation trends

## User Analytics

* Most active users
* Most used templates

---

# Module 9 — Monitoring

Display real-time platform status.

Services:

* Gateway
* Auth Service
* Business Service
* Orchestrator
* Template Service
* Fabric Service
* Try-On Service
* PostgreSQL
* Redis
* MinIO

For each service display:

* Status
* Uptime
* Response Time
* Health Check

Status colors:

* Healthy
* Warning
* Down

---

# Module 10 — Logs Explorer

Centralized logs viewer.

Features:

* Search logs
* Filter by service
* Filter by severity

Severity:

* Info
* Warning
* Error

Display:

* Timestamp
* Service
* Message

---

# Module 11 — API Explorer

Interactive internal API testing tool.

Features:

* View Swagger documentation
* Execute API requests
* Inspect responses

Purpose:

Enable developers and QA teams to test APIs without external tools.

---

# UI Requirements

Design:

* Modern SaaS Admin Dashboard
* Dark/Light Mode
* Responsive Layout
* Sidebar Navigation
* Top Navigation Bar

Sidebar:

* Dashboard
* Workflow Testing
* Templates
* Jobs
* Assets
* Users
* Analytics
* Monitoring
* Logs
* API Explorer
* Settings

---

# Architecture

Create dashboard as a separate frontend application.

Repository:

admin-dashboard/

Structure:

src/

* app/
* components/
* modules/
* services/
* hooks/
* stores/
* layouts/
* types/
* utils/

Use API abstraction layer.

Do not directly access databases.

Communicate exclusively through backend APIs.

---

# Deliverables

Build a complete internal Admin Dashboard application with:

* Authentication
* Workflow Testing Console
* Monitoring
* Analytics
* Logs Viewer
* Asset Management
* User Management
* Template Management
* Job Management
* API Explorer

This dashboard will serve as the central control panel, QA interface, and operational console for the Textile AI Platform.
