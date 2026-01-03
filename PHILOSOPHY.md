# Philosophy of PBM

## 1. Acceptance of Physical Noise

The physical world is messy. Lighting varies, lenses distort, and materials age. A robust protocol must accept this noise as a fundamental constraint, not an exception.

PBM does not seek perfect signal reconstruction. Instead, it seeks a "signal margin" sufficient to distinguish $d > 0$ (3D) from $d \approx 0$ (2D). We define a "Decodable State" where the signal-to-noise ratio (SNR) is sufficient for a deterministic decision. Outside this state, the system must return `UNDECIDABLE`, never a guess.

## 2. Determinism over Probability

Modern computer vision heavily relies on Machine Learning (ML), which is probabilistic. An ML model might conclude "99% probability this is a real object."

PBM rejects this approach. PBM is based on **Projective Geometry**, which is deterministic.
*   If layers are separated by distance $d$, and viewed at angle $\theta$, displacement $\Delta x$ **must** occur.
*   If $\Delta x$ does not occur, $d$ must be 0 (or $\theta$ is 0).

We prioritize algorithms with clear failure modes (e.g., FFT, Phase Correlation) over "black box" neural networks. A PBM decoder should be auditible.

## 3. Statelessness and Decentralization

A physical token lies in the user's hand. Its verification should not depend on:
*   A server in the cloud.
*   A blockchain transaction.
*   The previous state of the device.

Like a QR code, a PBM token simply *is*. It contains all necessary information for its own verification. This enables:
*   **Privacy**: Verification can happen offline.
*   **Resilience**: The system works when the internet is down.
*   **Longevity**: The token works 50 years from now, regardless of the creator's business status.

## 4. Normalization (The "DSNL" Approach)

Standardization requires normalization. QR codes use "finder patterns" to normalize perspective, rotation, and scale before decoding bits.

PBM mandates a **Deterministic Spatial Normalization Layer (DSNL)**. Before any parallax measurement is attempted, the input image must be geometrically warped to a canonical coordinate system (e.g., a unit square).
*   This removes dependence on camera distance and angle.
*   It simplifies the decoder, which only operates on the canonical space.

## 5. Simplicity vs. Intelligence

"Intelligence" in software often implies complexity and hidden assumptions. We prefer "Simplicity" in the Shannon sense—stripping away redundancy until only the core truth remains.

*   We do not try to "understand" the scene.
*   We only measure the specific frequency shift commanded by the protocol.
*   "Clever tricks" to compensate for bad tokens are rejected. If a token is bad, it should fail.

## 6. Open Standards > Proprietary Control

Security through obscurity is fragile. Proprietary security features (holograms, special inks) rely on the secrecy of the manufacturing process.

PBM relies on the **physics of parallax**. The security comes from the difficulty of presenting a properly aligned parallax field on a 2D display, not from a secret recipe. By opening the spec, we invite attack and analysis, which strengthens the protocol in the long run.

## 7. Identity is Born with Manufacturing

We reject the "Generation-First" approach where a digital ID is created in a database and then stamped onto a product. This creates a disconnect between the physical reality and the digital record.

In PBM:
1.  The product is made.
2.  The product is measured (Enrolled).
3.  The measurement (Physical Fingerprint) *becomes* the identity.

This ensures that the digital record is a derivative of the physical reality, not the other way around. The QR code is merely a vessel for this measurement, attached after the fact.
