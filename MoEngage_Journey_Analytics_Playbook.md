# MoEngage Journey Analytics — On-Demand Playbook

A reference for pulling journey ("Flow") data out of MoEngage directly in Claude,
via your MoEngage MCP server (built on the MoEngage Data/Reporting APIs).

Use it by **pasting a prompt line into a Claude chat** where the MoEngage
connector is enabled. Claude calls the MCP tool, MoEngage returns the numbers.

---

## 0. One-time setup (the only real blocker)

The MoEngage connector is **installed in your org but must be enabled per-chat**.

1. In the chat, open the tools/connectors menu (near the message box).
2. Find **Moengage** → toggle it **on** for this chat.
3. Authenticate/authorize if prompted (uses your MoEngage API credentials —
   the DATA API key + APP ID / bearer, whatever your server was configured with).
4. Verify it's live — paste:

   > List the MoEngage tools you can call right now, and show me one journey/flow
   > so I know the connection works.

If Claude lists MoEngage tools and returns a journey, you're ready. If it says it
has no MoEngage tools, the toggle didn't take — re-check the connector settings.

> Note: exact tool names and parameters depend on how *your* MCP server wraps the
> MoEngage APIs. The prompts below are written in plain English on purpose —
> Claude maps them to whatever tools your server exposes. If a prompt fails,
> ask: *"What parameters does the MoEngage journey-stats tool require?"* and
> adjust.

---

## 1. Find the journey you care about

You need the **Journey / Flow ID** for most stat pulls.

> List all my MoEngage journeys (flows) with their IDs, status (active/paused),
> and start date. Sort by most recently active.

> Find the MoEngage journey whose name contains "<keyword>" and give me its ID.

Keep a short list of the IDs you query often (fill in as you go):

| Journey name | ID | Notes |
|---|---|---|
| | | |
| | | |

---

## 2. Journey performance (reach, conversion, drop-off)

Entry → stage-by-stage → conversion. This is the "is the journey working" view.

> For MoEngage journey <ID>, over the last 30 days, give me:
> total users entered, users at each node/stage, conversion count, and the
> drop-off between consecutive stages (both absolute and %). Return as a table.

> For journey <ID>, which single node has the biggest drop-off? Show the
> before/after user counts and the % lost there.

> Compare conversion rate for journey <ID> for **this** 7-day period vs the
> **prior** 7-day period. Flag whether it went up or down and by how much.

---

## 3. Channel / message stats (push, email, SMS, in-app)

Per message step: sent, delivered, opened, clicked, CTR, plus failures.

> For journey <ID>, break down each messaging node by channel and give me:
> sent, delivered, delivery rate, opens, open rate, clicks, CTR, and
> unsubscribes/bounces where available. One row per message node.

> For journey <ID>, which channel (push vs email vs SMS) has the best CTR
> over the last 14 days? Rank them.

> For the email node "<node name>" in journey <ID>, pull daily sends and open
> rate for the last 14 days so I can see the trend.

---

## 4. Cohort / segment export (the users behind the numbers)

Pull the actual users who hit — or dropped at — a stage, for deeper analysis.

> For journey <ID>, export the users who **entered but did not convert** in the
> last 30 days. Give me count first; then the user list with user ID, email,
> and the last node they reached. Cap at <N> rows if it's large.

> For journey <ID>, list the users who dropped off at node "<node name>".
> Include any attributes your API returns (last seen, city, segment).

> Take the drop-off users from journey <ID> at node "<node>" and summarize them:
> top cities, top device/platform, and any common attribute pattern.

> Save that export as a spreadsheet.   ← works if a Drive/xlsx connector is on

---

## 5. Trends over time (compare periods)

> For journey <ID>, give me week-over-week entries, conversions, and conversion
> rate for the last 6 weeks. Return a table and call out the trend direction.

> Plot conversion rate over the last 8 weeks for journey <ID>.
> (Ask for a chart/artifact if you want it visual.)

> Compare journeys <ID-A> and <ID-B> head-to-head on entries, conversion rate,
> and best-performing channel over the same 30-day window.

---

## 6. Handy combined pulls (paste-and-go)

**Weekly journey health check:**
> Give me a weekly health check on journey <ID>: entries, conversion rate,
> biggest drop-off node, and best/worst channel by CTR — vs the prior week.
> Short summary + one table.

**Portfolio snapshot across all journeys:**
> For every active MoEngage journey, give me a one-row summary: name, entries
> (30d), conversion rate, and best channel. Sort by entries descending.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| "I don't have MoEngage tools" | Connector off in this chat | Re-toggle it on (Section 0) |
| Auth / 401 errors | API key/APP ID expired or wrong scope | Re-authorize the connector; check the DATA API credentials your server uses |
| Empty stats but journey exists | Date range has no traffic, or journey just launched | Widen the date range; confirm the journey was live in that window |
| Missing open/click data | MoEngage only tracks those for channels with tracking enabled | Confirm click/open tracking is on for that campaign/channel |
| Export truncated | API row/page limits | Ask Claude to paginate, or narrow the segment |

---

## What MoEngage's Data/Reporting APIs generally cover

So you know what's realistic to ask for:

- **Journey / Flow stats** — entries, node-level reach, conversions.
- **Campaign info & stats** — per-message sent/delivered/open/click/CTR.
- **Segment / export APIs** — user lists for a segment or campaign audience.
- **Data exports** — bulk user & event exports (may be async — Claude may need to
  request an export job, then fetch when ready).

If you need something not in the list above (e.g. raw event-level streams),
that usually lives in your **data warehouse / S3 export**, not the reporting API —
tell me and we can point Claude at that source instead.
