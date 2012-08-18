from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from oldmail.lib.gmail_imap import gmail_imap


class Account(models.Model):
    """docstring for Account"""
    name = models.CharField(max_length=500)
    slug = models.SlugField(unique=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    def profiles(self):
        return self.profile_set.all()

    def clients(self):
        return self.client_set.all()


class Client(models.Model):
    """docstring for Client"""
    name = models.CharField(max_length=500)
    account = models.ForeignKey('Account', editable=False)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    def contacts(self):
        return self.contact_set.all()

    def messages(self):
        return self.message_set.all()


class Profile(models.Model):
    """docstring for Profile"""
    account = models.ForeignKey('Account')
    user = models.OneToOneField(User, related_name="profile")
    is_verified = models.BooleanField(default=False)
    is_account_admin = models.BooleanField(default=False)
    oauth_token = models.CharField(max_length=100, blank=True)
    oauth_token_secret = models.CharField(max_length=100, blank=True)
    sync_label = models.CharField(max_length=100, default="@oldmail")

    def __unicode__(self):
        return self.user.get_full_name()

    def messages(self):
        return self.message_set.all()

    def get_messages(self, limit=10):
        gmail = gmail_imap(self.user.email,
                        self.oauth_token,
                        self.oauth_token_secret)
        gmail.messages.process(self.sync_label, limit)

        return gmail.messages


class Contact(models.Model):
    """docstring for Contact"""
    client = models.ForeignKey('Client', null=True)
    name = models.CharField(max_length=500)
    email = models.EmailField()
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    def messages(self):
        return self.message_set.all()


class Message(models.Model):
    """docstring for Message"""
    gmail_key = models.CharField(max_length=500)
    profile = models.ForeignKey('Profile')
    client = models.ForeignKey('Client')
    contact = models.ManyToManyField('Contact')
    message = models.TextField()
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.pk


class SignupLink(models.Model):
    """docstring for SignupLink"""
    random_string = models.TextField()
    account = models.ForeignKey('Account')
    email = models.EmailField()
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s' % self.pk

    def get_activate_url(self):
        return reverse('profile_activate', args=[self.account.slug, self.random_string])

    def get_verify_url(self):
        return reverse('profile_verify', args=[self.account.slug, self.random_string])
