from __future__ import annotations

from django.db import migrations


def seed_telegram_sample(apps, schema_editor) -> None:
    Process = apps.get_model("n8n", "Process")
    Process.objects.get_or_create(
        kind="telegram_post",
        name="Telegram post via BotFather",
        defaults={
            "is_active": True,
            "settings_json": {
                "chat_id": "@example_channel",
                "message": "Hello from SEOPartnerHub via n8n!",
                "parse_mode": None,
                "disable_web_page_preview": False,
            },
                "webhook_path": "/seopartnerhub/telegram-post",
                "schedule_cron": "",
        },
    )


def remove_telegram_sample(apps, schema_editor) -> None:
    Process = apps.get_model("n8n", "Process")
    Process.objects.filter(
        kind="telegram_post",
        name="Telegram post via BotFather",
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("n8n", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_telegram_sample, remove_telegram_sample),
    ]
