# RP-proj

# 📘 E-Learning Platform – Personalized Micro-Learning with Adaptive Content Structuring and Progress Analytics  
**Project ID:** 25-26J-233  

## 👥 Team Members  
| Name | Student ID | Role |
|------|-------------|------|
| **B. Iroshan** | IT22901262 | Education Content Extraction & Structuring Engine (ECESE) |
| **Ahamed M.N.A** | IT22243508 | Intelligent Learning Pathway Generator (ILPG) |
| **Weerasekara W.M.P.S** | IT22215406 | Progress Monitoring & Streak Analytics System (PMSAS) |
| **Ahmed M.N.A** | IT22920386 | Micro-Learning via Daily Challenges |

**Supervisor:** Mrs. Geethanjali Wimalaratne  
**Co-Supervisor:** Dr. Kapila Dissanayake  

---

## 🧩 Overview
This platform proposes a **teacher-supervised, AI-assisted e-learning ecosystem** that solves common issues in digital learning such as:  
- Generic content  
- Lack of personalization  
- No real-time motivation or analytics  
- No curriculum alignment  
- Limited teacher control  

The platform integrates four components:
1. **Education Content Extraction & Structuring Engine (ECESE)**
2. **Intelligent Learning Pathway Generator (ILPG)**
3. **Micro-Learning via Daily Challenges**
4. **Progress Monitoring & Streak Analytics System (PMSAS)**

---

## 🧠 1. Education Content Extraction & Structuring Engine (ECESE)

### Purpose  
Extracts, parses, and structures educational content from textbooks, teacher guides, and PDFs—fully aligned with curriculum requirements.

### Features  
- NLP-driven content extraction  
- Taxonomy & ontology-based curriculum mapping  
- Teacher validation dashboards  
- Structured output for downstream modules  

### Technologies  
- **NLP:** spaCy, NLTK, Hugging Face  
- **Parsing:** PDFBox, PyPDF2  
- **Backend:** Spring Boot / Node.js  
- **Frontend:** React.js / React Native  
- **Database:** MongoDB / Firebase / AWS S3  

### Evaluation  
- ≥ 90% curriculum alignment  
- Validation by teachers using official textbooks and guides  

---


## 📈 4. Progress Monitoring & Streak Analytics System (PMSAS)

### Purpose  
Tracks student engagement and progress using streaks, badges, awards, and predictive analytics.

### Features  
- Curriculum-linked streak engine  
- Predictive disengagement alerts  
- Teacher dashboard for interventions  
- Real-time analytics & visualizations  

### Technologies  
- **Frontend:** React.js / React Native  
- **Backend:** Node.js / Spring Boot  
- **Analytics:** Python (scikit-learn, pandas), D3.js  
- **Database:** MongoDB / Firebase / AWS S3  

### Evaluation  
- 20%+ improvement in engagement consistency  
- Metrics: **Avg streak length**, **drop-off reduction**, **intervention success rate**  

---

## 🏗️ System Architecture
- Microservice-based design  
- REST API integration between components  
- Secure cloud deployment (AWS / Firebase)  
- AES-256 encrypted data handling  
- Role-based user authentication  

---

## ⚙️ Non-Functional Requirements  
| Category | Requirement |
|-----------|--------------|
| *Performance* | < 2 sec response time |
| *Availability* | 99.9% uptime |
| *Security* | AES-256, HTTPS, RBAC |
| *Usability* | Mobile + Desktop compatibility |
| *Scalability* | Cloud-native microservices |

---

## 💡 Commercialization  
- SaaS platform for *schools, **tutoring centers, and **universities*  
- Subscription/licensing model  
- Unique selling point: *Curriculum-specific personalization + teacher oversight*  

---
📚 Micro-Learning via Daily Challenges

### Purpose  
Delivers daily, syllabus-aligned micro-learning tasks to improve engagement, retention, and habit formation.

### Features  
- Adaptive task scheduling  
- Teacher-approved micro-lessons  
- Motivation-aware reminders  
- Comparative analytics (micro vs clustered learning)  

### Technologies  
- *Frontend:* React.js / React Native  
- *Backend:* Spring Boot / Node.js  
- *Analytics:* D3.js, Matomo  
- *Database:* MongoDB / Firebase / AWS S3  

### Evaluation Metrics  
- Retention improvement  
- Streak continuation rate  
- Dropout reduction  

---
