# Security Policy

This project is an offline analysis package. It does not connect to Snowflake,
does not request credentials, and does not store account identifiers.

## Safe input rules

- Use exported, redacted query-history samples.
- Remove customer names, emails, tokens, URLs with secrets, and raw query text
  before committing fixtures.
- Prefer query hashes, warehouse names, owner roles, and coarse cost metrics.

## Reporting

Open a private security advisory or contact the maintainer if you find a
credential leak, unsafe deploy configuration, or input-handling issue.

