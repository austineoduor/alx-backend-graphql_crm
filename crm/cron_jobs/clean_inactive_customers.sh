#!/bin/bash

# Log file location
LOG_FILE="/tmp/customer_cleanup_log.txt"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Run Django shell command to delete inactive customers
DELETED_COUNT=$(python manage.py shell -c "
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer
cutoff = timezone.now() - timedelta(days=365)
to_delete = Customer.objects.filter(orders__isnull=True, created_at__lt=cutoff).distinct()
count = to_delete.count()
to_delete.delete()
print(count)
")

# Log the result
echo \"[$TIMESTAMP] Deleted customers: $DELETED_COUNT\" >> \"$LOG_FILE\"