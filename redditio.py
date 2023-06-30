import datetime
import json
import time
from datetime import timedelta
from random import random

import halo
import httplib2
import pysrt
import pyttsx3
# import pyyoutube.models as mds
import whisper  # OpenAI Whisper
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
# from pyyoutube import Client
# from pyyoutube.media import Media
# from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
# from selenium.webdriver.firefox.options import Options
# from simple_youtube_api.Channel import Channel
# from simple_youtube_api.LocalVideo import LocalVideo

import constants as C
from driver import DriverHelper

httplib2.RETRIES = 1  # Handling retry logic ourselves, so tell httplib2 not to retry


class RedditIO:
    def __init__(self):
        driverhelper = DriverHelper()
        self.driver = driverhelper.get_driver()
        if self.driver is None:
            driverhelper.start_session()
            self.driver = driverhelper.get_driver()
        self.cleanup()  # Run just in case some old files are left over

    def get_post(self):
        spinner = halo.Halo(text='Loading Firefox', spinner='dots')
        spinner.start()

        driver = self.driver

        spinner.stop()

        spinner = halo.Halo(text='Loading Reddit', spinner='dots')
        spinner.start()

        driver.get('https://old.reddit.com/r/AmItheAsshole/')

        spinner.stop()

        spinner = halo.Halo(text='Finding Post', spinner='dots')
        spinner.start()

        post_list = driver.find_element(By.ID, 'siteTable').find_elements(By.XPATH, './div')  # All posts
        top_post = post_list[2]  # Top post
        top_post.find_element(By.TAG_NAME, 'a').click()  # Click on title to navigate to post
        driver.implicitly_wait(5)

        spinner.stop()

        spinner = halo.Halo(text='Finding Post Info', spinner='dots')
        spinner.start()

        post_info = {}
        post_info['title'] = driver.find_elements(By.CLASS_NAME, 'title')[2].text.split('(self.AmItheAsshole)')[0]
        post_info['body'] = driver.find_elements(By.CLASS_NAME, 'usertext-body')[1].text.replace('\n', ' ')
        for i in C.AITA_REPLACE_LIST:
            post_info['title'] = post_info['title'].replace(i, C.AITA_REPLACE_LIST[i])
            post_info['body'] = post_info['body'].replace(i, C.AITA_REPLACE_LIST[i])

        spinner.stop()

        already_made = False
        with open('./video_list.json', 'r') as f:
            video_list = json.load(f)
            for i in video_list['videos']:
                if i == post_info['title']:
                    already_made = True
                    break
        if not already_made:
            video_list['videos'].append(post_info['title'])
            with open('./video_list.json', 'w') as f:
                json.dump(video_list, f)

        self.post_info = post_info
        print(self.post_info)

        return already_made

    def generate_voiceread(self):
        # Generate voice read with gTTS
        spinner = halo.Halo(text='Generating Voice Read', spinner='dots')
        spinner.start()
        engine = pyttsx3.init('sapi5')  # Using the Windows SAPI5 engine

        engine.save_to_file(self.post_info['title'] + self.post_info['body'], './output/voiceover.mp3')
        engine.runAndWait()

        # tts_file = gTTS(text=self.post_info['title'] + self.post_info['body'], lang='en')
        # tts_file.save('post.mp3')
        spinner.stop()

    def generate_subtitles(self):
        # Generate subtitles with OpenAI Whisper
        spinner = halo.Halo(text='Generating Subtitles', spinner='dots')
        spinner.start()

        model = whisper.load_model("base")
        result = model.transcribe('./output/voiceover.mp3')

        # Write the transcript to an SRT file
        output_writer = whisper.utils.get_writer("srt", "./output")
        output_writer(result, './output/voiceover.mp3')
        spinner.stop()

        # self.fix_subtitles()

    def fix_subtitles(self):
        # Whisper subtitles are generated with a block for every sentence.
        # This function makes it so that there is a block for every word,
        # So that the subtitles can fit on screen

        subs = pysrt.open('./output/voiceover.srt')
        newfile = pysrt.SubRipFile()  # New SRT file
        index_counter = 1

        for i in range(len(subs)):
            start_time = subs[i].start.to_time()
            end_time = subs[i].end.to_time()
            # find the duration of the subtitle
            # You cannot subtract time objects
            duration = timedelta(hours=end_time.hour - start_time.hour,
                                 minutes=end_time.minute - start_time.minute,
                                 seconds=end_time.second - start_time.second,
                                 microseconds=end_time.microsecond - start_time.microsecond)
            num_of_words = len(subs[i].text.split(' '))
            list_of_words = subs[i].text.split(' ')
            dur_per_word = duration / num_of_words

            start_time = datetime.datetime.combine(datetime.date(1, 1, 1), start_time)

            # Create a new block for every word
            for j in range(num_of_words):
                new_sub = pysrt.SubRipItem()
                new_sub.index = index_counter
                new_sub.text = list_of_words[j]
                word_start = start_time + (dur_per_word * j)
                word_end = start_time + (dur_per_word * (j + 1))

                new_sub.start.seconds = word_start.second
                new_sub.start.minutes = word_start.minute
                new_sub.start.hours = word_start.hour
                new_sub.start.milliseconds = word_start.microsecond / 1000
                new_sub.end.seconds = word_end.second
                new_sub.end.minutes = word_end.minute
                new_sub.end.hours = word_end.hour
                new_sub.end.milliseconds = word_end.microsecond / 1000

                newfile.append(new_sub)
                index_counter += 1

        os.rename('./output/voiceover.srt', './output/voiceover_old.srt')
        newfile.save('./output/voiceover.srt')

    def generate_video(self):
        clip = VideoFileClip('./videos/clip1.mp4')
        audio = AudioFileClip('./output/voiceover.mp3')
        clip = clip.set_duration(59)
        audio = audio.set_duration(59)
        clip = clip.set_audio(audio)

        generator = lambda txt: TextClip(txt, font='./fonts/static/Geologica-Bold.ttf', fontsize=100, color='white',
                                         method='caption', size=clip.size)
        sub = SubtitlesClip('./output/voiceover.srt', generator)
        clip = CompositeVideoClip([clip, sub.set_position(('center', 'center'))])

        clip.write_videofile('./output/video.mp4', fps=24, codec='libx264')

        movie = VideoFileClip('./output/video.mp4')
        movie = movie.set_duration(59)
        movie.write_videofile('./output/final_video.mp4', fps=24, codec='libx264')

    def cleanup(self):
        try:
            os.remove('./output/voiceover_old.srt')
        except:
            pass
        try:
            os.remove('./output/voiceover.mp3')
        except:
            pass
        try:
            os.remove('./output/video.mp4')
        except:
            pass
        try:
            os.remove('./output/voiceover.srt')
        except:
            pass

    def random_time(self):
        return random()

    # def upload_video_with_selenium(self):
    #     spinner = halo.Halo(text='Uploading Video', spinner='dots')
    #     spinner.start()
    #
    #     # Upload video with selenium
    #     driver = webdriver.Firefox(self.fp, options=self.options)
    #     # driver.install_addon('./uBOLite_1.0.23.6195.firefox.mv3.xpi', temporary=True)
    #     driver.get('https://studio.youtube.com')
    #
    #     # Login
    #     email = driver.find_element(By.ID, 'identifierId')
    #     time.sleep(self.random_time())
    #     for i in C.EMAIL:
    #         email.send_keys(i)
    #         time.sleep(self.random_time())
    #     time.sleep(1)
    #     for i in range(len(C.EMAIL)):
    #         email.send_keys(Keys.BACKSPACE)
    #         time.sleep(self.random_time())
    #     time.sleep(1)
    #     for i in C.EMAIL:
    #         email.send_keys(i)
    #         time.sleep(self.random_time())
    #     time.sleep(self.random_time())
    #     email.send_keys(Keys.ENTER)
    #
    #     time.sleep(2)
    #
    #     password = driver.find_element(By.CLASS_NAME, 'whsOnd')
    #     password.send_keys(C.PASSWORD)
    #     time.sleep(self.random_time())
    #     password.send_keys(Keys.ENTER)
    #
    #     driver.implicitly_wait(5)
    #
    #     # Upload video
    #     create_video_button = driver.find_element(By.ID, 'create-icon')
    #     create_video_button.click()
    #     time.sleep(0.2)
    #     upload_video_button = driver.find_element(By.ID, 'text-item-0')
    #     upload_video_button.click()
    #     time.sleep(2)
    #     # select_files_button = driver.find_element(By.ID, 'select-files-button')
    #     # select_files_button.click()
    #
    #     file_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
    #     file_input.send_keys("D:\\Code\\Python\\redditIO\\output\\final_video.mp4")
    #     time.sleep(10)
    #
    #     title_input = driver.find_element(By.CSS_SELECTOR,
    #                                       "[aria-label='Add a title that describes your video (type @ to mention a channel)']")
    #     try:
    #         title_input.send_keys(self.post_info['title'])
    #     except Exception as e:
    #         print(e)
    #         print('Continuing with default title')
    #         title_input.send_keys('Am I The Asshole Reddit Story')
    #     # No need to type body, since it is the same for every video and autofills
    #     time.sleep(0.25)
    #     next_button = driver.find_element(By.ID, 'next-button')
    #     next_button.click()
    #     time.sleep(0.25)
    #     next_button.click()
    #     time.sleep(0.35)
    #     next_button.click()
    #
    #     done_button = driver.find_element(By.ID, 'done-button')
    #     done_button.click()

    def upload_video_with_selenium_beta(self):
        spinner = halo.Halo(text='Uploading Video', spinner='dots')
        spinner.start()

        driver = self.driver
        driver.get('https://studio.youtube.com')

        # Upload video
        create_video_button = driver.find_element(By.ID, 'create-icon')
        create_video_button.click()
        time.sleep(0.2)
        upload_video_button = driver.find_element(By.ID, 'text-item-0')
        upload_video_button.click()
        time.sleep(2)
        # select_files_button = driver.find_element(By.ID, 'select-files-button')
        # select_files_button.click()

        file_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
        file_input.send_keys("D:\\Code\\Python\\redditIO\\output\\final_video.mp4")
        time.sleep(10)

        title_input = driver.find_element(By.CSS_SELECTOR,
                                          "[aria-label='Add a title that describes your video (type @ to mention a channel)']")
        try:
            title_input.send_keys(Keys.CONTROL, 'a')
            title_input.send_keys(Keys.DELETE)
            title_input.send_keys(self.post_info['title'])
        except Exception as e:
            print(e)
            print('Continuing with default title')
            title_input.send_keys(Keys.CONTROL, 'a')
            title_input.send_keys(Keys.DELETE)
            title_input.send_keys('Am I The Asshole Reddit Story')
        # No need to type body, since it is the same for every video and autofills
        time.sleep(0.25)
        next_button = driver.find_element(By.ID, 'next-button')
        next_button.click()
        time.sleep(0.25)
        next_button.click()
        time.sleep(0.35)
        next_button.click()

        done_button = driver.find_element(By.ID, 'done-button')
        done_button.click()

        time.sleep(30)  # Wait to make sure video is done uploading before closing YouTube Studio

        driver.get('https://www.google.com')

        spinner.stop()

    # def upload_video_with_new_API(self):
    #     client = Client(api_key=C.API_KEY)
    #
    #     # check if title exists in post_info
    #     if self.post_info is None:
    #         self.post_info = {}
    #         self.post_info['title'] = 'Am I The Asshole Reddit Story'
    #
    #     body = mds.Video(
    #         snippet=mds.VideoSnippet(
    #             title=self.post_info['title'],
    #             description='Thanks for watching everyone, please subscribe :D. #shorts #reddit #redditstories '
    #         )
    #     )
    #
    #     media = Media(filename='./output/final_video.mp4')
    #
    #     upload = client.videos.insert(
    #         body=body,
    #         media=media,
    #         parts=['snippet'],
    #         notifySubscribers=True
    #     )
    #
    #     video_body = None
    #
    #     while video_body is None:
    #         status, video_body = upload.next_chunk()
    #         if status:
    #             print(f"Uploaded {int(status.progress() * 100)}%.")
    #
    #     print(video_body)
    #
    # def upload_video_with_API(self):
    #     channel = Channel()
    #     channel.login('client_secrets.json', 'credentials.storage')
    #
    #     video = LocalVideo('./output/final_video.mp4')
    #
    #     video.set_title(self.post_info['title'])
    #     video.set_description('Thanks for watching everyone, please subscribe :D. #shorts #reddit #redditstories '
    #                           '#redditshorts')
    #     video.set_tags(['reddit', 'redditstories', 'redditshorts', 'shorts', 'gaming', 'funny', 'memes', 'askreddit', ])
    #     video.set_default_language('en-US')
    #
    #     video.set_embeddable(True)
    #     video.set_license('creativeCommon')
    #     video.set_privacy_status('public')
    #     video.set_public_stats_viewable(True)
    #
    #     video = channel.upload_video(video)
    #     print(video.id)
    #     print(video)
    #
    #     video.like()  # Like your own video. It's meta.
