from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import datetime

class Command(BaseCommand):
    help = 'Create periodic tasks for Celery'

    def handle(self, *args, **kwargs):
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=30,
            period=IntervalSchedule.MINUTES,
        )

        task_name = 'perform_instagram_tasks'

        PeriodicTask.objects.update_or_create(
            name='Every 30 minutes Instagram Tasks',
            defaults={
                'task': task_name,
                'interval': schedule,
                'one_off': False,
                'start_time': datetime.datetime.now(),
            }
        )

        self.stdout.write(self.style.SUCCESS('Periodic tasks created successfully'))
