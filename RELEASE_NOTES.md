# RELEASE NOTES
## Contains releases info

### v1.0.0 - 11092020:
- Added following features to the django application.
    - search
    - caching
    - throttling and rate limit
- Added test suite for testing above features.
- Added additional modules in requirement.txt
- Formatted in PEP8 Syntax style
- A basic Updation Script

#### Note:
- Have modified `get_identifier` function of tastypie/authentication.py, Inside that under Authentication class to validate user throttle in localhost, copy paste below code after installing depedencies.
```=python
    def get_identifier(self, request):
        """ 
        Provides a unique string identifier for the requestor.
        """
        user = request.headers.get("Authorization")
        if user:
            return user.split()[1].split(":")[0]
        else request.GET.get("username"):
            return request.GET.get("username", "ananonyms")
```
- Put the updation script (galactica/periodic.py) in a cron job and it will check and update models in specified periods.
