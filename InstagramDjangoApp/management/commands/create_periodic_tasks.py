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

        task_name = 'tasks.perform_instagram_tasks'  # Updated to reference the task in tasks.py

        # Schedule the task to start 30 minutes after the current time
        start_time = datetime.datetime.now() + datetime.timedelta(minutes=30)

        PeriodicTask.objects.update_or_create(
            name='Every 30 minutes Instagram Tasks',
            defaults={
                'task': task_name,
                'interval': schedule,
                'one_off': False,
                'start_time': start_time,
            }
        )

        self.stdout.write(self.style.SUCCESS('Periodic tasks created successfully'))
