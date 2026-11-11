from django.contrib import admin

from .models import SearchJob, Lead


class LeadInline(admin.TabularInline):
    model = Lead
    extra = 0
    readonly_fields = ("email", "phone", "is_valid_email", "source_url", "found_at")


@admin.register(SearchJob)
class SearchJobAdmin(admin.ModelAdmin):
    list_display = ("topic", "status", "valid_lead_count", "total_lead_count", "created_at")
    readonly_fields = ("id", "created_at", "finished_at")
    inlines = [LeadInline]


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("email", "company_name", "is_valid_email", "job", "found_at")
    list_filter = ("is_valid_email",)
    search_fields = ("email", "company_name", "source_url")
