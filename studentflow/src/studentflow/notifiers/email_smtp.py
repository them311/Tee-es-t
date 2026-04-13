"""SMTP email notifier.

Uses the stdlib `smtplib` + `email.message` so we avoid pulling a heavy
SDK. Works with any SMTP provider: Gmail, Fastmail, OVH, SendGrid SMTP
relay, Brevo (ex-Sendinblue), Mailgun, Infomaniak, etc.

The SMTP call is synchronous, so we run it inside `asyncio.to_thread` to
keep the NotifierAgent loop non-blocking.
"""

from __future__ import annotations

import asyncio
import logging
import smtplib
import ssl
from email.message import EmailMessage

from ..models import Match, Offer, Student
from .base import NotificationChannel

log = logging.getLogger(__name__)


class EmailNotifier(NotificationChannel):
    name = "email"

    def __init__(
        self,
        *,
        host: str,
        port: int,
        username: str,
        password: str,
        from_addr: str,
        use_tls: bool = True,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.use_tls = use_tls

    async def send(self, *, match: Match, student: Student, offer: Offer) -> None:
        msg = self._build_message(match=match, student=student, offer=offer)
        await asyncio.to_thread(self._send_sync, msg)
        log.info(
            "EmailNotifier: sent match %s to %s (%s)",
            match.id,
            student.email,
            offer.title,
        )

    def _build_message(self, *, match: Match, student: Student, offer: Offer) -> EmailMessage:
        pct = round(match.score * 100)
        reasons_txt = "\n".join(f"  • {r}" for r in match.reasons) or "  (aucun détail)"

        subject = f"[StudentFlow] Nouveau match {pct}% — {offer.title or 'offre'}"
        body = (
            f"Salut {student.full_name or 'toi'},\n\n"
            f"On a un nouveau match pour toi sur StudentFlow :\n\n"
            f"  Titre      : {offer.title or '-'}\n"
            f"  Entreprise : {offer.company or '-'}\n"
            f"  Ville      : {offer.city or '-'}\n"
            f"  Score      : {pct}%\n\n"
            f"Pourquoi on pense que ça colle :\n{reasons_txt}\n\n"
            f"Voir l'offre : {offer.url or '(lien non fourni)'}\n\n"
            f"— StudentFlow\n"
            f"Pour ne plus recevoir ces alertes, réponds STOP.\n"
        )

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.from_addr
        msg["To"] = student.email
        msg.set_content(body)
        return msg

    def _send_sync(self, msg: EmailMessage) -> None:
        context = ssl.create_default_context()
        if self.use_tls:
            with smtplib.SMTP(self.host, self.port, timeout=15) as server:
                server.starttls(context=context)
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(msg)
        else:
            with smtplib.SMTP_SSL(self.host, self.port, context=context, timeout=15) as server:
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(msg)
