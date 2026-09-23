# CyAN lake dashboard prepared for Vercel: per-lake files committed once, hosting note, 2026-09-23

## What the owner directed

The dashboard proves a concept and collects feedback. The repository is not updated afterward. The owner chose a one-time commit of the per-lake files and a hosting note, and asked to return afterward to the question of more years of pixel data within the storage limits.

## What changed

| Item | Detail |
|---|---|
| Ignore rules | The two rules that kept `docs/dashboards/*/data/lakes/` and `data/pixels/` out of git are removed. The review dashboard's frames stay ignored |
| Per-lake files | 4,642 files, 138,303,761 bytes, committed once: 2,321 series files and 2,321 pixel files with exact outlines, as built on 2026-09-23 by the step 1f builder |
| `docs/dashboards/cyan-lakes/vercel.json` | No framework, no install, no build, the folder as output. Mirrors the weather repository's file without its rewrite, because this page is `index.html` |
| [docs/vercel-hosting.md](../vercel-hosting.md) | What is deployed, the limits that apply with quotes and statuses, the owner's steps in Vercel, the checks, and the open items |
| README, CLAUDE.md, `.gitignore` comment | Say that the per-lake files are committed once for hosting and point to the note |

## Evidence

- Folder to deploy: 149 MB, 4,650 files, largest file 4.6 MB. `measured`
- Vercel's documented caps of 100 MB and 15,000 files apply to CLI uploads. No cap is documented for git deployments, `unverified` until the live deployment. Hobby includes 100 GB of transfer a month and is for non-commercial use. GitHub recommends repositories under 1 GB and blocks files over 100 MiB. Quotes and dates in the note.
- After this commit the repository holds about 160 MB.

## Checks

Ruff clean, ruff format clean, 148 tests pass, including the documentation link and date checks over the new note and this record.

## Limits

- The deployment itself is the owner's action in Vercel. This record cannot state the URL or confirm that Vercel accepts a 4,650-file git deployment.
- Committing a rebuild later adds about 140 MB to the history each time. The owner accepted this for a repository that is not updated.
- The imagery basemap streams from Esri under terms not yet checked for a public site.

## Authorization

The owner authorized the one-time commit, the hosting note, and their commit and push on 2026-09-23.

## Deployment

The owner imported the repository in Vercel on 2026-09-23 and reported that it deployed properly. The URL and the check results are not recorded here.

## Proposed next step

The owner records the deployment URL and the check results. Then the question of more years of pixel data: [measurement 11](../measurements.md#11-a-year-of-per-lake-pixel-images-what-it-costs-in-bytes-2026-09-23) gives 53 MB a year with the codes stacked per lake and colored in the browser, against GitHub's 1 GB guidance. Step 1g, the AWS note, follows.
