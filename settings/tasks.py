import requests
from celery import shared_task

from .models import ZohoCredentials


@shared_task(bind=True)
def zohoTokenRefresh(self):
    try:
        # Fetch all ZohoCredentials objects
        zoho_credentials = ZohoCredentials.objects.all()
        # Loop through each ZohoCredentials object
        for credentials in zoho_credentials:
            # Construct the URL for token refresh
            refresh_url = f"https://accounts.zoho.in/oauth/v2/token?refresh_token={credentials.bearerToken}&client_id={credentials.clientId}&client_secret={credentials.clientSecret}&grant_type=refresh_token"
            # Send a POST request to refresh the token
            response = requests.post(refresh_url)
            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                access_token = data.get('access_token')
                # Update the ZohoCredentials object with the new access_token
                credentials.accessToken = access_token
                credentials.save()
                self.update_state(state='SUCCESS', meta=f'Refreshed token for ZohoCredentials with ID {credentials.id}')
            else:
                # Handle errors here if needed
                self.update_state(state='FAILURE', meta='Token refresh failed')
    except Exception as e:
        # Handle exceptions or errors here
        self.update_state(state='FAILURE', meta=str(e))

    return 'Token refresh completed'
