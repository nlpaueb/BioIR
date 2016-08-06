import sys

def progress(i, total, suffix):
    sys.stdout.write('Progress: %d/%d %s completed.\r' % (i, total, suffix))
    sys.stdout.flush()