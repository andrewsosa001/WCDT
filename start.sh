#!/bin/bash
uwsgi --socket 0.0.0.0:8000 --protocol=http -w wcdt:app --master
