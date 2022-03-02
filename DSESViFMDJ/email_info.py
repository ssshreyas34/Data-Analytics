import  os
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER ="djangodatainsights@gmail.com"
# EMAIL_HOST_PASSWORD ="Jeevan@123"
EMAIL_HOST_USER ="nagababuupputuri@gmail.com"
EMAIL_HOST_PASSWORD ="Jeevan$@1234"
EMAIL_PORT = 587
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER