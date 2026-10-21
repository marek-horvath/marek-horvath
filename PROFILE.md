# Profile maintenance

The profile uses Markdown and self-contained SVG images. There are no third-party statistics widgets, runtime scripts, externally loaded fonts, or required paid services. Dark/light and desktop/mobile images are selected with GitHub-supported `<picture>` sources. All substantive links and descriptions remain ordinary text if images are unavailable.

## Content and design sources

The read-only local portfolio supplied the professional identity, affiliation, location, completed PhD, experience, project descriptions, teaching background, and contact links. Specific sources were `src/components/PortfolioPage.vue` and the Work, Education, Projects, Publications, Teaching, and OtherActivities tabs. Its Fraunces/Plus Jakarta typography, navy `#10233d` and `#163a66`, blue `#2c5ea8`, ice `#eef6ff`, and connected-particle motif informed the design. SVGs use Georgia/Segoe UI fallbacks so they remain portable without font downloads. The tree motif is an illustration of source code structure, not a visualization of research results. Motion was deliberately omitted to keep reading calm and rendering predictable.

Public repository READMEs and file trees were inspected through GitHub's API on October 21, 2026. Research links were checked against [arXiv](https://arxiv.org/abs/2603.11150), [the publisher's ICPEC record](https://drops.dagstuhl.de/entities/document/10.4230/OASIcs.ICPEC.2024.4), [Crossref's ICETA record](https://api.crossref.org/works/10.1109/ICETA67772.2025.11280212), and [Zenodo](https://zenodo.org/records/18641274). The survey's published preprint title differs from the portfolio; the README uses the arXiv title and author order, and describes it as a preprint. A benchmark manuscript's acceptance status is not claimed because the repository and portfolio describe different stages.

## Recommended pins, in order

| Order | Repository | Reason |
| --- | --- | --- |
| 1 | [survey-extracting-script](https://github.com/marek-horvath/survey-extracting-script) | The clearest research identity: programmer attribution, a reusable Python analyzer, curated bibliography, and a permanently archived artifact. |
| 2 | [Benchmarking-LLM-assignements](https://github.com/marek-horvath/Benchmarking-LLM-assignements) | Research implementation with local-model grading, prompt templates, and evaluation outputs. Keep the repository's existing spelling in links. |
| 3 | [python](https://github.com/marek-horvath/python) | Substantial teaching material with bilingual course content, practical examples, and a published course website. |
| 4 | [algo](https://github.com/marek-horvath/algo) | Karel online: an interactive teaching tool whose code complements the course materials. A setup/usage README would strengthen this pin. |
| 5 | [cnk](https://github.com/marek-horvath/cnk) | A community application with Vue source, an API, and Docker setup; demonstrates practical delivery outside research. |
| 6 | [revik](https://github.com/marek-horvath/revik) | A real business website with Vue source and clear project documentation; demonstrates product/UI work. |

The remaining repositories were also reviewed. `git` is a useful training reference but overlaps teaching pins; `c-student-demo` is a small demonstration; `web` is a fork of BALab's website. `portfolio` and `skupina` expose deployed site output on their default `gh-pages` branches; their live websites are useful profile links, but the six recommendations above expose more implementation or research material. This profile repository does not need a pin because its README is already displayed on the profile. Athena is professionally relevant and featured in the README, but no corresponding public repository was found, so it is not a pin recommendation.

To set pins: open [your GitHub profile](https://github.com/marek-horvath), choose **Customize your pins** above the repositories, select the six repositories above, and save. Drag the pinned items into this order. Pinning is a manual GitHub profile operation; this project does not claim to change pins through an unsupported API.

## Profile metadata and photo

`profile.json` contains the verified display name, bio, website, affiliation, and location. `scripts/update_profile.py --apply` uses the authenticated GitHub CLI and the supported user/social-account REST endpoints, checks the account identity first, keeps a local ignored backup of the previous public values, preserves existing social links, and verifies the response. It adds the portfolio's LinkedIn and Google Scholar URLs. No unverified Twitter/X, ORCID, hiring status, or public-email setting is added. This script is intentionally manual and never runs in GitHub Actions.

To change the profile photo: open [Settings → Public profile](https://github.com/settings/profile), choose **Edit → Upload a photo** on your profile picture, select the portfolio's `src/assets/photo.jpg`, adjust the square crop so the face is centered, and save. The portfolio's `public/og-image.jpg` is another available image, but the original portrait is the better starting point. The supported profile metadata endpoint does not upload a profile photo. This project does not change it automatically.

## Regenerate and validate

Python 3.11 or newer is sufficient. No dependency installation is required.

```sh
python scripts/generate.py                 # Offline render from the saved public snapshot
python scripts/generate.py --refresh       # Refresh and render; keep dated data on API failure
python scripts/generate.py --refresh --require-fresh
python scripts/generate.py --check         # Reproducibility check; no writes or network
python -m unittest discover -s tests -v
python scripts/validate.py                 # Local references and SVG restrictions
python scripts/validate.py --links         # Also check external links
python scripts/update_profile.py           # Preview intended metadata, no mutation
python scripts/update_profile.py --apply   # Apply using your authenticated gh session
```

The optional `scripts/preview.py` requires Playwright and uses an installed Chrome browser to review GitHub-rendered Markdown at desktop/mobile sizes in both color schemes. Preview files go in the ignored `.preview/` directory and are not profile dependencies. The preview surrounds GitHub's rendered content with approximate GitHub styling; the deployed profile is checked separately. External link checks report access/rate-limit restrictions separately, including LinkedIn's nonstandard HTTP 999 response. Such responses do not independently confirm a link's destination.

## Automation and data boundaries

`.github/workflows/profile.yml` validates pushes and pull requests with read-only permissions. At 06:23 UTC daily, or via **Actions → Profile assets → Run workflow**, a separate job refreshes the snapshot with the repository's automatic `GITHUB_TOKEN` and commits only `assets/*.svg` and `data/activity.json`. The checkout action is pinned to a verified commit. No custom token or secret is required. The write job runs only for this repository's `main` branch on scheduled/manual events. Pushes from the bot do not create an update loop; no force push is used. A concurrent remote change causes a normal rejected push rather than overwriting work.

The only network source is `/users/marek-horvath/repos`, paginated at 100 repositories. Private, forked, archived, disabled, empty, differently owned, and profile repositories are excluded before saving. The snapshot stores only repository name, primary language, last push time, and a UTC retrieval date. It contains neither raw API responses nor private contribution data. Credentials stay in environment variables or GitHub CLI's credential store.

The activity image lists the six most recently pushed eligible repositories. Its bar is a push-recency indicator over 90 days, not a count of commits or contributions; an empty bar means the latest push was at least 90 days ago. Languages are GitHub's primary-language labels, not skill rankings. Refreshes occur at most daily by schedule. Requests use timeouts, bounded retries for transient errors, and fail quickly on permission/rate-limit responses. Failed refreshes preserve the previous assets and their original date. Live repository links remain available beside the snapshot.

If branch protection rejects the automatic commit, allow the workflow's bot under the repository's chosen policy or use manually reviewed refresh commits. If GitHub disables schedules after prolonged inactivity, re-enable this workflow in the Actions tab.
