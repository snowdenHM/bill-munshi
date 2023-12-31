import requests
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ZohoCredentials


@receiver(post_save, sender=ZohoCredentials)
def createZohoAccessToken(sender, instance, **kwargs):
    zoho = instance
    url = "https://accounts.zoho.in/oauth/v2/token?grant_type=authorization_code&code=" + zoho.accessCode + "&client_id=" \
          + zoho.clientId + "&redirect_uri=" + zoho.redirectUrl + "&client_secret=" + zoho.clientSecret
    response = requests.request("POST", url)
    apiResponse = response.json()
    if "refresh_token" in apiResponse:
        zoho.accessToken = apiResponse["access_token"]
        refresh_token = apiResponse["refresh_token"]
        zoho.refreshToken = refresh_token
        zoho.save()
        # Get AccessToken
        url = "https://accounts.zoho.in/oauth/v2/token?refresh_token=" + refresh_token + "&client_id=" + zoho.clientId + \
              "&client_secret=" + zoho.clientSecret + "&grant_type=refresh_token"
        response = requests.request("POST", url)
        token = response.json()
        zoho.bearerToken = token['access_token']
        zoho.save()
        return "Done"
    else:
        print("Refresh Token not found in API response.")
        return "Error"
