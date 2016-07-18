#!/usr/bin/env python
import logging
import os
import sys
import djcelery


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "containerstorageservice.settings")

    from django.core.management import execute_from_command_line
    logging.basicConfig(level=logging.INFO)
    djcelery.setup_loader()
    execute_from_command_line(sys.argv)
