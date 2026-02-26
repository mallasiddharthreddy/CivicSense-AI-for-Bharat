# CivicSense — AI-Powered Waste Verification  
## AWS Phase 2 Prototype

CivicSense is a Zero-UI, AI-powered first-mile waste verification system designed to improve waste segregation compliance in Indian communities. The system enables residents to submit waste images via WhatsApp, which are automatically verified using AI before pickup is scheduled. By combining computer vision, workflow orchestration, and contextual feedback generation, CivicSense reduces contamination in recycling streams and promotes responsible waste behavior at the source.

This repository contains the structured technical design and implementation plan for the **AI for Bharat Hackathon – Phase 2 Prototype (Track: AI for Communities, Access & Public Impact)**.

---

## 🚀 Phase 2 Objective

The goal of this phase is to deploy a functional AWS-native prototype within 7 days using a fully serverless architecture. The prototype will validate:

- AI-based waste image classification  
- Context-aware corrective feedback generation  
- Approval/rejection workflow automation  
- Credit tracking and pickup orchestration  
- Observability and logging for evaluation  

---

## 🏗️ System Architecture (AWS Native)

CivicSense uses a serverless, event-driven architecture built on AWS:

- **Amazon API Gateway** – Entry point for WhatsApp webhook integration  
- **AWS Lambda** – Core compute & orchestration layer  
- **Amazon Rekognition** – Waste image classification and quality verification  
- **Amazon Bedrock (Claude 3 Haiku)** – AI-generated contextual feedback  
- **AWS Step Functions** – Approval/rejection workflow orchestration  
- **Amazon DynamoDB** – User state, credits, and verification logs  
- **Amazon S3** – Temporary image storage (with lifecycle auto-deletion)  
- **Amazon CloudWatch** – Logging, monitoring, and observability  

The system is privacy-first: minimal PII storage, encrypted object storage, and automated image deletion post-verification.

---

## 📂 Repository Structure

- `requirements.md` — Functional and non-functional requirements  
- `design.md` — Detailed system design and AWS architecture  
- `README.md` — Project overview and execution plan  

This repository will be actively updated throughout the 7-day prototype build.

---

## 📅 7-Day Prototype Plan

- **Day 1–2:** Infrastructure setup (API Gateway, Lambda, S3, DynamoDB)  
- **Day 3–4:** Rekognition integration and classification validation  
- **Day 5:** Bedrock integration for feedback generation  
- **Day 6:** Workflow orchestration using Step Functions  
- **Day 7:** End-to-end testing, latency optimization, and logging setup  

