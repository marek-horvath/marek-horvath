# Profile maintenance

The README uses GitHub-supported HTML/Markdown, a self-contained animated SVG header, and four individually clickable SVG link buttons. It has dark/light and desktop/mobile variants, no runtime JavaScript, no external fonts, and no third-party widgets.

## Content and design sources

The read-only local portfolio supplied the professional identity, affiliation, location, experience, research interests, teaching background, and contact links. Sources were `src/components/PortfolioPage.vue` and its Work, Education, Projects, Publications, Teaching, and OtherActivities tabs. Its serif heading, navy/ice palette, and connected-particle motif informed the profile design. The SVGs use Georgia/Segoe UI fallbacks without downloading fonts.

The October 21, 2026 revision removes the introductory slogans, project showcase, and public repository activity display. Research presents the three journal articles first, followed by the survey with Diomidis Spinellis and the sole-author preprint. Titles, authors, and publication details were checked against these primary records:

- [arXiv:2603.11150 — survey with Emília Pietriková and Diomidis Spinellis](https://arxiv.org/abs/2603.11150)
- [arXiv:2607.07400 — sole-author code authorship study](https://arxiv.org/abs/2607.07400)
- [Acta Informatica Pragensia — personalized learning analytics](https://doi.org/10.18267/j.aip.283)
- [Acta Polytechnica Hungarica — AI grading benchmark](https://acta.uni-obuda.hu/Issue169.html), DOI [10.12700/APH.23.5.2026.5.11](https://doi.org/10.12700/APH.23.5.2026.5.11)
- [PeerJ Computer Science — programmer proficiency](https://doi.org/10.7717/peerj-cs.3981), with metadata confirmed through [Crossref](https://api.crossref.org/works/10.7717/peerj-cs.3981)

The journal articles are presented with their actual journal names and bibliographic details. Preprints are explicitly separate from published journal articles. No journal quartile is applied to a preprint.

## Animation and links

The header background smoothly fades through four colors in a continuous 16-second loop: navy, blue, violet, and teal in dark mode; ice blue, lavender, mint, and pale blue in light mode. SVG `animate` changes the full background fill with eased transitions and a matching first/last color, so the loop has no jump. Three signals also move through the decorative network using SVG `animateMotion`. The network does not encode measurements. There is no JavaScript, external media, CSS in the README, or changing claim about GitHub activity. The README's `<picture>` selects a separately generated still SVG when `prefers-reduced-motion: reduce` is enabled. This works even in browsers that do not propagate motion preferences into SVG image documents. SVG CSS additionally hides moving elements for direct SVG viewing. The complete static header remains visible.

Each contact button is a separate SVG image inside an ordinary link. This preserves four real click targets in GitHub's renderer. Alt text names each destination. The buttons wrap into two rows on narrow screens. Their SVGs carry icons, restrained borders, and theme-matched colors rather than relying on unsupported README button styling.

The old repository snapshot, activity graphics, network-fetching generator, and daily refresh/write job were removed with the activity section. The remaining workflow checks the assets with read-only permissions on pushes, pull requests, and manual runs. No token, API request, or scheduled commit is needed to animate the header.

## Regenerate and validate

Python 3.11 or newer is sufficient; the generator and normal validation require only the standard library.

```sh
python scripts/generate.py
python scripts/generate.py --check
python -m unittest discover -s tests -v
python scripts/validate.py
python scripts/validate.py --links
```

`scripts/preview.py` optionally uses Playwright and installed Chrome. It renders the README through GitHub's Markdown API, checks all four mobile/desktop and light/dark layouts, verifies movement in the embedded header, verifies that reduced-motion stops it, and checks SVG text bounds. Screenshots and temporary files stay in ignored `.preview/`. The preview's surrounding stylesheet approximates GitHub; the live profile is checked after deployment as well. Link checks separately report browser/access restrictions such as LinkedIn's nonstandard HTTP 999.

## Profile metadata and photo

`profile.json` records the verified display name, bio, portfolio URL, TUKE affiliation, and Košice location. `python scripts/update_profile.py` previews them; `python scripts/update_profile.py --apply` applies them with authenticated GitHub CLI user/social-account REST endpoints. The script checks the account identity, keeps an ignored local backup of previous public values, preserves existing social links, and verifies the result. It never runs in Actions and never stores credentials in the repository.

For a professional photo, open [Settings → Public profile](https://github.com/settings/profile), choose **Edit → Upload a photo** by the profile picture, and use the portfolio's `src/assets/photo.jpg`. Adjust the square crop to center the face and save. The supported profile metadata endpoint does not upload photos.

## Recommended pins

All 12 public repositories were reviewed during the original profile audit. The following six prioritize research implementations, teaching tools, and practical applications:

| Order | Repository | Reason |
| --- | --- | --- |
| 1 | [survey-extracting-script](https://github.com/marek-horvath/survey-extracting-script) | Programmer attribution research, Python analyzer, curated bibliography, and an archived artifact. |
| 2 | [Benchmarking-LLM-assignements](https://github.com/marek-horvath/Benchmarking-LLM-assignements) | Research implementation with local-model grading, prompts, and evaluation outputs. The existing repository spelling is preserved. |
| 3 | [python](https://github.com/marek-horvath/python) | Bilingual lectures, exercises, and a published university course website. |
| 4 | [algo](https://github.com/marek-horvath/algo) | Karel online: an interactive teaching tool. A setup/usage README would strengthen this pin. |
| 5 | [cnk](https://github.com/marek-horvath/cnk) | Vue community application, API, and Docker setup. |
| 6 | [revik](https://github.com/marek-horvath/revik) | A real business website with Vue source and project documentation. |

`git` overlaps the teaching pins, `c-student-demo` is a small demonstration, and `web` is a BALab website fork. `portfolio` and `skupina` expose deployed site output on their default `gh-pages` branches. Athena is relevant research/teaching work, but no corresponding public repository was found. This README already appears directly on the profile, so the profile repository does not need a pin.

To set the pins, open [your profile](https://github.com/marek-horvath), click **Customize your pins**, select these six, save, and drag them into this order. Pinning remains a manual GitHub profile operation.
