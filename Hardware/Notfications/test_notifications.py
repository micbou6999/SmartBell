import unittest
import Notifications as NotificationClass


class MyTestCase(unittest.TestCase):
    notifications = NotificationClass.Notifications()

    def test_read_file(self):
        lines = self.notifications.read_file('test_file')
        for line in lines:
            line = line.rstrip()
        assert line == 'This is a test file.'


if __name__ == '__main__':
    unittest.main()
