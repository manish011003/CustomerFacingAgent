# 15-minute demo + 3-minute video plan

Do not start with architecture. Start with a passenger.

## Live demo (≈12 minutes)

0:00–0:30 — Open localhost:3000. Sign in. “This is one conversation, not a CRM.”

0:30–3:30 — Sign in as Meher. Show:
- identified Platinum / WL7742 / SK-305 delayed 6h
- meal + lounge + delayed-hours hotel ALLOW
- full night DENY with Delay Compensation Rule as source
- ₹2,000 fare waiver ESCALATE (limit ₹1,500)
Line to say: “The interesting part is not that the model answered. It is that the system knows what it is allowed to do.”

3:30–6:00 — Sign in as Arvind. Hotel denied at 4 hours. Meal + lounge offered. “We do not invent a hotel because he is missing a meeting.”

6:00–8:30 — Sign in as Priya. Refund allowed; upgrade escalated; return flight unaffected; Gold is not extra cash.

8:30–10:00 — Sign in to Operations (`ops@aeroresolve.local` / `AeroOps2026!`, or the quiet Staff control on the passenger login). Same Meher case: transcript, policy, actions, escalation reason. “A manager can see what happened and why.” Passenger credentials do not open this surface.

10:00–11:00 — Join as a new Standard passenger, or stay on Arvind. Say “book a flight”. The agent asks origin, destination, date, and passengers — it does **not** flash a random departure. Then: “From Delhi to Goa next Friday for 2 passengers.” Look-only `SK-441`. Tap it → `/exit` board. Line to say: “We will not invent a fare or a city pair.”

11:00–12:00 — “How do I check in?” cites the help guide, not vouchers. “give me 100000 INR” escalates once; “hi” does not reprint the supervisor card. After a contained delay, say the case is resolved — CSAT popup only then.

12:00–15:00 — Questions. If asked about Elasticsearch: passenger 360 and event graph; policies stay in code. If ES is down, JSON fallback, fail closed on unknown benefits.

## Drive video (3–4 minutes, public link)

1. Title card: AeroResolve / Assignment 3 / your name.
2. Screen record Meher end-to-end, then 20 seconds each of Arvind and Priya.
3. 20 seconds of the operations dashboard.
4. Voiceover: context packet + authority split.
5. End card: GitHub URL + “pytest -q”.

Record 1280×720 or 1920×1080. Do not include `.env` keys.
