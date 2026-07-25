"""Collect Philippine higher-education institutions from CHED HEIDA."""

import argparse
import csv
import html
import math
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = "https://heida.ched.gov.ph/hei-directory"
PAGE_SIZE = 10

REGION_IDS = (
    19,
    14,
    17,
    13,
    18,
    1,
    2,
    3,
    4,
    9,
    5,
    6,
    7,
    8,
    10,
    11,
    12,
    16,
)


class ChedDirectoryParser(HTMLParser):
    def __init__(self):
        super().__init__()

        self.records = []
        self.in_row = False
        self.in_cell = False
        self.row_cells = []
        self.cell_parts = []

    def handle_starttag(
        self,
        tag,
        attrs,
    ):
        if tag == "tr":
            self.in_row = True
            self.row_cells = []

        elif tag == "td" and self.in_row:
            self.in_cell = True
            self.cell_parts = []

    def handle_data(
        self,
        data,
    ):
        if not self.in_cell:
            return

        text = " ".join(
            data.split()
        )

        if text:
            self.cell_parts.append(
                text
            )

    def handle_endtag(
        self,
        tag,
    ):
        if tag == "td" and self.in_cell:
            self.row_cells.append(
                self.cell_parts
            )

            self.in_cell = False
            self.cell_parts = []

        elif tag == "tr" and self.in_row:
            self._save_row()

            self.in_row = False
            self.row_cells = []

    def _save_row(self):
        if len(self.row_cells) < 4:
            return

        name_and_code = self.row_cells[0]

        if len(name_and_code) < 2:
            return

        school_name = name_and_code[0]
        official_code = name_and_code[-1]

        if not official_code:
            return

        institution_type = " ".join(
            self.row_cells[1]
        )

        sector = None

        if institution_type.lower().startswith(
            "private"
        ):
            sector = "Private"

        elif institution_type.lower().startswith(
            "public"
        ):
            sector = "Public"

        self.records.append(
            {
                "school_name": school_name,
                "official_school_code": official_code,
                "school_type": institution_type,
                "sector": sector,
                "address": " ".join(
                    self.row_cells[3]
                ),
            }
        )


def parse_ched_directory(
    html_text,
):
    parser = ChedDirectoryParser()
    parser.feed(html_text)

    return parser.records


def parse_region_name(
    html_text,
):
    decoded = html.unescape(
        html_text
    )

    match = re.search(
        (
            r"Comprehensive list of institutions in"
            r"\s*<span[^>]*>(.*?)</span>"
        ),
        decoded,
        flags=re.DOTALL,
    )

    if not match:
        return None

    return " ".join(
        re.sub(
            r"<[^>]+>",
            "",
            match.group(1),
        ).split()
    )


def parse_record_count(
    html_text,
):
    match = re.search(
        r"([\d,]+)\s+Records Found",
        html_text,
    )

    if not match:
        raise ValueError(
            "CHED record count was not found."
        )

    return int(
        match.group(1).replace(
            ",",
            "",
        )
    )


def fetch_page(
    region_id,
    page,
):
    query = ""

    if page > 1:
        query = "?" + urlencode(
            {
                "page": page,
            }
        )

    url = (
        f"{BASE_URL}/{region_id}"
        f"{query}"
    )

    request = Request(
        url,
        headers={
            "User-Agent": (
                "StudExEl/1.0 "
                "(Philippine school directory import)"
            ),
            "Accept": "text/html",
        },
    )

    with urlopen(
        request,
        timeout=30,
    ) as response:
        return response.read().decode(
            "utf-8"
        )


def collect_region(
    region_id,
    delay,
):
    first_page = fetch_page(
        region_id=region_id,
        page=1,
    )

    region_name = (
        parse_region_name(first_page)
        or f"CHED Region {region_id}"
    )

    record_count = parse_record_count(
        first_page
    )

    page_count = math.ceil(
        record_count / PAGE_SIZE
    )

    print(
        f"{region_name}: "
        f"{record_count} record(s), "
        f"{page_count} page(s)."
    )

    collected = []
    seen_records = set()

    for page in range(
        1,
        page_count + 1,
    ):
        if page == 1:
            page_html = first_page
        else:
            time.sleep(delay)

            page_html = fetch_page(
                region_id=region_id,
                page=page,
            )

        records = parse_ched_directory(
            page_html
        )

        if not records:
            raise RuntimeError(
                f"No institutions found on "
                f"region {region_id}, page {page}."
            )

        for record in records:
            official_code = record[
                "official_school_code"
            ]

            record_key = (
                official_code,
                record["school_name"].casefold(),
            )

            if record_key in seen_records:
                continue

            seen_records.add(
                record_key
            )

            record["directory_source"] = "CHED"
            record["region"] = region_name
            record["is_active"] = "true"

            collected.append(
                record
            )

        print(
            f"  Page {page}/{page_count}: "
            f"{len(records)} row(s)"
        )

    if len(collected) != record_count:
        raise RuntimeError(
            f"Expected {record_count} directory rows "
            f"but collected {len(collected)}."
        )

    return collected


def write_csv(
    output_path,
    records,
):
    fieldnames = (
        "school_name",
        "official_school_code",
        "short_name",
        "school_type",
        "sector",
        "region",
        "province",
        "city",
        "website",
        "address",
        "directory_source",
        "is_active",
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for record in records:
            writer.writerow(
                {
                    field: record.get(
                        field
                    )
                    for field in fieldnames
                }
            )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Download CHED HEIDA institutions "
            "for one Philippine region."
        )
    )

    parser.add_argument(
        "--region-id",
        type=int,
        required=True,
        choices=REGION_IDS,
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=0.35,
        help=(
            "Seconds to pause between page requests."
        ),
    )

    arguments = parser.parse_args()

    records = collect_region(
        region_id=arguments.region_id,
        delay=max(
            arguments.delay,
            0,
        ),
    )

    write_csv(
        output_path=arguments.output,
        records=records,
    )

    print(
        f"Wrote {len(records)} school(s) "
        f"to {arguments.output}."
    )


if __name__ == "__main__":
    main()
