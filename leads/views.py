import csv

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import TopicForm
from .models import SearchJob
from .tasks import run_lead_search


def index(request):
    if request.method == "POST":
        form = TopicForm(request.POST)
        if form.is_valid():
            job = SearchJob.objects.create(topic=form.cleaned_data["topic"])
            run_lead_search.delay(str(job.id))
            return redirect("leads:job_detail", job_id=job.id)
    else:
        form = TopicForm()

    recent_jobs = SearchJob.objects.all()[:10]
    return render(request, "leads/index.html", {"form": form, "recent_jobs": recent_jobs})


def job_detail(request, job_id):
    job = get_object_or_404(SearchJob, id=job_id)
    leads = job.leads.all()
    return render(request, "leads/job_detail.html", {"job": job, "leads": leads})


def export_csv(request, job_id):
    job = get_object_or_404(SearchJob, id=job_id)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="leads_{job.id}.csv"'

    writer = csv.writer(response)
    writer.writerow(["Company", "Email", "Valid Email", "Phone", "Source URL", "Found At"])
    for lead in job.leads.all():
        writer.writerow([
            lead.company_name,
            lead.email,
            "Yes" if lead.is_valid_email else "No",
            lead.phone,
            lead.source_url,
            lead.found_at,
        ])
    return response
