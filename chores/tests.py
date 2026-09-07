from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Chore, ChoreCompletion, Household, Membership


User = get_user_model()


class HouseholdModelTests(TestCase):
    def test_households_receive_unique_invitation_codes(self):
        first = Household.objects.create(name="Maple House")
        second = Household.objects.create(name="Oak House")

        self.assertTrue(first.invitation_code)
        self.assertNotEqual(first.invitation_code, second.invitation_code)

    def test_a_user_can_join_a_household_only_once(self):
        user = User.objects.create_user(username="sam", password="test-password")
        household = Household.objects.create(name="Maple House")
        Membership.objects.create(household=household, user=user)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Membership.objects.create(household=household, user=user)


class ChoreModelTests(TestCase):
    def setUp(self):
        self.household = Household.objects.create(name="Maple House")
        self.member = User.objects.create_user(
            username="member", password="test-password"
        )
        self.outsider = User.objects.create_user(
            username="outsider", password="test-password"
        )
        Membership.objects.create(household=self.household, user=self.member)

    def test_chore_can_be_left_unassigned_and_defaults_to_weekly(self):
        chore = Chore.objects.create(
            household=self.household,
            title="Take out recycling",
            due_date=date(2026, 9, 14),
        )

        self.assertIsNone(chore.assignee)
        self.assertEqual(chore.recurrence_days, 7)

    def test_chore_assignee_must_belong_to_the_household(self):
        chore = Chore(
            household=self.household,
            title="Clean kitchen",
            assignee=self.outsider,
            due_date=date(2026, 9, 14),
        )

        with self.assertRaises(ValidationError):
            chore.full_clean()

    def test_completion_records_a_household_member_and_scheduled_date(self):
        chore = Chore.objects.create(
            household=self.household,
            title="Vacuum living room",
            assignee=self.member,
            due_date=date(2026, 9, 14),
        )
        completion = ChoreCompletion.objects.create(
            chore=chore,
            completed_by=self.member,
            scheduled_for=chore.due_date,
        )

        self.assertEqual(chore.completions.get(), completion)
        self.assertIsNotNone(completion.completed_at)

    def test_completion_must_be_by_a_household_member(self):
        chore = Chore.objects.create(
            household=self.household,
            title="Mop floors",
            due_date=date(2026, 9, 14),
        )
        completion = ChoreCompletion(
            chore=chore,
            completed_by=self.outsider,
            scheduled_for=chore.due_date,
        )

        with self.assertRaises(ValidationError):
            completion.full_clean()
