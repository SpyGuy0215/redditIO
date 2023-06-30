# RedditIO


RedditIO is a program that automatically reads videos from Reddit and publishes them
to YouTube. Written in Python 3, it uses powerful libraries like `selenium`, 
`moviepy`, `pyttsx3`, and `openai-whisper` to generate videos that are both entertaining and
surprisingly human.

Tested with Python 3.10

## Installation

Clone this repository:

```bash
git clone https://github.com/SpyGuy0215/redditIO.git
```

Make a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install the required libraries:

```bash
pip install -r requirements.txt
```
(This may take a while, since there are a lot of dependencies)

This program comes packaged with GeckoDriver, which is used to control Firefox. If
this version doesn't work for you, or if you want to control another browser,
download the driver for that platform (ex: ChromeDriver for Chrome) and replace 
`geckodriver.exe` with the new driver. Then, in the code, replace all instances of
`webdriver.Firefox` with `webdriver.<browser>`, where `<browser>` is the name of 
the browser you want to use. (ex: `webdriver.Chrome`)

Go to `constants.py` and replace the `FIREFOX_BINARY_PATH` with the path to your
browser binary. The name doesn't have to be changed if you use another browser, 
but feel free to if you want (don't forget to change it wherever it's used in the
program as well!)

## Usage

While in the virtual environment, run the program:

```bash
python main.py
```

The program will ask you to log in to YouTube Studio. This is so the YouTube API
is bypassed, and the program can upload without a verified Google Cloud project.
Log in to YouTube Studio, **DO NOT CLOSE THE TAB**, and type `y` into the console
to continue running the program. Everything should be smooth sailing from there.

## Planned Features

- [ ] Organize project files better
- [ ] Add support for more subreddits
- [ ] Add support for hooking onto drivers with `webdriver.Remote`
- [ ] Optimize the video creation process, as a lot of unnecessary processing is
      done
- [ ] Integrate with qHub (coming soon!)

## Customization

By default, the program checks Reddit to post a video every 6 hours. This can be
changed in `main.py`, by changing this line:
```python
schedule.every(6).hours.do(lambda: run_redditIO(global_reddit))
```
Replace the `6` with anything you want. You can also replace the `hours` with
something else to change the interval. Check the `schedule` library documentation
to learn more. And remember, 
### **DO NOT USE THIS PROGRAM TO SPAM YOUTUBE!**

## Example Implementation

You can see an example of what this program does on YouTube. A channel called
RedditIO (fitting, right?) uploads videos generated by this program. Check it out
at `@redditio` on YouTube. And if you could, please subscribe :D