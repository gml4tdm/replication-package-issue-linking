import threading
import subprocess

from . import logs


class NullList:

    def append(self, item):
        pass


def run_process(args: list[str], *,
                stream_stdout=True,
                stream_stderr=True,
                capture_stdout=False,
                capture_stderr=False,
                error_handling='strict') -> tuple[str | None, str | None]:
    p = subprocess.Popen(args,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout_out = [] if capture_stdout else NullList()
    stderr_out = []
    t = threading.Thread(target=_output_streamer,
                         args=(
                             p,
                             stream_stdout,
                             stream_stderr,
                             args[0],
                             stdout_out,
                             stderr_out,
                             error_handling
                         )
    )
    t.start()
    t.join()        # Also waits for the process to finish
    if p.returncode != 0:
        logger = logs.get_logger(f'{args[0]}.STDERR')
        for line in stderr_out:
            logger.error(line.decode(errors=error_handling).strip())
        import time
        time.sleep(1)
        raise RuntimeError(f'Command {args!r} failed with code {p.returncode}')
    if capture_stdout:
        stdout = b'\n'.join(stdout_out).decode(errors=error_handling).strip()
    else:
        stdout = None
    if capture_stderr:
        stderr = b'\n'.join(stderr_out).decode(errors=error_handling).strip()
    else:
        stderr = None
    return stdout, stderr


def _output_streamer(p: subprocess.Popen,
                     stdout: bool,
                     stderr: bool,
                     process_name: str,
                     stdout_list,
                     stderr_list,
                     error_handling: str):
    logger = logs.get_logger(f'{process_name}.STDOUT')
    for line in iter(p.stdout.readline, b''):
        if stdout:
            logger.info(line.decode(errors=error_handling).strip())
        stdout_list.append(line)
    logger = logs.get_logger(f'{process_name}.STDERR')
    for line in iter(p.stderr.readline, b''):
        if stderr:
            logger.error(line.decode(errors=error_handling).strip())
        stderr_list.append(line)
    p.wait()
