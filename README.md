# CivicSense — AI-Powered Waste Verification  
## AWS Phase 2 Prototype

CivicSense is a Zero-UI, AI-powered first-mile waste verification system designed to improve waste segregation compliance in Indian communities. The system enables residents to submit waste images via WhatsApp, which are automatically verified using a strict multimodal AI inspector before pickup is scheduled. By combining advanced visual reasoning, seamless logistics orchestration, and bilingual context-aware feedback (English & Hindi), CivicSense reduces contamination in recycling streams and promotes responsible waste behavior at the source.

This repository contains the structured technical design, requirements, and implementation code for the **AI for Bharat Hackathon – Phase 2 Prototype (Track: AI for Communities, Access & Public Impact)**.

---

## 🚀 Phase 2 Objective

The goal of this phase was to deploy a functional AWS-native prototype within 7 days using a fully serverless architecture. The successfully deployed prototype validates:

- Multimodal AI-based waste image verification (Conservative Inspector approach)  
- Bilingual context-aware corrective feedback generation (English & Devanagari Hindi)  
- Seamless logistics orchestration (WhatsApp → AI → Driver Portal)  
- Real-time credit tracking and environmental impact analytics (Admin Dashboard)  
- High-performance observability and logging for evaluation  

---

## 🏗️ System Architecture (AWS Native)

CivicSense uses a serverless, event-driven architecture built entirely on AWS:

- **Amazon API Gateway** – Entry point for Twilio WhatsApp webhooks using a Greedy Proxy (`/{proxy+}`)  
- **AWS Lambda** – Core compute & orchestration layer (built with FastAPI and Mangum)  
- **Amazon Bedrock (Nova Pro)** – Advanced multimodal AI for strict waste segregation verification and bilingual reasoning  
- **Amazon DynamoDB** – State management for users, logistics (pickups), and Green Credits  
- **Amazon S3 (`civicsense-waste-images`)** – Permanent object storage for submitted waste images to ensure auditability  
- **Amazon S3 (Static Hosting)** – Hosts the web-based Driver Interface and Admin Dashboard  
- **Amazon CloudWatch** – Logging, timeout management, and system observability  

The system is privacy-first: minimal PII storage (phone numbers are masked on public dashboards), secure object storage, and highly scalable infrastructure.

---

## 📂 Repository Structure

- `requirements.md` — Functional and non-functional requirements  
- `design.md` — Detailed system design and AWS architecture  
- `README.md` — Project overview and execution timeline

---

## 📅 7-Day Execution Timeline

- **Day 1–2:** Core infrastructure setup (API Gateway, Lambda, S3, DynamoDB)  
- **Day 3–4:** Twilio WhatsApp Sandbox integration and FastAPI backend routing  
- **Day 5:** Amazon Bedrock (Nova Pro) integration for multimodal reasoning and strict prompt engineering  
- **Day 6:** Frontend UI development (Driver App & Admin Dashboard) and live DynamoDB wiring  
- **Day 7:** Bilingual support implementation (Hindi/English), S3 static hosting deployment, 30-second timeout optimization, and end-to-end testing
