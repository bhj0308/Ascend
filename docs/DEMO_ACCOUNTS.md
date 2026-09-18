# Demo accounts

Created by `backend/scripts/seed.py` (local) or `backend/scripts/seed_render.sh` (live site).
Sign in at http://localhost:5173/login or https://ascend-web-irk7.onrender.com/login.

**Password for every account: `demo-pass-2026`.** It's public (it's in this repo), so treat these
as throwaway demo logins — see [Removing or securing the demo data](#removing-or-securing-the-demo-data).

## Start here

| I want to see… | Log in as | Go to |
|---|---|---|
| A founder reviewing applicants | `jihoon@example.com` | Browse Jobs → *Senior Backend Engineer* → View applicants |
| A contract waiting for a signature (talent side) | `yuna@example.com` | Contracts → *Frontend Engineer (React)* → Sign |
| Editing and sending a draft contract (KRW, Korea ⇄ Canada) | `daniel@example.com` | Contracts → *ML Engineer (Seoul-based)* |
| Payment records (ledger) | `grace@example.com` | Payments |
| Accepting or declining a mentorship request | `seojin@example.com` | Mentorships |
| An active mentorship + messages | `yuna@example.com` | Mentorships, Messages |
| The mentor directory | any account | Find a Mentor |

## Every account

| Email | Role | Name · city | What's in the account |
|---|---|---|---|
| `jihoon@example.com` | founder | Jihoon Park · Vancouver | **Jobs:** Senior Backend Engineer (Minseo — *interviewing*), Frontend Engineer (React) (Yuna — *offered*), Mobile Engineer (Flutter, contract) (Taeyang — *applied*). **Contract:** Yuna's full-time offer, *pending signature*. **Messages:** thread with Minseo about an interview. |
| `grace@example.com` | founder · mentor | Grace Choi · Toronto | **Jobs:** Full-stack Developer (Yuna — *rejected*, Seojin — *applied*), Part-time Data Analyst (Eunji — *hired*). **Contract:** Eunji's part-time contract, *signed*. **Payments:** to Eunji — CA$1,400 *pending*, CA$350 *cancelled*. **Messages:** thread with Yuna. Listed as a mentor. |
| `daniel@example.com` | founder | Daniel Lee · Toronto | **Jobs:** ML Engineer (Seoul-based) (Minseo — *reviewing*), DevOps Engineer (Hyunwoo — *reviewing*). **Contract:** Minseo, Korea engineer ⇄ Canadian company, KRW salary, *draft* (editable). **Payments:** CA$5,000 signing bonus to Minseo, *pending*. |
| `minseo@example.com` | engineer | Minseo Kang · Seoul | **Applications:** Senior Backend Engineer (*interviewing*), ML Engineer (*reviewing*). **Contract:** Daniel's draft (read-only until sent). **Payments:** incoming CA$5,000 from Daniel. **Mentorship:** with Sarah, *completed*. **Messages:** thread with Jihoon. |
| `yuna@example.com` | IEC worker | Yuna Oh · Vancouver | **Applications:** Frontend Engineer (React) (*offered*), Full-stack Developer (*rejected*). **Contract:** from Jihoon, *ready to sign*. **Mentorship:** Hyunwoo is her mentor, *active*. **Messages:** threads with Grace and Hyunwoo. |
| `hyunwoo@example.com` | engineer · mentor | Hyunwoo Shin · Toronto | **Application:** DevOps Engineer (*reviewing*). **Mentoring:** Yuna (*active*), declined Taeyang. **Messages:** thread with Yuna. |
| `seojin@example.com` | immigrant · mentor | Seojin Lim · Calgary | **Application:** Full-stack Developer (*applied*). **Mentoring:** request from Eunji *waiting for accept/decline*. **Messages:** from Eunji. |
| `eunji@example.com` | IEC worker | Eunji Moon · Toronto | **Application:** Part-time Data Analyst (*hired*). **Contract:** with Grace, *signed*. **Payments:** from Grace (1 pending, 1 cancelled). **Mentorship:** requested Seojin, *waiting*. **Messages:** thread with Seojin. |
| `taeyang@example.com` | engineer | Taeyang Kwon · Busan | **Application:** Mobile Engineer (Flutter, contract) (*applied*). **Mentorship:** request to Hyunwoo, *declined*. |
| `sarah@example.com` | engineer · mentor | Sarah Kim · Vancouver | **Mentoring:** Minseo, *completed*. Listed as a mentor. |

Mentors in the directory: Grace, Hyunwoo, Seojin, Sarah.

## Clicking things changes the data

Signing Yuna's contract, accepting Seojin's request, moving applicants, sending messages — all of
it is saved. To put everything back the way it was:

```bash
cd backend && python scripts/seed.py --reset    # local
backend/scripts/seed_render.sh --reset          # live site
```

`--reset` deletes only rows tied to the ten `@example.com` accounts, then recreates them.

## Removing or securing the demo data

Anyone who reads this repo can sign in as these accounts. Before real users rely on the site,
either:

- **Keep the demo but lock it:** change `PASSWORD` in `backend/scripts/seed.py`, **don't commit
  that change**, and run the seed with `--reset`, or
- **Remove it:** sign in as each account → Profile → Delete account. Deletion anonymizes rather
  than erases, so their jobs close and their records remain as "User #id" for counterparties.
