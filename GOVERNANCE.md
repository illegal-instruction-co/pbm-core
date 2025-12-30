# Governance of PBM

## 1. Decentralized by Design

PBM is designed to be a "commons" protocol. It belongs to no single entity. 
*   **No API Keys**: You do not need an account to use PBM.
*   **No Usage Fees**: There are no royalties for printing tokens or running decoders.
*   **No Central Server**: The verification logic runs entirely on the edge device.

## 2. Who Can Implement PBM?

**Anyone.**
*   You do not need permission to write a PBM decoder.
*   You do not need permission to print PBM tokens.
*   You can include PBM in commercial, open-source, or private software.

## 3. Compatibility Marking

We define "COMPATIBLE" implementations as those that:
1.  Correctly implement the DSNL normalization step.
2.  Adhere to the `UNDECIDABLE` safety rule (never guess).
3.  Can successfully decode standard reference tokens.

There is currently no formal certification body. Compatibility is established via community consensus and reference suites (to be developed).

## 4. RFC Culture

We follow the "Request For Comments" (RFC) model of the Internet Engineering Task Force (IETF).
*   Changes to the spec are proposed as RFCs.
*   Adoption is driven by rough consensus and running code.
*   "Simplicity" is a primary selection criterion for new features.

## 5. Trademarks

If a "PBM" trademark is ever registered, its sole purpose will be to prevent **misuse**, such as:
*   Companies claiming a proprietary, closed system is "PBM Standard".
*   Malicious actors distributing compromised decoders under the official name.
It will **not** be used to restrict legitimate usage or forks.
