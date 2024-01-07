#
# Copyright (C) 2023 Erymanthus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# 

'''
https://www.reddit.com/r/Technoblade/comments/17fmpaw/off_topic_reddit_api/

Off Topic: Reddit API

Hey everyone!

I have a small amount of Java code I need someone to write,
because I'm old and I'm not about to try to plunge into the reddit API
at this stage in my life. Me at 20 would tackle anything;
these days learning new APIs makes my head hurt.

Looking for someone to write a Java program that,
when given a reddit username, will retrieve as many post from that user
as possible. I believe the limit is the last 1000 posts, 100 at a time.

Efficiency, economy, code quality, formatting, etc. all unimportant to me.
Just need the last 1000 posts. (Presumably if they've posted less than 1000
times, then however many that is.)

My expectation is that for someone already knowledgeable about the reddit API
this would not be much work at all. I hope so anyway!

I am going to take the body text of the 1000 posts and do some further string
processing on them. The results will be going on a video on my YouTube channel.

Am happy to either credit the author on the video, or not credit the author,
as the author prefers.

I have no idea what I ought to offer for this so I'll just say $100.
If that number is horribly off please let me know.

Prefer people reply on this thread.
Reddit private messages are completely borked for me.

I know this is off-topic but I hope it's not a horrific misdeed.
Also if anyone knows a better place to ask, by all means let me know.

Thank you all very much.

-- "Mister" Technodad
'''

# ok, i know you wanted it to be in java and i *have* written kotlin + java code
# for various minecraft mods before but i have never known how to compile
# my own jar file so take this as more of a proof of concept than anything,
# because i don't have the knowledge to import com.google.gson or whatever
# with the expectation that it'll compile correctly

# the bad news (besides this whole thing being in python, of course)
# is that while the loop will go as far as 1k pieces of content,
# there is no guarantee that it'll fully parse all 1k pieces even if the
# supplied username has over 1k+ posting history in either category.
# i (u/raydeeux) have been on reddit for at least three years and i *know*
# that i have more than 1k+ comments, but this scraper only scrapes around 970+
# for my username on a good day. why? most likely because those comments were
# removed by some faraway subreddit mod (outside r/technoblade and r/mrtechnodad)
# for reasons beyond my control (and therefore, beyond API access).

# the good news is that unlike 90% of the reddit api-related files you'll find
# that are written in python, this one doesn't rely on all that fancy-schamncy
# PRAW stuff everyone's using. this works as a standlone python file! (woww)

# as compensation for writing this in python, the output of this file gets
# sent to .txt form, which can hopefully be read by your java code as necessary.

# worst case scenario, bommerboss probably sent you something better in your
# discord dms by the time you're reading this.

# credit me as necessary.

# erymanthus[#5074] | (u/)raydeeux {u/raydeesux}

from urllib.error import HTTPError # necessary import to intercept HTTP error codes
import urllib.request as url # necessary import to grab reddit data
import json # necessary import to convert to json object
import re # necessary import as there's a bit of regex happening here

