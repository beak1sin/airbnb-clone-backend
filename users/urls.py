from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("sign-up", views.Users.as_view()),
    path("change-password", views.ChangePassword.as_view()),
    path("me", views.Me.as_view()),  # 공개프로필에 안걸릴라면 코드가 먼저와야함.
    path("log-in", views.Login.as_view()),  # 쿠키 로그인
    path("log-out", views.Logout.as_view()),
    path("@<str:username>", views.PublicUser.as_view()),  # 공개프로필
    path("token-login", obtain_auth_token),  # 토큰 로그인
    path("jwt-login", views.JWTLogin.as_view()),  # jwt 로그인
    path("github", views.GithubLogin.as_view()),
    path("kakao", views.KakaoLogin.as_view()),
    path("naver", views.NaverLogin.as_view()),
]
