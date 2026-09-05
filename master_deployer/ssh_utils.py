import socket
import paramiko


def run_ssh_command(ip, user, pwd, cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=user, password=pwd, timeout=5)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='ignore')
        err = stderr.read().decode('utf-8', errors='ignore')
        ssh.close()
        return True, out, err
    except Exception as e:
        return False, "", str(e)


def test_connection(ip, user, pwd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=user, password=pwd, timeout=6)
        ssh.close()
        return True, None
    except paramiko.AuthenticationException:
        return False, "AUTH_FAILED"
    except (paramiko.SSHException, socket.timeout, socket.error, OSError) as e:
        return False, f"CONNECTION_ERROR: {e}"
    except Exception as e:
        return False, f"UNKNOWN_ERROR: {e}"
