import shutil

from django.test import TestCase
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
vue_project_path = os.path.join(BASE_DIR, "webfront")

virtual_vue_path = os.path.join(BASE_DIR, 'backend', 'virtual_vue_project', 'cyy', '12342234', 'webfront')
shutil.copytree(vue_project_path, virtual_vue_path)
