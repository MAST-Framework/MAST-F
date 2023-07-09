from __future__ import annotations

import json
import pathlib

from io import StringIO
from django.core.management import BaseCommand

from mastf.MASTF import settings
from mastf.MASTF.models import FindingTemplate


class Command(BaseCommand):
    help = "Import new finding templates by loading JSON documents."

    def __init__(self) -> None:
        super().__init__()
        self.updated = 0
        self.created = 0

    def handle(self, *args, **options) -> str:
        self.updated = 0
        self.created = 0
        json_files_dir = pathlib.Path(settings.MASTF_FT_DIR)
        self.stdout.write(f"Importing FindintTemplate objects from {json_files_dir}")

        for json_file in json_files_dir.glob("**/*.json"):
            self.handle_json_file(json_file)

    def handle_json_file(self, json_file: pathlib.Path) -> None:
        try:
            self.stdout.write(f"+ {json_file}")
            self.stdout.write("    Reading from file ... ", ending="")
            self.stdout.flush()

            with open(str(json_file), "rb") as docfp:
                data = json.load(docfp)
                self.stdout.write("Ok")

                templates = data.get("templates", [])
                self.stdout.write("    Iporting Templates ... ", ending="")
                for template in templates:
                    self.import_data(template)

                self.stdout.write(f"Ok ({self.created} newly created, {self.updated} updated)\n\n")
        except json.decoder.JSONDecodeError as err:
            self.stderr.write("  Could not import file: %s" % (str(err)))
            self.stderr.flush()

    def import_data(self, template_data: dict) -> None:
        if not template_data.get("title", None):
            return

        template_data["template_id"] = FindingTemplate.make_uuid()
        template_data["internal_id"] = FindingTemplate.make_internal_id(
            template_data["title"]
        )

        try:
            template = FindingTemplate.objects.get(internal_id=template_data["internal_id"])
            updated = False
            for key, value in template_data.items():
                if hasattr(template, key) and key not in ("template_id", "internal_id"):
                    t_value = getattr(template, key)
                    if t_value != value:
                        setattr(template, key, value)
                        updated = True

            if updated:
                self.updated += 1
                template.save()

        except (FindingTemplate.DoesNotExist, FindingTemplate.MultipleObjectsReturned):
            FindingTemplate.objects.create(**template_data)
            self.created += 1
