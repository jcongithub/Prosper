import re
import math
from optparse import OptionParser
import subprocess
from subprocess import check_call, PIPE, Popen
import shlex

def split_video(filename, chunk_duration, output_file_name='video'):
    #get video duration
    stdoutdata = subprocess.getoutput("ffmpeg -i " + filename)
    print("=================Video Info=======================")
    print(stdoutdata)

    duration_pattern = re.compile(".*Duration: (.*):(.*):(.*)\.(.*), start")
    match = duration_pattern.findall(stdoutdata)

    duration=0
    if match:
        m = match[0]
        duration = 3600*int(m[0]) + 60*int(m[1]) + int(m[2]) + 1
        print('video duration:{}'.format(duration))
            
    if not duration:
        print('cannot get video duration!')
        raise SystemExit

    chunk_count = math.ceil(duration / chunk_duration)

    for n in range(chunk_count):
        start = chunk_duration * n
        pth, ext = filename.rsplit(".", 1)
        cmd =  "ffmpeg -i {} -vcodec copy  -strict -2 -ss {} -t {} {}-{}.{}".format(filename, start, chunk_duration, pth, n, ext)
        check_call(shlex.split(cmd), universal_newlines=True)
