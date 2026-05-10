# Reply Classification

Use this to classify the latest inbound message in a selection thread. Read the entire thread for context, but classify on the latest inbound only. Confidence below `high` always becomes `manual_review`, never an action.

## Classes

### `positive`

A clear, unconditional yes to the campaign. The creator is keen and has not asked a question.

Examples:
- "yes please!"
- "I'm in"
- "would love to"
- "sounds great, send it through"
- "yep keen"

Action: send the brief-options message.

### `brief_picked`

The creator has named a specific brief option. May be a number, the brief title, or a brief URL pasted back. The thread already contains a brief-options message from us.

Examples:
- "option 1"
- "the slow morning one"
- "first one please"
- "https://www.notion.so/<brief-url>"

Action: re-confirm the picked brief is linked to this campaign, then click `Select creator` and `Accept this creator`. Update Notion `Status = Selected` with the chosen brief.

### `question`

The creator wants more information before committing. Includes deadline negotiation, address questions, format clarifications, or any "depends on…" reply.

Examples:
- "when does it need to be posted by?"
- "can it be next month?"
- "do you ship to NT?"
- "what's the gift?"
- "yes if the deadline is flexible"

Action: log `manual_review` with the question quoted. Do not auto-respond. The marketer answers personally.

### `negative`

A clear no. Includes hard declines and softened declines.

Examples:
- "thanks but no thanks"
- "I'll pass on this one"
- "not for me sorry"
- "I don't take gifted work currently"

Action: write Notion `Status = Declined` with reason `creator declined post-shortlist`. Do not send further messages on this thread.

### `ambiguous`

Cannot classify with high confidence. Emoji-only, off-topic, message body unparseable, or mixed signals.

Examples:
- "🌸"
- "haha thanks"
- "let me think"
- a reply that contains both "yes" and a question

Action: log `manual_review`.

## Rules

- A "yes" followed by a question in the same message is `question`, not `positive`.
- A reply that mentions a brief option but also asks a question is `question`, not `brief_picked`.
- An emoji thumbs-up or single positive emoji on its own is `ambiguous`, not `positive`. The creator may be reacting to a different message.
- If the latest inbound predates our latest outbound (we sent something after they replied), do not act on the inbound — the thread is already past it.
- Do not classify on tone alone. If the words don't carry a clear yes or no, default to `ambiguous`.
- Never auto-Select on `question`, `ambiguous`, or `negative`.

## Confidence

Mark a classification `high` only when:

- The latest inbound is the message being classified (not stale).
- The class signal is explicit, not inferred from emoji or punctuation.
- No competing signal exists in the same message.

Otherwise drop to `medium` or `low` and route to `manual_review`.
