import os
import time

from django.core.management.base import BaseCommand

from web.core.models import CCNewsRecord


class Command(BaseCommand):
    help = 'Ingest CC News Records into the DB'

    def get_filenames(self, dirs):
        idx_files = []
        for direc in dirs:
            for idx_file in os.listdir(direc):
                if idx_file.endswith(".idx"):
                    idx_files.append(os.path.join(direc, idx_file))
        return idx_files

    def get_records(self, filepath):
        records = []
        path_elems = filepath.split("/")
        year = path_elems[3]
        month = path_elems[4]
        filename = path_elems[5][:-4]
        with open(filepath, "r") as warc_idx:
            for line in warc_idx:
               uuid, offset = line.split()[0], line.split()[1]
               records.append(CCNewsRecord(record_id=uuid, year=year, month=month, filename=filename, offset=offset))
        return records, filename


    def handle(self, *args, **option):
        self.stdout.write(self.style.SUCCESS("Starting ingestion of CC News Records"))

        dirs = ["/cc/wet/2020/01", "/cc/wet/2020/02", "/cc/wet/2020/03"]
        idx_files = self.get_filenames(dirs)
        self.stdout.write(self.style.SUCCESS("Found {} files".format(len(idx_files))))

        total0 = time.time()
        record_cnt = 0
        for count, idx_file in enumerate(idx_files):
            records, filename = self.get_records(idx_file)
            record_cnt += len(records)
            self.stdout.write(self.style.SUCCESS("{} - Found {} records in {}".format(count, len(records), idx_file)))
            if CCNewsRecord.objects.filter(filename=filename).exists():
                self.stdout.write(self.style.SUCCESS("Skipping {} - records already exist".format(idx_file)))
                continue
            t0 = time.time()
            CCNewsRecord.objects.bulk_create(records)
            t1 = time.time()
            self.stdout.write(self.style.SUCCESS("Took {} to write".format(t1 - t0)))
        total1 = time.time()
        self.stdout.write(self.style.SUCCESS("Total time taken: {}".format(total1 - total0)))

        cnt = CCNewsRecord.objects.filter(month="04").count()
        self.stdout.write(self.style.SUCCESS("{} rows in DB, {} records in idx files".format(cnt, record_cnt)))

        self.stdout.write(self.style.SUCCESS(
            'Ingestion of all CC News Records completed')
        )


