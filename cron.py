import json
import os
import subprocess
import logging
import tempfile
import shutil
import datetime

tempdir = tempfile.mkdtemp()
cwd = "/home/hopebayadmin/hb_monitor/ptt-web-crawler"
progress_file = "save/ptt_progress" 
board_list = ['MobileComm', 'Soft_Job', 'Tech_Job']
logging.basicConfig(filename='/home/hopebayadmin/hb_monitor/ptt-web-crawler/cron.log',level=logging.DEBUG)

# start logging
logging.debug(datetime.datetime.now().isoformat())

# change cwd
os.chdir(cwd)

# load progress 
progress = {}
with open(progress_file , 'r') as f:
    try:
        progress = json.load(f)
    except:
	pass

# for each board list
for board in board_list:
    # get board progress
    try:
        board_prog = progress[board]
    except:
        board_prog = 0
 
    # crawler
    subprocess.check_output("cd %s; python %s/crawler.py -b %s -i %s -1" % (tempdir, cwd,  board, board_prog ), shell=True)
    crawled_result = subprocess.check_output("ls %s | grep %s" % ( tempdir, board ), shell=True)
    crawled_result = crawled_result.rstrip('\n')

    crawled_progress = crawled_result.split('-')[2].split('.')[0]
    logging.debug( "crawled_result: %s" % (crawled_result) )
    logging.debug( "crawled_prog: %s" % (crawled_progress) )
    logging.debug( "board_prog: %s" % (board_prog) )
    
    # if last page id = board progress, skip
    if int(board_prog) != int(crawled_progress):
        # import to es
        logging.debug( "import %s" % (crawled_result) )
        subprocess.check_output("python import_es.py %s/%s" % ( tempdir, crawled_result ), shell=True)

    # archive crawled_result
    logging.debug( "archive %s" % (crawled_result) )
    subprocess.check_output("mv -f %s/%s archive" % ( tempdir , crawled_result ), shell=True)
    # save board progress
    logging.debug( "save progress: %s" % (crawled_progress) )
    progress[board] = crawled_progress

# save progress
with open(progress_file, 'w') as outfile:
     json.dump(progress, outfile)

# clear temp folder
shutil.rmtree( tempdir )
