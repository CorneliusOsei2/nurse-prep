#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Ensure only cards with A/B/C/D choices are tagged as application
python manage.py shell -c "
from cards.models import Card
Card.objects.filter(question_type='application').exclude(question__contains='\nA.').update(question_type='concept')
"
