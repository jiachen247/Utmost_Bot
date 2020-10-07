# Utmost Bot (@utmost_bot)
Telegram bot that servers content from My Utmost for his Highest by Oswald Chambers
hosted on GAE.

Based off LljBot by @whipermr5

#story time
This bot was born out of the love for two things. Utmost of His Highest and Bots

It is my sincere desire that this bot will truly lead people to have a deep and personal daily quiet time.

#on a side note
Added 2 layers of cache to optimize response time by removing network IO
    1. GAE's Memcache
    2. GAE's Datastore

This lead to 2 things,
    a cut of response time by more than half +
    generating alot less traffic for utmost.org

So far, all usage has been under GAE's free qouta YAYERS:)

- added DevoSource Interface to using Abstract Base Classes to make reusing code easier.


To God be the Glory


#Mass Messages
9/9/16 07:01
weeksary_message = (
            "✨* Update 1.01 *✨\n" +
            "🌞 Happy Saturday 🌞\n\n" +

            "Hello everyone :) Today marks my *1st WEEK-SARY* 💐 I pray & hope that I've been a blessing to y'all over the course of this week, spurring everyone on to a consistent and daily quiet time with God.\n\n" +

            "Due to the overwhelming feedback, today's update includes support for different bible versions! ( _yay finally_ 🎉 )\n\n" +

            "This change would (hopefully) allow for everyone to read God's Word to us in a version that they're most comfortable with. Do try it out with my /bible command!\n\n" +

            "Should you have any further feedback, please do not hesitate to relay it to me via my /feedback command :))\n\n\n" +

            "God Bless🌻\n@Utmost\_bot")
