from django.core.management.base import BaseCommand
import collection.models
from tqdm import tqdm
from lxml import etree


class Command(BaseCommand):
    help = "Load jobs into the from an EAD export from ArchiveSpace"

    def add_arguments(self, parser):
        parser.add_argument("ead", nargs="+", type=str)

    def handle(self, *args, **options):
        ead = etree.parse(options["ead"][0])
        ns = {"ead": "urn:isbn:1-931666-22-9"}
        negative_files = ead.xpath(
            ".//ead:archdesc[ead:did/ead:unitid=0000.0197]//ead:c[@level='file']", namespaces=ns
        )
        print(f"{len(negative_files)} negative files")
        for c in tqdm(negative_files):
            try:
                title = c.xpath(".//ead:unittitle", namespaces=ns)[0].text
                container = c.xpath(".//ead:container", namespaces=ns)[0].text
                try:
                    job = collection.models.Job.objects.get(job_code=container)
                    job.label = title
                    job.save()
                except:
                    job = collection.models.Job.objects.get(job_code=container[:-1])
                    job.label = title
                    job.save()
            except:
                continue
