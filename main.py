import time

import schedule

from redditio import RedditIO


def run_redditIO(reddit):
    # Runs using the global_reddit instance
    if reddit.get_post():
        print('Already made video for this post')
        reddit.upload_video_with_selenium_beta()
    else:
        reddit.get_post()
        reddit.generate_voiceread()
        reddit.generate_subtitles()
        reddit.generate_video()
        reddit.upload_video_with_selenium_beta()


if __name__ == '__main__':
    global_reddit = RedditIO()   # Start a global RedditIO instance to be used every time a video is made
    schedule.every(6).hours.do(lambda: run_redditIO(global_reddit))  # Every 6 hours, run RedditIO's tasks
    run_redditIO(global_reddit)
    while True:
        schedule.run_pending()
        time.sleep(1)
