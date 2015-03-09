# coding=utf-8
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

class MyUserManager(BaseUserManager):

    def _create_user(self, username, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        return self._create_user(username, email, password, True, True,
                                 **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    objects = MyUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('-date_joined', )
        db_table = "user"

    email = models.EmailField(_('email address'), max_length=100, blank=False, unique=True)

    username = models.CharField(_('username'), max_length=50, blank=True, default='')
    first_name = models.CharField(_('first name'), max_length=50, blank=True, default='')
    last_name = models.CharField(_('last name'), max_length=50, blank=True, default='')
    middle_name = models.CharField(_('middle_name'), max_length=50, blank=True, default='')

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now())

    birthday = models.DateField(_(u'День рождения'), blank=True, null=True)

    country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=True, null=True)
    city = models.CharField(_(u'Город'), max_length=50, blank=True)
    about = models.TextField(_(u'О себе'), max_length=1000, blank=True)
    gender = models.BooleanField(_(u'Пол'), blank=True, default=False)

    avatar_url = models.CharField(_('avatar url'), max_length=255, blank=True, default='')

    def __unicode__(self):
        return self.email

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        full_name = '%s %s %s' % (self.first_name, self.middle_name, self.last_name)
        return full_name.strip()


class Country(models.Model):
    class Meta:
        verbose_name = _(u'Страна')
        verbose_name_plural = _(u'Страны')
        ordering = ('name', )
        db_table = "country"

    name = models.CharField(max_length=100, verbose_name=u'Название')

    def __unicode__(self):
        return self.name


class Question(models.Model):
    class Meta:
        verbose_name = _(u'Вопрос')
        verbose_name_plural = _(u'Вопросы')
        ordering = ('-creation_date', )
        db_table = "question"

    text = models.TextField(_(u'Текст вопроса'), max_length=500, blank=True, default='')
    is_closed = models.BooleanField(_(u'Закрыт?'), default=False)
    creation_date = models.DateTimeField(_(u'Дата создания'), default=timezone.now())

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name="liked_questions")

    def __unicode__(self):
        return "Question #" + str(self.id) + " by " + self.author.email


class Comment(models.Model):
    class Meta:
        verbose_name = _(u'Комментарий')
        verbose_name_plural = _(u'Комментарии')
        db_table = "comment"

    text = models.TextField(_(u'Текст комментария'), max_length=1000, blank=True, default='')
    creation_date = models.DateTimeField(_(u'Дата создания'), default=timezone.now())

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name="liked_comments", through="CommentLike")

    def __unicode__(self):
        return "Comment #" + str(self.id) + " by " + self.author.email


class CommentLike(models.Model):
    class Meta:
        verbose_name = _(u'Лайк комментария')
        verbose_name_plural = _(u'Лайки комментариев')
        db_table = "comment_likes"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __unicode__(self):
        return "Like for comment #" + str(self.comment.id) + \
               ", question #" + str(self.question.id) + " by " + self.user.email


class Poll(models.Model):
    class Meta:
        verbose_name = _(u'Голосовалка')
        verbose_name_plural = _(u'Голосовалки')
        db_table = "poll"

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    items_count = models.SmallIntegerField(_(u'Количество вариантов'), default=0)

    def __unicode__(self):
        return "Poll for question #" + str(self.question.id)


class PollItem(models.Model):
    class Meta:
        verbose_name = _(u'Вариант голосовалки')
        verbose_name_plural = _(u'Варианты голосовалок')
        db_table = "poll_item"

    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(_(u'Текст варианта'), max_length=255, blank=True, default='')
    image_url = models.CharField(_(u'Ссылка на картинку'), max_length=255, blank=True, default='')
    votes_count = models.SmallIntegerField(_(u'Количество голосов'), default=0)
    votes = models.ManyToManyField(User, related_name="voted_poll_items", through="Vote")

    def __unicode__(self):
        return "Poll item for poll #" + str(self.poll.id) + " for question #" + str(self.question.id)


class Vote(models.Model):
    class Meta:
        verbose_name = _(u'Голос')
        verbose_name_plural = _(u'Голоса')
        db_table = "vote"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll_item = models.ForeignKey(PollItem, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)

    def __unicode__(self):
        return "Vote for poll item #" + str(self.poll_item.id) + \
               " for poll #" + str(self.poll.id) + " by user " + str(self.user.email)