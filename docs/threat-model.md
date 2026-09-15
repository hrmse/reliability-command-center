# Threat model

The control plane exposes no mutating tools, credentials or unrestricted shell.
Untrusted alerts/logs are data, not instructions. Redact secrets and personal
data before normalization; isolate model adapters from executors; bind approval
to one immutable decision; and audit every external execution separately.
