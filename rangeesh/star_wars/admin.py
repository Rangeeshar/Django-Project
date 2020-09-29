from django.contrib import admin

from star_wars.models import People, Species


@admin.register(People)
class PeopleAdmin(admin.ModelAdmin):
    pass


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    pass
