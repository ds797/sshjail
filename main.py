import subprocess
import select
import re

def extract(line):
    match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', line)
    ip = match.group(0)
    return ip

def block(ip):
    line = f'iptables -I sshjail -s {ip} -p tcp -j REJECT --reject-with tcp-reset'
    subprocess.run(line.split())

def load():
    try:
        with open('/var/db/sshjail/db') as file:
            for line in file.readlines():
                ip = extract(line)
                block(ip)
    except:
        with open('/var/db/sshjail/db', 'w') as file:
            pass

def read():
    # read logs
    process = subprocess.Popen(['/usr/bin/journalctl', '-afb', '-p', 'info', '-n1', '-t', 'sshd', '-o', 'cat'], env={'LANG': 'C'}, stdout=subprocess.PIPE)

    while True:
        ready, _, _ = select.select([process.stdout], [], [])
        for stream in ready:
            line = stream.readline().decode('utf-8')
            if line:
                if 'failed password' in line.lower():
                    with open('/var/db/sshjail/db', 'a') as file:
                        file.write(line)
                    ip = extract(line)
                    block(ip)
            else:
                break

load()
read()
