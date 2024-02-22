from unittest.mock import patch

from utils.lib_manager import *

# class LibraryManagerTest(unittest.TestCase):

#     @patch('src.utils.task_runner.TaskRunner')
#     def setUp(self, MockTaskRunner):
#         self.manager = LibraryManager(MockTaskRunner.return_value)
#         self.manager.__libraries = {}
#         self.manager.__favorite_list = set()
#         self.manager.instance = None

#     def test_create_library(self):
#         self.manager.create_library('test', 'test', 'test', False)
#         self.assertEqual(len(self.manager.__libraries), 1)

#     def test_create_library_switch_to(self):
#         self.manager.create_library('test', 'test', 'test', True)
#         self.assertEqual(len(self.manager.__libraries), 1)

#     def test_demolish_library(self):
#         self.manager.create_library('test', 'test', 'test', True)
#         self.manager.demolish_library()
#         self.assertEqual(len(self.manager.__libraries), 0)

#     def test_change_name(self):
#         self.manager.create_library('test', 'test', 'test', True)
#         self.manager.change_name('test')
#         self.assertEqual(self.manager.__libraries[self.manager.instance.uuid].name, 'test')
