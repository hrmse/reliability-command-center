# Architecture and integration boundary

`reliability-command-center` is intentionally a planning component, not an
automation executor. It accepts a normalized incident JSON document, validates
each evidence field against a narrow schema and produces a deterministic record
with a `decision_id`. Prometheus textfile output exposes only decision state.

An integration can pass the JSON record to an incident-management system, but
must treat all alert, log and model output as untrusted input. A separate
executor is responsible for authenticating a human approval, verifying the
decision hash, enforcing a short expiry and using its own least-privileged
identity. This repository contains no such executor and no credentials.

The runbook command is presentation-only. It is a fixed inspection template,
not an instruction that the process runs.
