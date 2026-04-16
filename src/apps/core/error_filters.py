from django.views.debug import SafeExceptionReporterFilter

class GlobalSensitiveDataFilter(SafeExceptionReporterFilter):
    def get_post_parameters(self, request):
        if request is None:
            return {}
        
        # Get the default cleansed POST parameters
        cleansed_post = super().get_post_parameters(request).copy()
        
        # keyword list
        sensitive_keywords = ['ssn', 'fin_number', 'routing', 'bank_account', 'dl_number', 'password', 'dl_exp', 'dl_issued']
        
        for key in cleansed_post:
            # If any of our danger words are in the HTML input name, scrub it
            if any(keyword in key.lower() for keyword in sensitive_keywords):
                cleansed_post[key] = '[REDACTED BY GLOBAL FILTER]'
                
        return cleansed_post