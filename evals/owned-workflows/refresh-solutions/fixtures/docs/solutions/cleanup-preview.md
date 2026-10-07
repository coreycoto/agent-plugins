# Cleanup preview

Context: engineers inspect the affected cache before approving cleanup.
Decision: preview must be nonmutating; destructive cleanup needs explicit authorization.
Command: python legacy_clean.py --preview
Rejected alternative: running cleanup first to discover its affected paths can destroy evidence.
Evidence: historical investigation only; current command has not been verified.
