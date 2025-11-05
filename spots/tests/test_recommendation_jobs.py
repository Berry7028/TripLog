from datetime import timedelta
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from spots.models import (
    RecommendationJobLog,
    RecommendationJobSetting,
    Spot,
    Tag,
    UserSpotInteraction,
)
from spots.services import (
    build_recommendation_tool_context,
    build_recommendation_tool_schema,
    get_or_create_job_setting,
    is_job_due,
    run_recommendation_for_user,
    store_recommendation_scores,
    update_last_run,
)


class RecommendationJobServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="jobs-user", password="pass12345")
        self.tag = Tag.objects.create(name="夜景")
        self.spot = Spot.objects.create(
            title="夜景スポット",
            description="とても綺麗な夜景",
            latitude=35.0,
            longitude=135.0,
            address="大阪府",
            created_by=self.user,
        )
        self.spot.tags.add(self.tag)
        self.interaction = UserSpotInteraction.objects.create(
            user=self.user,
            spot=self.spot,
            view_count=3,
            total_view_duration=timedelta(minutes=12),
        )

    def test_tool_schema_contains_expected_function(self):
        schema = build_recommendation_tool_schema()
        self.assertTrue(schema)
        self.assertEqual(schema[0]["function"]["name"], "store_user_recommendation_scores")

    def test_tool_context_includes_interactions(self):
        context = build_recommendation_tool_context(self.user, [self.interaction])
        self.assertEqual(context["user"]["id"], self.user.id)
        self.assertEqual(len(context["interactions"]), 1)
        self.assertEqual(context["interactions"][0]["spot_id"], self.spot.id)

    def test_store_recommendation_scores_creates_log(self):
        arguments = {
            "user_id": self.user.id,
            "schema_version": "1.0",
            "source": "api",
            "scores": [{"spot_id": self.spot.id, "score": 42.5, "reason": "人気"}],
        }
        log = store_recommendation_scores(arguments)
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.source, "api")
        self.assertEqual(log.scored_spot_ids, [self.spot.id])
        self.assertEqual(log.metadata["tool_payload"]["scores"][0]["reason"], "人気")

    def test_run_recommendation_for_user_creates_log(self):
        RecommendationJobLog.objects.all().delete()
        result = run_recommendation_for_user(self.user, triggered_by="admin")
        self.assertIsNotNone(result)
        self.assertGreaterEqual(len(result.scored_spot_ids), 1)
        self.assertEqual(RecommendationJobLog.objects.count(), 1)

    def test_run_recommendation_for_user_without_persist(self):
        RecommendationJobLog.objects.all().delete()
        result = run_recommendation_for_user(self.user, triggered_by="admin", persist_log=False)
        self.assertIsNotNone(result)
        self.assertEqual(RecommendationJobLog.objects.count(), 0)

    def test_is_job_due_respects_interval(self):
        setting = get_or_create_job_setting()
        setting.enabled = True
        setting.last_run_at = timezone.now() - timedelta(hours=40)
        setting.save()
        self.assertTrue(is_job_due(setting, now=timezone.now()))

        update_last_run(setting, now=timezone.now())
        setting.refresh_from_db()
        self.assertFalse(is_job_due(setting, now=timezone.now()))


class RunRecommendationJobsCommandTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="runner", password="pass12345")
        self.tag = Tag.objects.create(name="展望台")
        self.spot = Spot.objects.create(
            title="展望台スポット",
            description="眺めが良い",
            latitude=36.0,
            longitude=138.0,
            address="長野県",
            created_by=self.user,
        )
        self.spot.tags.add(self.tag)
        self.interaction = UserSpotInteraction.objects.create(
            user=self.user,
            spot=self.spot,
            view_count=2,
            total_view_duration=timedelta(minutes=8),
        )

    def test_command_skips_when_not_due(self):
        setting = get_or_create_job_setting()
        setting.enabled = True
        setting.last_run_at = timezone.now()
        setting.save()

        out = StringIO()
        call_command("run_recommendation_jobs", stdout=out)
        self.assertIn("スキップ", out.getvalue())

    def test_command_executes_with_force(self):
        RecommendationJobLog.objects.all().delete()
        out = StringIO()
        call_command("run_recommendation_jobs", "--force", stdout=out)
        self.assertIn("解析完了", out.getvalue())
        self.assertEqual(RecommendationJobLog.objects.count(), 1)

        setting = RecommendationJobSetting.objects.first()
        self.assertIsNotNone(setting.last_run_at)

    def test_command_dry_run(self):
        RecommendationJobLog.objects.all().delete()
        out = StringIO()
        call_command("run_recommendation_jobs", "--force", "--dry-run", stdout=out)
        self.assertIn("ツールコールプレビュー", out.getvalue())
        self.assertEqual(RecommendationJobLog.objects.count(), 0)

    def test_command_filters_user(self):
        RecommendationJobLog.objects.all().delete()
        out = StringIO()
        call_command(
            "run_recommendation_jobs", "--user-id", str(self.user.id), "--force", stdout=out
        )
        self.assertIn(self.user.username, out.getvalue())
        log = RecommendationJobLog.objects.latest("executed_at")
        self.assertEqual(log.triggered_by, RecommendationJobLog.TRIGGER_CLI)

    def test_command_prints_tool_schema(self):
        RecommendationJobLog.objects.all().delete()
        out = StringIO()
        call_command("run_recommendation_jobs", "--print-tool-schema", stdout=out)
        self.assertIn("store_user_recommendation_scores", out.getvalue())
