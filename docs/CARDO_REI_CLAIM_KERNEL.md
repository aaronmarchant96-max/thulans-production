# CARDO REI Claim Kernel

Status: implemented foundation. This document describes the current code, not
future physics capability.

## Purpose

The claim kernel prevents a producer from authorizing its own result. A tool may
request `PASS_SCOPED`; `tools/cardo_claims.py` derives the effective verdict and
authorization from explicit proof obligations.

The governing sequence is:

`claim -> capability -> execution -> evidence + counterevidence -> provenance -> authorization`

Any missing link fails closed.

## Verdict states

- `UNIMPLEMENTED`: a required executable capability does not exist.
- `BLOCKED`: execution cannot begin because a declared prerequisite is absent.
- `NOT_RUN`: the capability exists but was not executed for this candidate.
- `ERROR`: execution ended without a valid measurement verdict.
- `FAIL`: executed evidence contradicts the predicate.
- `PASS_SCOPED`: all declared obligations are satisfied within the stated scope.
- `INVALIDATED`: a requested pass lacks required integrity or no longer binds to
  its candidate, source, parameters, or evidence.

`PASS_SCOPED` is the only authorizable state. It never means real-world safety,
manufacturability, visual approval, or any claim outside the recorded scope.

## Mandatory record content

Every canonical record contains:

- A stable claim ID and bounded scope.
- Declared capabilities and their implementation entry points.
- Proof obligations with predicates.
- Positive evidence and counterevidence references.
- Candidate path and SHA-256.
- Source revision and reproduction command.
- Known exclusions and unexecuted checks.
- A kernel-derived verdict, authorization boolean, and failure reasons.

The canonical schema identifier is `cardo-claim-1.0`.

## Enforcement

Run:

```bash
python -m unittest discover -s spec -v
python tools/audit_claim_records.py
```

The scanner fails CI for malformed canonical records. Existing evidence predates
the kernel and is inventoried as legacy rather than silently promoted. Migrate a
legacy record only when its producer and independent oracle can populate the
complete contract.

## Philosophical controls made mechanical

- **Feynman:** counterevidence and exclusions are mandatory.
- **Beer:** authorization follows observable execution, not declared intent.
- **Dijkstra:** unimplemented and unexecuted obligations fail closed.
- **Victor:** verdict reasons and dependency state are exposed in one record.
