# Competitive Research

How to research a hackathon without making things up.

## Sources, in order of authority
1. **Official rules / terms page.** This is binding. Rules here override everything else.
2. **Official event page / Devpost overview**: tracks, prizes, judging criteria, deadlines.
3. **Sponsor pages for the event**: prize requirements (for example "must use X API").
4. **Organizer announcements** (Discord, email, FAQ). Binding if the organizers posted them, but note the date, since they change.
5. **Past editions' winner galleries.** These show *patterns*, not requirements.
6. **Blog posts, social media, third-party write-ups.** Weak evidence. Use them only to form hypotheses.

## Tools (use whatever detect_environment found)
- Firecrawl: best for whole-site extraction (rules, FAQ and prize pages in one crawl).
- WebFetch / WebSearch: fine for individual pages.
- Browser (Playwright or a browser MCP): for pages that render with JavaScript or sit behind a login. Devpost galleries sometimes need it.
- `scripts/fetch_hackathon_docs.py`: fallback fetcher. It saves raw HTML and clean text to `research/raw/`. Network access can be restricted in some environments. If fetching fails, ask the user to paste or save the page and run the script on the file.
- `scripts/extract_submission_requirements.py`: a heuristic first pass. Always check its output against the source text.

## Citation rule
Every fact in `HACKATHON_BRIEF.md` gets a source: `(source: <url or file>, retrieved <date>)`. Anything you can't source is tagged `[UNVERIFIED]` and goes on the "Questions for organizers" list. Never fill a gap with what hackathons "usually" do. Put that in a separate "Typical (not confirmed for this event)" note.

## What to extract
- Deadline: date, time **and timezone**. Is there a separate code-freeze or video deadline?
- Eligibility: team size, student or pro status, location, whether pre-existing code is allowed (important!).
- Required deliverables: repo, video (max length?), Devpost fields, deployed URL, slides, live pitch slot.
- Judging criteria, weights, and the judging format: expo, stage pitch, async video?
- Tracks and prizes, and whether one project can enter several tracks.
- Sponsor requirements, per prize.
- Technology restrictions or requirements, licensing, open-source requirements.
- Disqualification conditions.

## Past-winner analysis
For 5–15 winners from past editions of this event (or similar events), record: problem domain, the "wow" moment, how deep the tech went, sponsor tech used, demo format and polish level. Then write **patterns** with their frequency ("6 of 9 winners had a live working demo, not slides"). Label this section *"Observed patterns — not official criteria."* Note survivorship bias: you only see the winners.

## Competitive landscape
Look at what other teams are probably building, given the theme and sponsors. The obvious idea for each sponsor API is crowded, so treat it as a differentiation warning. If the gallery for the current edition is public before the deadline, scan it ethically. Look at themes only, and never copy another team's work.

## Output: COMPETITIVE_ANALYSIS.md
Sections: Judging-format implications · Past-winner patterns (with counts) · Crowded idea zones · Open opportunity zones · Sponsor-prize opportunity map (prize value ÷ integration effort) · Sources.
