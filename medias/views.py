from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from .models import Photo
from django.conf import settings
import requests
import json


class PhotoDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Photo.objects.get(pk=pk)
        except Photo.DoesNotExist:
            raise NotFound

    def delete(self, request, pk):
        photo = self.get_object(pk)
        # if photo.room:
        #     if photo.room.owner != request.user:
        #         raise PermissionDenied
        # elif photo.experience:
        #     if photo.experience.host != request.user:
        #         raise PermissionDenied
        if (photo.room and photo.room.owner != request.user) or (
            photo.experience and photo.experience.host != request.user
        ):
            raise PermissionDenied
        photo.delete()
        return Response(status=HTTP_204_NO_CONTENT)


# curl --request POST \
# --url https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/images/v1 \
# --header 'Authorization: Bearer <API_TOKEN>' \
# --form 'url=https://[user:password@]example.com/<PATH_TO_IMAGE>' \
# --form 'metadata={"key":"value"}' \
# --form 'requireSignedURLs=false'


class GetUploadURL(APIView):
    def post(self, request):
        url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CLOUDFLARE_ID}/images/v2/direct_upload"
        one_time_url = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {settings.CLOUDFLARE_TOKEN}",
            },
        )
        one_time_url = one_time_url.json()
        result = one_time_url.get("result")
        return Response(result)
