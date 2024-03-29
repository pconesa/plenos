from django.contrib import admin

# Register your models here.

from .models import *

class VoteInline(admin.TabularInline):
    model = Vote

class VotingAdmin(admin.ModelAdmin):
    inlines = [
        VoteInline,
    ]

admin.site.register(Party)
admin.site.register(Town)
admin.site.register(Politician)
admin.site.register(Job)
admin.site.register(Charge)
admin.site.register(Meeting)
admin.site.register(Voting, VotingAdmin)
admin.site.register(Vote)
admin.site.register(Resource)
