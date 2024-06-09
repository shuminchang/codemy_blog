from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.utils.dateparse import parse_datetime

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not request.user.is_authenticated:
            return response
        
        try:
            # Get the last activity time from the session
            last_activity_str = request.session.get('last_activity')

            if last_activity_str:
                # Convert the string back to a datetime object
                last_activity = parse_datetime(last_activity_str)

                # Calculate the time elapsed since the last activity
                if last_activity:
                    elapsed_time = timezone.now() - last_activity
                    if elapsed_time > timedelta(seconds=settings.SESSION_COOKIE_AGE):
                        # Log out the user if they have been inactive for too long
                        from django.contrib.auth import logout
                        logout(request)
                        return response
        except KeyError:
            pass

        # Update the last activity time in the session
        request.session['last_activity'] = timezone.now().isoformat()

        return response