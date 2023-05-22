import json
import pathlib

from django.core.management import BaseCommand

from mastf.MASTF import settings
from mastf.MASTF.models import FindingTemplate

class Command(BaseCommand):
    help = "Import new finding templates by loading JSON documents."

    def handle(self, *args, **options) -> str:
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
                amount = 0
                self.stdout.write("    Creating templates ... ", ending="")
                for template in templates:
                    if self.import_data(template):
                        amount += 1

                self.stdout.write(f"Ok ({amount} newly created)\n\n")
        except json.decoder.JSONDecodeError as err:
            self.stderr.write("  Could not import file: %s" % (str(err)))
            self.stderr.flush()

    def import_data(self, template_data: dict) -> bool:
        if not template_data.get("title", None):
            return False

        template_data["template_id"] = FindingTemplate.make_uuid()
        template_data["internal_id"] = FindingTemplate.make_internal_id(template_data["title"])

        queryset = FindingTemplate.objects.filter(internal_id=template_data["internal_id"])
        if queryset.exists():
            return False

        FindingTemplate.objects.create(**template_data)
        return True