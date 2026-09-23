# Smart Contact Portal v2 🌐

> **Cognifyz Tech Internship — Task 2: Inline Styles, Basic Interaction, and Server-Side Validation**

An advanced, production-ready full stack web application built using **Python, Flask, Jinja2, HTML5, Vanilla CSS3, and Inline Client-Side JavaScript**.

---

## 📌 Project Overview

**Smart Contact Portal v2** expands Task 1 with live client-side validation, password entropy meters, character counters, file upload thumbnail previews, extended profile fields, strict server-side verification, and an **Apple VisionOS / Raycast** inspired dark space glassmorphic design system.

---

## ✨ Features

- **Inline Client-Side Interaction Engine**:
  - **Live Email Check**: Real-time syntax verification.
  - **Password Strength Meter**: Dynamic entropy score bar.
  - **Password Match Indicator**: Instant password comparison.
  - **Live Character Counter**: Dynamic message length tracker (`0 / 500 characters`).
  - **File Drag & Drop Preview**: Instant thumbnail preview for profile avatar image uploads.
  - **Dynamic Submit Button Enabler**: Keeps the submit button disabled until terms are accepted and basic rules pass.
- **Extended Form Schema**: Full Name, Email, Phone, Password, Confirm Password, Date of Birth, Country Dropdown, Gender Selection, Message, Avatar Image Upload, Terms Checkbox.
- **Robust Flask Server-Side Validation**: Sanitizes data, checks file extensions (`PNG`, `JPG`, `WEBP`), enforces file size limits (5MB), and validates fields before persistence.
- **Temporary JSON Storage**: Persists validated entries to `data/submissions.json` (with `/tmp/data` serverless fallback).
- **VisionOS & Raycast Glassmorphism UI**: Abstract floating mesh canvas, glowing light ribbons, 22px glass cards, floating inputs, and Lucide vector icons.

---

## 📁 Folder Structure

```text
Task-02_Inline_Styles_Basic_Interaction_Server_Side_Validation/
│
├── app.py                  # Main Flask application & validation engine
├── requirements.txt        # Python dependency list
├── README.md               # Project documentation
├── vercel.json             # Vercel deployment configuration
├── .gitignore              # Git ignore rules
├── LICENSE                 # MIT License by Kavati John Shreyan
│
├── templates/              # Jinja2 HTML Templates
│   ├── base.html           # Layout with floating navbar & canvas
│   ├── index.html          # Extended contact form page
│   └── success.html        # Submission confirmation summary page
│
├── static/                 # Static Assets
│   ├── css/
│   │   └── style.css       # 2026 VisionOS & Raycast Glassmorphic Stylesheet
│   ├── js/
│   │   └── main.js         # Inline client validation & interaction script
│   └── uploads/            # Profile avatar image upload directory
│
└── data/                   # Data Storage
    └── submissions.json    # JSON storage for form submissions
```

---

## 🛠️ Routes

| Route | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Renders home page with interactive extended contact form |
| `/contact` | `POST` | Validates form & avatar upload, persists to JSON, redirects |
| `/success` | `GET` | Displays submission confirmation summary page |

---

## ⚙️ Installation & Local Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch Flask application
python app.py
```

Access the application in your browser at:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 📄 License

This project is licensed under the **MIT License** by **Kavati John Shreyan**.
Created as part of the Cognifyz Technologies Internship Program.
