# Security and Deployment Checklist

## Before local demonstration

- [ ] `python manage.py check` completes without errors.
- [ ] `python manage.py test` completes successfully.
- [ ] `python manage.py system_readiness` has no unresolved errors.
- [ ] A non-admin account cannot access staff/admin-only actions.
- [ ] Users cannot read another user's complaint or notifications.
- [ ] Mutating browser forms include CSRF tokens.
- [ ] Complaint attachments are validated and stored safely.
- [ ] PDF exports respect the user's complaint visibility scope.
- [ ] Secrets remain in `.env`, not in Git.

## Before production deployment

- [ ] Set `DEBUG=False`.
- [ ] Set a unique, high-entropy `SECRET_KEY`.
- [ ] Set `ALLOWED_HOSTS` to exact hostnames.
- [ ] Configure HTTPS and secure cookies at the deployment layer.
- [ ] Review `CSRF_TRUSTED_ORIGINS` for the exact HTTPS origin.
- [ ] Use a dedicated MySQL database account with least privilege.
- [ ] Use a dedicated MongoDB Atlas database user with least privilege.
- [ ] Restrict Atlas network access to known application egress IPs where possible.
- [ ] Never expose `MONGODB_URI`, passwords, or secret keys in logs.
- [ ] Set up backups and test restoration.
- [ ] Define log retention and monitor failed sync jobs.
- [ ] Configure a real scheduler/background worker if continuous cloud sync is required.
- [ ] Configure static-file collection and serving for the chosen host.
- [ ] Review file upload limits, MIME checks, and malware scanning needs.
- [ ] Add privacy/retention rules for complaints, user data, and attachments.
- [ ] Review dependencies and pin tested versions before deployment.

## Cloud sync acceptance test

1. Create a complaint while Atlas is unavailable.
2. Confirm the complaint remains saved in MySQL.
3. Confirm a SyncJob is queued after the write-path integration is installed.
4. Restore Atlas connectivity.
5. Run `python manage.py sync_cloud`.
6. Confirm the job becomes synced and a matching cloud document exists.
7. Re-run sync and confirm an existing cloud document is replaced rather than duplicated.
8. Simulate an outage and confirm failed jobs remain queued for retry.

## AI/ML acceptance test

- [ ] Train on representative labelled data.
- [ ] Check class distribution and per-class precision/recall, not accuracy alone.
- [ ] Verify predictions are reviewed by a person.
- [ ] Retrain the model in the same Python environment used by Django.
- [ ] Do not use sensitive complaint text in external datasets without authorization.
