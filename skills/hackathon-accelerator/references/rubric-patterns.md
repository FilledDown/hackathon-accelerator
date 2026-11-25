# Rubric Patterns

How to map official judging criteria onto the scorecard, plus what each common criterion really rewards.

## Mapping procedure
1. Copy the official criteria **verbatim** into `HACKATHON_BRIEF.md`, with weights if they're published.
2. If weights aren't published, treat the criteria as equal. Note "weights not published" and don't make up a weighting.
3. Map each official criterion onto the scorecard dimensions. One official criterion can feed several dimensions. Use the official names in `IDEA_SCORECARD.md`.
4. Default dimensions (used only when there is no rubric): rubric alignment 25, technical sophistication 20, originality 15, real-world impact 15, demo experience 15, sponsor integration 10.
5. If sponsor prizes have their own criteria, give each target prize its own mini-rubric.

## Scoring scale (use the same one everywhere)
- 1: absent or broken
- 3: present but generic; a judge would forget it
- 5: solid, clearly works, competent
- 7: strong; a judge would mention it in deliberation
- 9: exceptional; the thing the judges remember
- (10 is reserved. Don't use it for your own project.)

Score only `VERIFIED` features. Report two numbers: **current** (verified only) and **projected** (if the build plan completes).

## Common criteria and what they actually reward
| Criterion wording | Judges actually reward | Common trap |
|---|---|---|
| Technical complexity / difficulty | Hard problems solved *visibly*: a custom model pipeline, real-time sync, clever data work, and an explanation of why it was hard | Lots of libraries glued together; complexity the judge never sees |
| Innovation / creativity / originality | A new framing of the problem or an unexpected combination | "ChatGPT wrapper for X"; the obvious sponsor-API idea |
| Impact / usefulness | A specific user with a specific pain, ideally with evidence (quote, statistic, personal story) | "This could help millions" with no named user |
| Design / UX / polish | A coherent, intentional interface and a smooth flow on the demo path | A generic template; a broken mobile layout; no loading states |
| Completeness / functionality | The core journey works end to end, live | A broad feature list where half the features are mocks |
| Presentation / pitch | A clear problem → demo → why it matters, on time | Slides before the demo; jargon; running over time |
| Use of sponsor technology | The sponsor tech is *essential*: take it away and the product breaks | Bolted-on API call; sponsor logo slide |
| Business viability | A believable first user and go-to-market path | A TAM slide with no wedge |

## Red flags judges notice
- Claims that the demo doesn't show.
- "AI-powered" without saying what the model does or what happens when it fails.
- A pre-recorded demo presented as live (this can be a rules violation, so check).
- Pre-existing code that wasn't disclosed.
