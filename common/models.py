from django.db import models


# Create your models here.
class CommonModel(models.Model):
    """Common Model"""

    created_at = models.DateTimeField(auto_now_add=True)  # 처음 설정할때
    updated_at = models.DateTimeField(auto_now=True)  # 업데이트할때마다 설정

    # 위 2코드 재사용을 위해서 이 클래스를 호출해도 데이터베이스에 저장하지 않도록 하는 용도
    class Meta:
        abstract = True
