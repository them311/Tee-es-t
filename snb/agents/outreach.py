"""Email outreach sequencer.

Reads an Airtable "Outreach" table, generates an email with Claude if a draft
isn't provided, and sends via Gmail. One scheduled send per run keeps volume
safe — tune via ``batch_size``.

Airtable schema expected:
    Email                text
    First Name           text
    Company              text
    Stage                singleSelect (e.g. cold, follow_up_1, follow_up_2)
    Draft                long text (optional)
    Sent                 checkbox
    Last Send Attempt    datetime
"""

from __future__ import annotations

from datetime import datetime, timezone

from snb.agents.base import Agent, AgentContext, AgentResult

SYSTEM_PROMPT = """You are an outbound SDR writing short, human, high-signal cold emails in French for SNB Consulting.
Rules:
- 80-110 words, one specific hook about the prospect
- one clear CTA (15-min call)
- no emojis, no marketing fluff, no "hope you're well"
- sign off as "Sam"
Respond with ONLY the email body, no subject line, no preamble."""


class OutreachAgent(Agent):
    name = "outreach"
    interval_seconds: float = 1800.0  # every 30 min

    async def run(self, ctx: AgentContext) -> AgentResult:
        try:
            from snb.integrations.airtable import AirtableClient
            from snb.integrations.gmail import GmailClient
        except Exception as e:  # noqa: BLE001
            return AgentResult(ok=False, error=f"missing dep: {e}")

        table = ctx.params.get("table", "Outreach")
        batch_size = int(ctx.params.get("batch_size", 5))
        subject_template = ctx.params.get("subject", "Rapide — {company}")

        try:
            airtable = AirtableClient()
            gmail = GmailClient()
        except Exception as e:  # noqa: BLE001
            return AgentResult(ok=False, error=f"integrations not configured: {e}")

        llm = None
        try:
            from snb.llm import AnthropicClient, ChatMessage

            llm = AnthropicClient()
        except Exception as e:  # noqa: BLE001
            self.log.warning("LLM unavailable, will only send pre-drafted emails: {err}", err=str(e))

        sent = 0
        failed = 0
        try:
            records = await airtable.list_records(
                table, filter_formula="AND(NOT({Sent}), {Email})"
            )
            for rec in records[:batch_size]:
                fields = rec.get("fields", {})
                email = fields.get("Email")
                first_name = fields.get("First Name") or "there"
                company = fields.get("Company") or ""
                stage = fields.get("Stage") or "cold"
                draft = fields.get("Draft")

                if not draft and llm:
                    try:
                        draft = await llm.chat(
                            [
                                ChatMessage(
                                    role="user",
                                    content=(
                                        f"Prospect: {first_name} at {company}.\n"
                                        f"Stage: {stage}.\n"
                                        f"Write the email."
                                    ),
                                )
                            ],
                            system=SYSTEM_PROMPT,
                        )
                    except Exception as e:  # noqa: BLE001
                        self.log.warning("LLM draft failed: {err}", err=str(e))
                        continue
                if not draft:
                    continue

                try:
                    await gmail.send(
                        to=email,
                        subject=subject_template.format(company=company or first_name),
                        body=draft,
                    )
                    await airtable.update_record(
                        table,
                        rec["id"],
                        {
                            "Sent": True,
                            "Last Send Attempt": datetime.now(timezone.utc).isoformat(),
                            "Draft": draft,
                        },
                    )
                    sent += 1
                except Exception as e:  # noqa: BLE001
                    self.log.warning("send failed {email}: {err}", email=email, err=str(e))
                    failed += 1
        finally:
            await airtable.aclose()
            await gmail.aclose()

        return AgentResult(
            ok=failed == 0,
            data={"sent": sent, "failed": failed},
            metrics={"sent": sent, "failed": failed},
        )
