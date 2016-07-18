from django.apps import AppConfig


class ContainerstorageConfig(AppConfig):
    name = 'containerstorage'

    def ready(self):
        import containerstorage.signals
