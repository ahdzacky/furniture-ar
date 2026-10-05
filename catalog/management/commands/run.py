import socket
from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand

class Command(RunserverCommand):
    help = 'Starts a lightweight Web server for development and outputs local network IP.'

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def handle(self, *args, **options):
        # By default, use 0.0.0.0 so it is accessible from the network
        if not options.get('addrport'):
            options['addrport'] = '0.0.0.0:8000'
        
        ip = self.get_local_ip()
        
        # Determine the port being used
        addrport = options.get('addrport')
        if ':' in addrport:
            port = addrport.split(':')[-1]
        else:
            port = '8000'

        self.stdout.write(self.style.SUCCESS('\n✨ Server is running! ✨'))
        self.stdout.write(self.style.SUCCESS(f'➜  Local:   http://127.0.0.1:{port}/'))
        self.stdout.write(self.style.SUCCESS(f'➜  Network: http://{ip}:{port}/ \n'))
        
        # Proceed with the original runserver logic
        options['insecure'] = True
        super().handle(*args, **options)
