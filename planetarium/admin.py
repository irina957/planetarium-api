from django.contrib import admin

from planetarium.models import (ShowTheme, AstronomyShow,
                                PlanetariumDome, ShowSession,
                                Reservation, Ticket)


class TicketInLine(admin.TabularInline):
    model = Ticket
    extra = 1
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    inlines = [TicketInLine,]


admin.site.register(ShowTheme)
admin.site.register(AstronomyShow)
admin.site.register(PlanetariumDome)
admin.site.register(ShowSession)
admin.site.register(Ticket)