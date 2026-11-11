
import os
import re
import time
import logging
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils import timezone
from email_validator import validate_email, EmailNotValidError
from celery import shared_task

from .models import SearchJob, Lead

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
    )
}

EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)

PHONE_RE = re.compile(r"(\+?\d[\d\-\s()]{8,}\d)")

CONTACT_PATHS = [
    "/contact",
    "/contact-us",
    "/contact.html",
    "/about",
    "/about-us",
]

JUNK_EMAIL_PATTERNS = (
    "example.com",
    "sentry.io",
    "wixpress.com",
    "domain.com",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    "yourname@",
    "email@",
)


def search_tavily(query, max_results):

    api_key = (
        getattr(settings, "TAVILY_API_KEY", "")
        or os.getenv("TAVILY_API_KEY", "")
    )

    if not api_key:
        raise Exception("TAVILY_API_KEY is missing")

    response = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",
            "include_raw_content": True,
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    results = []

    for item in data.get("results", []):

        url = item.get("url")

        if url and url.startswith(("http://", "https://")):

            results.append({
                "url": url,
                "content": item.get("content", ""),
                "raw_content": item.get("raw_content", "") or "",
                "title": item.get("title", ""),
            })

    logger.info(
        "Tavily query returned %s results",
        len(results)
    )

    return results


def extract_contacts(html):

    soup = BeautifulSoup(html, "html.parser")

    emails = set(EMAIL_RE.findall(html))

    for link in soup.select('a[href^="mailto:"]'):

        email = link.get("href", "").replace(
            "mailto:", ""
        ).split("?")[0]

        if email:
            emails.add(email.strip())

    emails = {
        email.lower()
        for email in emails
        if not any(
            pattern in email.lower()
            for pattern in JUNK_EMAIL_PATTERNS
        )
    }

    phones = set(
        PHONE_RE.findall(soup.get_text(" "))
    )

    title = soup.find("title")

    company_name = (
        title.get_text(strip=True)[:255]
        if title else ""
    )

    return emails, phones, company_name


def check_email_valid(email):

    try:

        result = validate_email(
            email,
            check_deliverability=True
        )

        return True, result.normalized, ""

    except EmailNotValidError as exc:

        return False, email, str(exc)

    except Exception as exc:

        logger.warning(
            "Email validation problem: %s",
            exc
        )

        return False, email, str(exc)


def get_page_urls(base_url):

    urls = [base_url]

    parsed = urlparse(base_url)

    if parsed.scheme not in ("http", "https"):
        return urls

    for path in CONTACT_PATHS:

        urls.append(
            urljoin(base_url, path)
        )

    return list(dict.fromkeys(urls))


def fetch_page(url, timeout):

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout
        )

        response.raise_for_status()

        if "text/html" not in response.headers.get(
            "Content-Type", ""
        ):
            return ""

        return response.text

    except requests.RequestException as exc:

        logger.info(
            "Fetch failed %s: %s",
            url,
            exc
        )

        return ""


def save_lead(job, email, source_url, company_name, phone):

    is_valid, normalized, note = check_email_valid(email)

    lead, created = Lead.objects.get_or_create(
        job=job,
        email=normalized,
        source_url=source_url,
        defaults={
            "company_name": company_name,
            "phone": phone,
            "is_valid_email": is_valid,
            "validation_note": note,
        }
    )

    if created:

        logger.info(
            "Lead saved: %s | Valid: %s",
            normalized,
            is_valid
        )

    return created


@shared_task(bind=True)
def run_lead_search(self, job_id):

    job = SearchJob.objects.get(id=job_id)

    job.status = SearchJob.STATUS_RUNNING
    job.error_message = ""

    job.save(
        update_fields=["status", "error_message"]
    )

    max_results = getattr(
        settings,
        "LEADFINDER_MAX_RESULTS",
        15
    )

    fetch_timeout = getattr(
        settings,
        "LEADFINDER_FETCH_TIMEOUT",
        10
    )

    total_found = 0

    try:

        queries = [
            f"{job.topic} Bangladesh official website email contact",
            f"{job.topic} Bangladesh contact us email",
            f"{job.topic} Bangladesh phone address website",
        ]

        all_results = {}

        # STEP 1: Tavily search

        for query in queries:

            logger.info(
                "Searching Tavily: %s",
                query
            )

            results = search_tavily(
                query,
                max_results
            )

            for item in results:

                url = item["url"]

                if url not in all_results:
                    all_results[url] = item

        logger.info(
            "Total websites found: %s",
            len(all_results)
        )

        if not all_results:

            raise Exception(
                "Tavily returned no websites."
            )

        seen_emails = set()

        # STEP 2: Search result content

        for base_url, item in all_results.items():

            combined_content = (
                item.get("content", "")
                + " "
                + item.get("raw_content", "")
            )

            emails, phones, company_name = extract_contacts(
                combined_content
            )

            if not company_name:
                company_name = item.get("title", "")[:255]

            phone = next(iter(phones), "")

            for email in emails:

                if email in seen_emails:
                    continue

                seen_emails.add(email)

                if save_lead(
                    job,
                    email,
                    base_url,
                    company_name,
                    phone
                ):
                    total_found += 1

            # STEP 3: Visit website contact pages

            for page_url in get_page_urls(base_url):

                html = fetch_page(
                    page_url,
                    fetch_timeout
                )

                if not html:
                    continue

                emails, phones, company_name = extract_contacts(html)

                phone = next(iter(phones), "")

                for email in emails:

                    if email in seen_emails:
                        continue

                    seen_emails.add(email)

                    if save_lead(
                        job,
                        email,
                        base_url,
                        company_name,
                        phone
                    ):
                        total_found += 1

                time.sleep(0.3)

        # STEP 4: Complete job

        job.status = SearchJob.STATUS_DONE
        job.finished_at = timezone.now()

        job.save(
            update_fields=[
                "status",
                "finished_at"
            ]
        )

        logger.info(
            "Lead search completed. Total saved: %s",
            total_found
        )

    except Exception as exc:

        logger.exception(
            "Lead search failed for job %s",
            job_id
        )

        job.status = SearchJob.STATUS_FAILED
        job.error_message = str(exc)
        job.finished_at = timezone.now()

        job.save(
            update_fields=[
                "status",
                "error_message",
                "finished_at"
            ]
        )
