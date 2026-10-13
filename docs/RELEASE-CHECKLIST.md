# Publication checklist

This repository contains generic workflow instructions, deterministic utilities, and synthetic examples. Research parameters are provided at runtime and do not belong in reusable documentation.

Before publishing:

- Review every tracked file, example, filename, package field, repository description, and release note.
- Exclude client or employer identifiers, actual assignments, private source text, credentials, personal filesystem paths, and unpublished outputs.
- Check Git history as well as the current tree. A deletion commit does not remove old content from history.
- Build release archives from the reviewed Git tree, not the entire working directory.
- Inspect archive entries and verify the archive digest before uploading.

`python3 scripts/check_package.py` checks common structural leaks and non-example URLs in example files. Automated checks do not prove complete anonymization; contextual review remains necessary.

Validation scope: local tests check citation mapping and document generation. They do not execute a real research assignment or verify real-world claims. Source content rights must be assessed for each actual use.
