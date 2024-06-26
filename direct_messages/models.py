from django.db import models
from common.models import CommonModel


# Create your models here.
class ChattingRoom(CommonModel):
    users = models.ManyToManyField(
        "users.User",
    )

    def __str__(self):
        return "Chatting Room"


class Message(CommonModel):
    text = models.TextField()
    user = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="direct_messages",
    )
    room = models.ForeignKey(
        "direct_messages.ChattingRoom",
        on_delete=models.CASCADE,
        related_name="direct_messages",
    )

    def __str__(self):
        return f"says: {self.text}"
