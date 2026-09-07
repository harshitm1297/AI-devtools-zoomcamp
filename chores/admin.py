from django.contrib import admin

from .models import Chore, ChoreCompletion, Household, Membership


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ("name", "invitation_code", "created_at")
    search_fields = ("name", "invitation_code")


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "household", "joined_at")
    list_filter = ("household",)
    search_fields = ("user__username", "household__name")


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ("title", "household", "assignee", "due_date")
    list_filter = ("household", "due_date")
    search_fields = ("title",)


@admin.register(ChoreCompletion)
class ChoreCompletionAdmin(admin.ModelAdmin):
    list_display = ("chore", "completed_by", "scheduled_for", "completed_at")
    list_filter = ("chore__household",)
