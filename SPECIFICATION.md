# PBM Specification (DRAFT 0.2)

## 1. Introduction
This document outlines the technical requirements for the Parallax-Bit Mapping (PBM) token and decoder. It is a work in progress and subject to change.

## 2. Terminology

*   **PBM Token**: The physical object consisting of multiple semi-transparent layers.
*   **Carrier**: The physical high-frequency pattern (grid, noise, or lattice) printed on layer surfaces.
*   **Spacer**: The transparent medium separating layers with thickness $d$.
*   **Parallax Field**: The vector field $(\Delta x, \Delta y)$ describing the relative displacement of Carrier A and Carrier B.
*   **DSNL (Deterministic Spatial Normalization Layer)**: The algorithm step that warps the observed token image to a canonical coordinate system.
*   **Physical Fingerprint**: A compact digital representation of the intrinsic physical properties of the token (e.g. precise grid angles, frequencies, and phase defects).

## 3. Physical Carrier Assumptions

To ensure compatibility, a PBM token must adhere to:
*   **Dimensions**: The active area should be square (aspect ratio $1:1 \pm 0.05$).
*   **Fiducials**: Must contain machine-readable corners or borders to facilitate DSNL.
*   **Layer Separation**: Distance $d$ must be sufficient to produce $>$1 pixel shift at varying view angles (recommended $d \ge 1.0$ mm).
*   **Frequencies**: Carrier spatial frequencies must be resolvable by standard commodity cameras (e.g., > 20 pixels per period in captured image).

## 4. Signal vs. Noise

The decoder must distinguish between:
*   **Signal**: The coherent, rigid-body shift of Layer B relative to Layer A.
*   **Noise**: Sensor noise, compression artifacts, and localized defects.

**Rule 4.1**: The decoder must operate in the frequency domain or use rigorously defined correlation methods. Ad-hoc pixel differencing is prohibited.

## 5. Mandatory Normalization (DSNL)

Implementation conformance requires:
1.  **Input**: Raw image.
2.  **Process**: Detect fiducials $\to$ Compute Homography $\to$ Warp to Canonical Space ($512 \times 512$ px, 8-bit grayscale).
3.  **Output**: All subsequent processing acts *only* on this normalized image.

## 6. Enrollment & Verification

### 6.1 Enrollment
The enrollment process must:
1.  Validate PBM liveness (`VALID_3D`).
2.  Aggregate feature vectors over $N$ frames to reduce noise.
3.  Output a `fingerprint_hash` that uniquely identifies the physical token instance.

### 6.2 Verification
The verification process must:
1.  Read the `claimed_hash` from the QR code.
2.  Validate PBM liveness locally (`VALID_3D`).
3.  Re-extract the `measured_hash`.
4.  Compare using a defined tolerance metric (e.g. Euclidean distance or cosine similarity).

## 7. Decision Logic

The core output of a PBM decoder is a tri-state classification:

1.  **UNDECIDABLE**:
    *   Fiducials not found.
    *   Image blur / SNR too low.
    *   Calculated shift is unstable (high variance over time).

2.  **INVALID_2D / FAKE**:
    *   SNR is high (clear image).
    *   Calculated shift magnitude $|\vec{v}| < \epsilon$ (where $\epsilon$ is the noise floor).
    *   Liveness check fails.

3.  **VALID_3D / GENUINE**:
    *   SNR is high.
    *   Calculated shift magnitude $|\vec{v}| > \epsilon$.
    *   Fingerprint matches the claimed identity.
