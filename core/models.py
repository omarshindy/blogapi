from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """ User profile model with all the main user data  """

    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    bio = models.TextField(max_length=2000, null=True , blank=True)
    profile_picture = models.URLField(max_length=1000, null=True , blank=True)
    profile_picture
        
    def __str__(self):
        """ Show the username """
        return str(self.user)


@receiver(post_save,sender=User)
def create_profile(sender,instance,created,**kwargs):
    """ Create new profile for each new user """
    if created:
        Profile.objects.create(user=instance)