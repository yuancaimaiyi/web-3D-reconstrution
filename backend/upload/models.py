from django.db import models
from authentication.models import User


def user_directory_path(instance, filename):
    # MEDIA_ROOT/images/user_<id>/<filename>
    return '{0}/{1}'.format(instance.dataset.dataset_path, filename)


class Dataset(models.Model):
    user = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE)
    dataset_path = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    images_count = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    comment = models.CharField(max_length=255, default="")

    def __str__(self):
        return '{0}: {1}'.format(self.user.username, self.dataset_path)


class Image(models.Model):
    dataset = models.ForeignKey(to=Dataset, null=False, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_directory_path)

    def __str__(self):
        return '{0}: {1}'.format(
            self.dataset.user.username,
            self.image.name,
        )
