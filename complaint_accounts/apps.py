from django.apps import AppConfig
class ComplaintAccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "complaint_accounts"
    def ready(self):
        import complaint_accounts.signals
