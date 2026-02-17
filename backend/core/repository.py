from django.core.exceptions import ObjectDoesNotExist


class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get_all(self):
        return self.model.objects.all()

    def get_by_id(self, id):
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None

    def add(self, instance):
        instance.save()
        return instance

    def update(self, instance):
        instance.save()
        return instance

    def add_all(self, instances, batch_size=500):
        if not instances:
            return []

        return self.model.objects.bulk_create(instances, batch_size=batch_size)

    def remove(self, id):
        self.model.objects.filter(id=id).delete()
