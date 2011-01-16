#!/bin/sh

trap "kill 0" SIGINT SIGTERM EXIT

echo "Starting web server"
python manage.py runserver > runserver.log 2>&1 &

echo "Starting selenium server"
java -jar automated_tests/selenium-server.jar > selenium-server.log 2>&1 &

echo "Backup up current data"
python manage.py dumpdata --indent=2 > pre-test.json

echo "Flushing database"
python manage.py flush --noinput

echo "Loading test fixtures"
python manage.py loaddata automated_tests/automated_fixtures.json


cd automated_tests

python suite.py


cd ..

echo "Resetting to previous data"
python manage.py loaddata pre-test.json 
