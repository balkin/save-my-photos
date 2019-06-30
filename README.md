# Save my photos!
  
Perhaps I'm a slowpoke but a couple days ago I found that Flickr is saying I have more than 1000 photos and it's going
to delete oldest photos from my account. So, I'm willing to migrate them.

Obvious choice will be Google, but unfortunately I only have 15 GB of space, and most of that is occupied by my emails.
Because some of the photos are really old, and they were shot on shitty camera, I'm not going to further reduce their
quality.

Furthermore, I'd rather save them to multiple storages now. So, I decided to write a couple apps to help me.

# Introduction to Yandex Disk and Mail.ru Cloud

Yandex Disk is a cloud storage by Yandex, one of two biggest IT companies. You can think of Yandex as a Russian Google,
while Mail.Ru Group is a Russian Facebook. 

# Development

Although it's definitely the area where asynchronous I/O is the best, underlying libraries are not async. Hence the
migration tools are not async too. If you're feeling like you're able to add async support, please feel free to adjust
the code and send me the PR though.

Migration to Yandex is nearly finished and Works-for-me™. I will work on Mail.ru migration when I have time. Please feel
free to send me PRs if you have improvements.

# Usage

Flickr API client will print a link on your first run. When you will follow it and click "Allow", it will store OAuth
token and shut up. Things are more complicated with Yandex, you will need to get an OAuth token yourself.
https://oauth.yandex.ru/authorize?response_type=token&client_id=5bfb4e55ee8d420782c01a7f9c513eaa

Export it in your environment:

export YANDEX_OAUTH=AgAAAAAB...............................

If your photo folder is not `Фотокамера`, then you will need to provide that name too:

export YANDEX_PHOTOCAMERA=Photos

Other than that it's pretty much usual:

    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    export YANDEX_OAUTH=AgAAAAAB...............................
    export YANDEX_PHOTOCAMERA=Photos
    python src/app_flickr_to_yandex.py

# DISCLAIMER

THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.

It may hack Democrat Party servers, cause WW3, Fukushima explosion or something like that. And **you will be liable for
that**, unless you check the source first. Well, technically speaking, you will still be liable for that.

Just kidding :-)
