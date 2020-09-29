import json
import requests
import structlog
from lru import LruCache
from ratelimit import limits
from star_wars.models import People
from tastypie.resources import Resource
from tastypie.throttle import CacheThrottle
from ratelimit.exception import RateLimitException
from star_wars.api_resources.utils import APIResponse
from tastypie.authentication import ApiKeyAuthentication


logger = structlog.get_logger(__name__)
FIELDS = [
    "birth_year",
    "created",
    "edited",
    "name",
    "gender",
    "height",
    "mass",
    "eye_color",
]
AUTHENTICATION_PARAMS = ["api_key", "username"]


class PeopleResource(Resource):
    """
    Process API requests to fetch people related information.
    API endpoint: /api/v1/peoples/
    """

    def __init__(self):
        super().__init__(self)
        self.cache = LruCache(maxsize=15, expires=60, concurrent=True)

    class Meta:
        resource_name = "peoples"
        list_allowed_methods = ["get"]
        detail_allowed_methods = ["get"]
        throttle = CacheThrottle(throttle_at=100, timeframe=60)

    def _validate_and_parsedata(self, request):
        # authenticate and parse params
        data = {}
        authentication = ApiKeyAuthentication()
        valid = authentication.is_authenticated(request)
        if isinstance(valid, bool):
            params = request.GET
            for key, value in params.items():
                if key in AUTHENTICATION_PARAMS:  # skipping authentication params.
                    continue
                data[key] = value
            return True, data
        else:
            return False, str(valid)

    @limits(calls=10, period=60)
    def _make_swapi_call(self, url):
        try:
            response = requests.get(url)
            logger.info(
                "rqst_people_list",
                url=url,
                rqst_time_millis=round(response.elapsed.total_seconds() * 1e3, 2),
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            return {"Error": str(e)}

    def _check_local_storage(self, name, birth_y):
        response = People.objects.filter(name__icontains=name).filter(
            birth_year=birth_y
        )
        result = {}
        if response:
            resp = response.values()[0]
            resp.pop("id")  # Removing Id to maintain response format
            resp["created"] = resp["created"].isoformat()
            resp["edited"] = resp["edited"].isoformat()
            result["results"] = resp
            result["local"] = True
            logger.info("Served from local db")
            return result

        logger.info("Data not found in local db")
        return {}

    def _write_to_local(self, data):
        result, results = {}, {}
        # Filtering fields
        for item in FIELDS:
            result[item] = data.get(item)

        # Creating model object
        people_obj = People(
            birth_year=data.get("birth_year"),
            eye_color=data.get("eye_color"),
            gender="Undisclosed" if data.get("gender") == "n/a" else data.get("gender"),
            height=int(data.get("height", 0)),
            mass="0" if data.get("mass") == "unknown" else data.get("mass"),
            name=data.get("name"),
            created=data.get("created"),
        )

        try:
            people_obj.save()
            logger.info("Record Inserted successfully")
        except Exception as e:
            logger.info("Error while inserting: {}".format(e))

        results["results"] = result
        return results

    def get_list(self, request, **kwargs):
        response = {}
        self.throttle_check(request)
        self.log_throttled_access(request)
        valid, data = self._validate_and_parsedata(request)
        ispresent = lambda x: True if x in data.keys() else False
        if valid:
            if ispresent("name") and ispresent("birth_year"):
                cache_key = "{}-{}".format(data["name"], data["birth_year"])
                cache_data = self.cache.get(cache_key)
                if cache_data:
                    logger.info("serving from cache")
                    response = json.loads(cache_data)
                    response["local"] = True
                else:
                    response = self._check_local_storage(
                        data["name"], data["birth_year"]
                    )
                    if not response:
                        url = "https://swapi.dev/api/people/?search={}&limit=20".format(
                            data["name"]
                        )
                        try:
                            resp = self._make_swapi_call(url)
                        except RateLimitException:
                            return APIResponse.service_unavailable(
                                "Too many requests to external service"
                            )
                        # Creating empty result if recieved empty
                        if not resp.get("results"):
                            response = resp
                        else:
                            # Searching for birth year in records
                            for res in resp["results"]:
                                if res["birth_year"] == data["birth_year"]:
                                    response = res
                                    break
                        # Writing only if valid record found
                        if resp["results"]:
                            response = self._write_to_local(response)
                            logger.info("Served from end point")
                            response["local"] = False
                    logger.info("caching result")
                    self.cache[cache_key] = json.dumps(response)
                return APIResponse.ok(extend_dict=response)
            else:
                return APIResponse.bad_request(
                    "name and birth_year are required params"
                )
        else:
            return APIResponse.unauthorized(data)
