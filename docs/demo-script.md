# 15-minute demo + 3-minute video plan

Do not start with architecture. Start with a passenger.

## Live demo (≈12 minutes)

0:00–0:30 — Open localhost:3000. Point at the prototype banner. “This is a resolution desk, not a chatbot wrapper.”

0:30–3:30 — **Meher chip**. Read her line aloud. Show:
- identified Platinum / WL7742 / SK-305 delayed 6h
- meal + lounge + delayed-hours hotel ALLOW
- full night DENY with Delay Compensation Rule as source
- ₹2,000 fare waiver ESCALATE (limit ₹1,500)
Line to say: “The interesting part is not that the model answered. It is that the system knows what it is allowed to do.”

3:30–6:00 — **Arvind chip**. Hotel denied at 4 hours. Meal + lounge offered. “We do not invent a hotel because he is missing a meeting.”

6:00–8:30 — **Priya chip**. Refund allowed; upgrade escalated; return flight unaffected; Gold is not extra cash.

8:30–10:30 — Open `/desk`. Same Meher case: packet, transcript, graph edges. Assess with a supervisor note. “Human backup does not start from zero.”

10:30–12:00 — Click **This turn’s context**. Retrieve vs compute vs forbid. Mention pytest: policy still passes with the LLM unplugged.

12:00–15:00 — Questions. If asked about Elasticsearch: passenger 360 and event graph; policies stay in code. If ES is down, JSON fallback, fail closed on unknown benefits.

## Drive video (3–4 minutes, public link)

1. Title card: AeroResolve / Assignment 3 / your name.
2. Screen record Meher end-to-end, then 20 seconds each of Arvind and Priya.
3. 20 seconds of manager desk.
4. Voiceover: context packet + authority split.
5. End card: GitHub URL + “pytest -q”.

Record 1280×720 or 1920×1080. Do not include `.env` keys.
