#!/usr/bin/env python
import logging
import os
import sys

logging.basicConfig()

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "containerstorageservice.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
