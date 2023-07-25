import sys
import requests


class Notifications:
    def read_file(self, file_name):
        with open(file_name) as f:
            lines = f.readlines()
        return lines

    def create_arguments_dictionary(self, title, message):
        lines = self.read_file('user_list_for_notification')

        for line in lines:
            line = line.rstrip()

            user_field = line.split(';')[0]
            user_name = user_field.split('=')[1]

            token_field = line.split(';')[1]
            token_id = token_field.split('=')[1]

            push_arguments = dict()
            push_arguments['user'] = user_name
            push_arguments['token'] = token_id
            push_arguments['title'] = title
            push_arguments['message'] = message
            return push_arguments

    def send_notifications(self, title, message):
        push_arguments = self.create_arguments_dictionary(title, message)
        requests.post('https://api.pushover.net/1/messages.json', params=push_arguments)


def usage(program_name):
        print('USAGE: ', program_name, '<title> <message>')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        usage(sys.argv[0])
        sys.exit(1)

    notification_instance = Notifications()
    notification_instance.send_notifications(sys.argv[1], sys.argv[2])
