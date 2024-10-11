from django.contrib import admin
from .models import (
    Vizit,
    Prof,
    Report,
    ProfCollegianBodies,
    ProfMember,
    Awards,
    Vacation,
    SocialPartnershipAgreements,
)

# Регистрация моделей в админ-панели
admin.site.register(Vizit)
admin.site.register(Prof)
admin.site.register(Report)
admin.site.register(ProfCollegianBodies)
admin.site.register(ProfMember)
admin.site.register(Awards)
admin.site.register(Vacation)
admin.site.register(SocialPartnershipAgreements)