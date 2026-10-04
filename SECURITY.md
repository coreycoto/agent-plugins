# Security reporting

Report suspected credential exposure or unsafe upload behavior privately to
the repository owner. Use GitHub's private vulnerability reporting when the
repository Security tab offers it; otherwise contact the owner privately
before sending details. Do not put secrets or exploit transcripts in public
issues, PRs, or workflow artifacts.

Include the reviewed revision, affected command, synthetic reproduction,
expected boundary, and observed result. Do not upload actual credentials to
demonstrate a finding. Plugin installation is distinct from authentication and
operational authorization; a skill never grants provider or production access.

Only a maintained, reviewed revision should be used for hosted source uploads.
The public-readiness release is being prepared; older revisions do not have
its staging safeguards. Historical diagnostics and Actions logs require an
exposure review before the repository becomes public.
