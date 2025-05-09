#!/bin/sh

cd app/
PYTHONPATH="../:$PYTHONPATH" alembic "$@"
cd ..
