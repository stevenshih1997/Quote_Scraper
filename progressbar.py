"""Progress bar module"""
import sys

def progress(count, total, status=''):
    """Display a progressbar for running long operations in commandline"""
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    progress_bar = '#' * filled_len + '.' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s    %s\r' % (progress_bar, percents, '%', status))
    sys.stdout.flush()
