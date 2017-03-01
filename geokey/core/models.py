"""Core models."""

from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.postgres.fields import HStoreField

from geokey.core.signals import get_request

from .base import STATUS_ACTION, LOG_MODELS


class LoggerHistory(models.Model):
    """Store the event logs."""

    timestamp = models.DateTimeField(auto_now_add=True)
    user = HStoreField(null=True, blank=True)
    project = HStoreField(null=True, blank=True)
    usergroup = HStoreField(null=True, blank=True)
    category = HStoreField(null=True, blank=True)
    field = HStoreField(null=True, blank=True)
    location = HStoreField(null=True, blank=True)
    observation = HStoreField(null=True, blank=True)
    comment = HStoreField(null=True, blank=True)
    subset = HStoreField(null=True, blank=True)
    action = HStoreField(null=True, blank=True)
    historical = HStoreField(null=True, blank=True)


def generate_log(sender, instance, action):
    """Generate a single log (without saving to DB)."""
    log = LoggerHistory(action=action)

    request = get_request()
    if hasattr(request, 'user'):
        log.user = {
            'id': str(request.user.id),
            'display_name': str(request.user),
        }

    fields = {}

    if sender.__name__ == 'Project':
        fields['project'] = instance
    elif sender.__name__ == 'Category':
        fields['project'] = instance.project
        fields['category'] = instance
    elif sender.__name__ == 'Subset':
        fields['project'] = instance.project
        fields['subset'] = instance
    elif sender.__name__ == 'Location':
        fields['location'] = instance
    else:
        bases = [x.__name__ for x in sender.__bases__]

        if 'Field' in bases:
            fields['project'] = instance.category.project
            fields['category'] = instance.category
            fields['field'] = instance

    for field, value in fields.iteritems():
        value = {
            'id': str(value.id),
            'name': value.name,
        }

        # Fields for categories should also have type
        if field == 'field':
            value['type'] = sender.__name__

        setattr(log, field, value)

    return log


def cross_check_fields(new_instance, original_instance):
    """Check for changed fields between new and original instances."""
    changed_fields = []

    for field in LOG_MODELS.get(new_instance.__class__.__name__, {}):
        new_value = new_instance.__dict__.get(field)
        original_value = original_instance.__dict__.get(field)
        if new_value != original_value:
            action_id = STATUS_ACTION.updated

            # Store GeoJSON for geo. extent
            if field == 'geographic_extent' and new_value is not None:
                new_value = new_value.json

            # Action is "deleted" - nothing gets deleted, only status change
            if field == 'status' and new_value == 'deleted':
                action_id = STATUS_ACTION.deleted

            changed_fields.append({
                'id': action_id,
                'field': field,
                'value': str(new_value),
            })

    return changed_fields


@receiver(pre_save)
def logs_on_pre_save(sender, instance, *args, **kwargs):
    """Initiate logs when instance get updated."""
    if LOG_MODELS.has_key(sender.__name__):
        logs = []

        try:
            original_instance = sender.objects.get(pk=instance.pk)
            for field in cross_check_fields(instance, original_instance):
                logs.append(generate_log(sender, instance, field))
        except sender.DoesNotExist:
            pass

        instance._logs = logs


@receiver(post_save)
def log_on_post_save(sender, instance, created, *args, **kwargs):
    """Finalise initiated logs or create a new one when instance is created."""
    if LOG_MODELS.has_key(sender.__name__):
        logs = []

        if created:
            logs.append(generate_log(
                sender,
                instance,
                {'id': STATUS_ACTION.created}))
        elif hasattr(instance, '_logs') and instance._logs is not None:
            logs = instance._logs

        try:
            historical = {
                'class': instance.history.__class__.__name__,
                'id': str(instance.history.latest('pk').pk),
            }
        # TODO: Except when history model object does not exist
        except:
            historical = None

        for log in logs:
            log.historical = historical
            log.save()


@receiver(post_delete)
def log_on_post_delete(sender, instance, *args, **kwargs):
    """Create a log when instance is deleted."""
    if LOG_MODELS.has_key(sender.__name__):
        log = generate_log(
            sender,
            instance,
            {'id': STATUS_ACTION.deleted})
        log.save()
