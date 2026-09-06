# Next: scheduled GitHub Actions

Do not enable the cloud schedule until the converted scripts have completed one
successful local run against the existing Google Drive archive.

The intended schedule is:

```yaml
on:
  workflow_dispatch:
  schedule:
    - cron: "30 9 * * *"
      timezone: "America/New_York"
```

GitHub's current workflow syntax supports IANA time zones for scheduled
workflows, so `America/New_York` follows Eastern daylight/standard time.

The remaining cloud-specific piece is Google Drive authentication. The local
scripts deliberately do not embed credentials or service-account secrets.
