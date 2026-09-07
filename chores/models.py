"""Database models for shared households and their recurring chores."""

import secrets

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def generate_invitation_code():
    """Return a short code a new housemate can use to join a household."""
    return secrets.token_urlsafe(6).upper()


class Household(models.Model):
    name = models.CharField(max_length=100)
    invitation_code = models.CharField(
        max_length=16,
        unique=True,
        default=generate_invitation_code,
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Membership(models.Model):
    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="household_memberships",
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["household", "user"],
                name="unique_household_membership",
            )
        ]

    def __str__(self):
        return f"{self.user} in {self.household}"


class Chore(models.Model):
    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name="chores",
    )
    title = models.CharField(max_length=200)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_chores",
    )
    due_date = models.DateField()
    recurrence_days = models.PositiveSmallIntegerField(default=7, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date", "title"]

    def clean(self):
        super().clean()
        if self.assignee and not Membership.objects.filter(
            household=self.household,
            user=self.assignee,
        ).exists():
            raise ValidationError(
                {"assignee": "The assignee must be a member of this household."}
            )

    def __str__(self):
        return f"{self.title} ({self.household})"


class ChoreCompletion(models.Model):
    chore = models.ForeignKey(
        Chore,
        on_delete=models.PROTECT,
        related_name="completions",
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="completed_chores",
    )
    scheduled_for = models.DateField()
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at"]

    def clean(self):
        super().clean()
        if not Membership.objects.filter(
            household=self.chore.household,
            user=self.completed_by,
        ).exists():
            raise ValidationError(
                {"completed_by": "The completing user must be a household member."}
            )

    def __str__(self):
        return f"{self.chore.title} completed by {self.completed_by}"
