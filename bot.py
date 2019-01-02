import signal, sys
import praw
import secrets
import time
import traceback

DRY = len(sys.argv) > 1

def save_counter():
    global counter
    print('Saving the counter: %d' % counter)
    with open('counter', 'w') as f:
        f.write(str(counter))

def load_counter():
    global counter
    try:
        with open('counter') as f:
            counter = int(f.read())
        print('Loaded the counter: %d' % counter)
    except FileNotFoundError:
        counter = 0
        print('Starting with counter = 0')

def signal_handler(sig, frame):
    save_counter()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

load_counter()

cliche = 'Reddit cliché noticed'

template = cliche + ': ' + cliche + "\n\n\nPhrase noticed %d time%s.\n\n\n" + \
    ' '.join(map(lambda x: '^' + x, "I'm a bot, beep duh. Message me if you want to, I'll tell the code monkey".split(' ')))

def get_bot():
    return praw.Reddit(user_agent='/u/clichebot9001',
            client_id=secrets.CLIENT_ID,
            client_secret=secrets.CLIENT_SECRET,
            username=secrets.USERNAME,
            password=secrets.PASSWORD)

if __name__ == '__main__':
    try:
        bot = get_bot()
        for comment in bot.redditor('clichebot9000').stream.comments():
            try:
                comment.refresh()
            except Exception:
                print(traceback.format_exc())
                continue
            if cliche not in comment.body:
                continue
            print(comment.permalink)
            for reply in comment.replies:
                if reply.author == secrets.USERNAME:
                    print('Already answered')
                    break
            else:
                if not DRY:
                    counter += 1
                    s = 's' if counter != 1 else ''
                    print('Counter is now %d' % counter)
                    try:
                        comment.reply(template % (counter, s))
                    except Exception:
                        print(traceback.format_exc())
                        counter -= 1
    except Exception:
        save_counter()
        raise
    save_counter()