def grabRedditContent(username: str, commentMode: bool): # "commentMode = False" grabs selfposts, "commentMode = True" grabs comments.
    redditUsernameRegex = re.compile("[a-zA-Z0-9-_]{3,20}") # Reddit username validity regex. Included for sanity check. do not edit.
    if not redditUsernameRegex.match(username): # if username does not match regex requirements
        print("Username", username, "does not conform to Reddit's username requirements. Aborting mission.") # print message about this mistake
        return # end function execution early
    commentModePlaceholder = "submitted" # (DO NOT CHANGE) name per Reddit URL structure
    relevantKey = "selftext" # (DO NOT CHANGE) name per Reddit API JSON data key
    type = "Self-post" # safe to change, although keep as is to differentiate more easily
    contentTypePlaceholder = "selfposts" # safe to change, although keep as is to differentiate more easily
    if commentMode: # changes below string variables accordingly
        commentModePlaceholder = "comments" # (DO NOT CHANGE) name per Reddit URL structure
        relevantKey = "body" # (DO NOT CHANGE) name per Reddit API JSON data key
        type = "Comment" # safe to change, although keep as is to differentiate more easily
        contentTypePlaceholder = "comments" # safe to change, although keep as is to differentiate more easily
    afterKey = "" # do not arbitrarily change this, otherwise it will break the while loop below
    loopCount = 0 # for counting pieces of content (used later in writing into the file)
    total = 0 # for counting total content
    fileName = (username + "_" + contentTypePlaceholder + ".txt") # because easier place to change file name template
    # below two lines open/create the files for writing. mode = "w" to allow overwriting/refreshing (therefore, preventing duplicate occurences of comments)
    relevantFile = open(fileName, "w", encoding = "utf-8") # encoding is necessary to encode emojis in comments and prevent crashing
    afterKeyFile = open("afterKeys.txt", "w")
    # start the while loop
    try:
        while (afterKey is not None): # "is not None" conditional check to ensure we stop after we hit the 1000 pieces of content limit (which is autoenforced by reddit by setting "after" key to null)
            urlUrl = "https://www.reddit.com/user/" + username + "/" + commentModePlaceholder + ".json?limit=100&after=" + afterKey
            userAgent = {'User-Agent': 'ErymanthusAndMrFaceplate'} # pseudo useragent string to reduce https error code 429s
            request = url.Request(
                url = urlUrl,
                data = None, # apparently i need this line as part of me spoofing the user agent string.
                headers = userAgent
            )
            j = url.urlopen(request)
            jObj = json.load(j) # convert to json object (sorta)
            theData = jObj['data']['children'] # access the relevant data containing all content to be analyzed
            numIndicies = len(theData) # good 'ol (range(100)) isn't enough since it might crash if the dictionary is shorter than 100 indicies
            afterKey = jObj['data']['after'] # this is a surprise tool that helps continue the while loop later in order to grab 1000 pieces of content in one go
            for i in range(numIndicies):
                content = theData[i]["data"] # grab index-specific content
                if (content[relevantKey] is not None and content[relevantKey] != ""):
                    # above line's conditonal check prevents unnecessary content (non-selfposts or otherwise empty content) from being analyzed and written to file
                    # below line removes unnecessary line breaks and ensures the only one line break renders at a time. also allows ">" and "<" to render properly
                    prettifiedContent = content[relevantKey].replace("\r\n", "\n").replace("\n\n&amp;#x200B;", "").replace("&amp;#x200B;", "").replace("&amp;", "").replace("\n\n", "\n").replace("&gt;", ">").replace("&lt;", "<").replace("  ", " ")
                    # below lines remove non-word content
                    prettifiedContent = re.sub(r"!\[gif\]\(.*\)", " __[GIF CONTENT]__ ", prettifiedContent)
                    prettifiedContent = re.sub(r"https\:\/\/preview\.redd\.it/.*", " __[IMAGE]__ ", prettifiedContent)
                    # below lines attempt to remove all reddit-specific markdown
                    prettifiedContent = re.sub(r"(\*\*\*(?P<mdbolditalic>[^\*\*\*]+)\*\*\*)", "\\g<mdbolditalic>", prettifiedContent)
                    prettifiedContent = re.sub(r"(\_\_\_(?P<mdbolditalic>[^\_\_\_]+)\_\_\_)", "\\g<mdbolditalic>", prettifiedContent)
                    prettifiedContent = re.sub(r"(\~\~(?P<mdstrike>[^\~\~]+)\~\~)", "\\g<mdstrike>", prettifiedContent)
                    prettifiedContent = re.sub(r"(\*\*(?P<mdbold>[^\*\*]+)\*\*)", "\\g<mdbold>", prettifiedContent)
                    prettifiedContent = re.sub(r"(\_\_(?P<mdbold>[^\_\_]+)\_\_)", "\\g<mdbold>", prettifiedContent)
                    prettifiedContent = re.sub(r"(\*(?P<mditalic>[^\*]+)\*)", "\\g<mditalic>", prettifiedContent)
                    prettifiedContent = re.sub(r"(\_(?P<mditalic>[^\_]+)\_)", "\\g<mditalic>", prettifiedContent)
                    prettifiedContent = re.sub(r"(\>\!(?P<mdspoiler>[^\!\<]+)\!\<)", "\\g<mdspoiler>", prettifiedContent)
                    prettifiedContent = re.sub(r"(\>)*( )*(?P<mdquote>.*)", "\\g<mdquote>", prettifiedContent)
                    prettifiedContent = re.sub(r"\^(?P<mdsuper>[^\^ ]*)", "\\g<mdsuper>", prettifiedContent)
                    prettifiedContent = re.sub(r"\#{1,5}(?P<mdheading>.*)", "\\g<mdheading>", prettifiedContent)
                    prettifiedContent = re.sub(r"((\`){1,3}(?P<mdcode>[^\`]+)(\`){1,3})", "\\g<mdcode>", prettifiedContent)
                    prettifiedContent = re.sub(r"\[(?P<mdlinktext>[^\]]*)\]\((?P<mdlinkurl>[^\)]*)\)", "\\g<mdlinktext> __[\\g<mdlinkurl>]__ ", prettifiedContent)
                    # ensure escaped chars render properly
                    prettifiedContent = re.sub(r"\\(?P<escapedChar>\S.)", "\\g<escapedChar>", prettifiedContent)
                    # eliminate "  "s because they're ugly as heck 
                    prettifiedContent = prettifiedContent.replace("  ", " ")
                    # below line appends new line for readability between heading and actual content
                    prettifiedContent = "\n" + prettifiedContent
                    # below line appends post title before all content
                    if not commentMode: prettifiedContent = "\nSELF-POST TITLE:\n" + theData[i]["data"]["title"] + prettifiedContent
                    # below line counts total content
                    total = (loopCount * 100) + (i + 1)
                    # below line writes to file (potentially for further analysis)
                    relevantFile.write("__[" + type.upper() + " #" + str(total) + "]__" + prettifiedContent + "\n__[END ABOVE " + type.upper() +  "]__\n\n")
                    # below line ensures the program isn't freezing (it did that to me once and now i don't trust my loaner dell laptop anymore)
                    # print("__[FOR DEBUGGING PURPOSES ONLY: " + type + " #" + str(total) + "]__")
            if (afterKey is not None): # for debugging purposes, the afterkey returned by reddit is written to file
                afterKeyFile.write(afterKey + "\n")
            loopCount += 1
        # below two lines close files just to be safe
        relevantFile.close()
        afterKeyFile.close()
        # aaaaaand we are done! celebrate by printing a summary of what just happened.
        print(type, "content scraping complete for u/" + username + "!", total, type.lower() + "s were scraped.")
        if (total != 1000): print("Note that some contents may have been skipped either because they were not selfposts or\nbecause the content was removed from its respective subreddit.\nIt's also likely, however, that this user simply doesn't have enough content to begin with.")
    except HTTPError as e:
        print("Crap! It seems you've run into error", str(e.code) + "! Aborting mission.\nFor best results, please try again in about a minute. In the meantime...")
        if e.code == 404: print("- Make sure that u/" + username, "is a valid Reddit username.")
        if e.code == 429: print("- Please try not to request so many users at once.")
        print("- Have a glass of water and stay hydrated.")
        return

grabRedditContent("mrtechnodad", False) # sample code to grab selfposts for u/mrtechnodad
grabRedditContent("mrtechnodad", True) # sample code to grab comments for u/mrtechnodad

'''
CONCLUSION:
depending on the mode you chose earlier above, you'll get
(at most) two text files per user, one for each content type
(either comments or self-posts). in each text file, you'll see
lines (or portions of lines) formatted such as the one below:

__[FOO BAR FOO BAR]__

...or like even further below:

bar foobar foo __[FOO BAR FOO BAR]__ foobar bar foo far boo

anyway, these strings are meant to be ignored.
all other content is ready for analysis.

- erymanthus[#5074] | (u/)raydeeux {u/raydeesux}
'''
