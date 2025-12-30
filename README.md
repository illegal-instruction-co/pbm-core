# PBM Authentication Protocol

## Overview

PBM (Parallax-Bit Mapping) is an open physical-digital standard for ensuring product authenticity.

**Core Invariant: Identity is born with manufacturing.**

The system operates on the principle that identity is not known before the product exists. Identity is extracted from the unique physical imperfections and properties of the manufactured object (the "Physical Fingerprint") and then bound to a digital record.

## Features

*   **Manufacturing-First Identity:** The system does not generate the token; it measures the manufactured token.
*   **Enrollment & Verification:** Two distinct tools for registering and checking products.
*   **Unclonable:** Resists photocopies, photos, and screen-based spoofing via PBM liveness checks.
*   **Open Standard:** No proprietary cloud servers required. Works offline.

## System Components

1.  **Enrollment Tool (`enroll.py`):**
    *   Captures the physical token.
    *   Validates liveness (3D structure).
    *   Extracts the physical fingerprint hash.
    *   Outputs the data for QR generation.

2.  **Verification Tool (`verify.py`):**
    *   Scans the QR code (Claimed Identity).
    *   Validates liveness.
    *   Re-extracts the physical fingerprint.
    *   Compares the Measured vs Claimed identity.

## Philosophy
See [PHILOSOPHY.md](PHILOSOPHY.md) for the design principles.
See [SPECIFICATION.md](SPECIFICATION.md) for technical details.

## Quick Start

### 1. Installation
 
 ```powershell
 # Create venv
 py -3.11 -m venv .venv
 .venv\Scripts\activate
 
 # Install dependencies
 pip install -r pbm_mvp/requirements.txt
 ```

### 2. Initialization (One-time Setup)

Generate the cryptographic keys for the Product Authority:

```powershell
    python pbm_mvp/keygen.py
```
This creates `private_key.pem` (keep secret!) and `public_key.pem` (distribute to verifiers).

### 3. Enroll a Product (Manufacturer)

```powershell
python pbm_mvp/enroll.py
```
1.  Place the product under the camera.
2.  Follow on-screen instructions to align and capture.
3.  The tool outputs a JSON block containing the **Signed Digital Passport**.
4.  Generate a QR code containing this exact JSON data.

### 4. Verify a Product (User)

```powershell
python pbm_mvp/verify.py
```
1.  **Scan QR:** Show the product's signed QR code to the camera.
2.  **Signature Check:** The tool validates the signature using `public_key.pem`.
3.  **Liveness & Physics:** If valid, it proceeds to check the physical product against the signed fingerprint.
4.  **Result:** "GENUINE" or "MISMATCH".

## Philosophy
See [PHILOSOPHY.md](PHILOSOPHY.md) for the design principles.
See [SPECIFICATION.md](SPECIFICATION.md) for technical details.
