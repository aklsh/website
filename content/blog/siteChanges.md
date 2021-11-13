---
title: "Site Changes"
date: 2020-12-26
description: "I can't do parkour. So my site does it!"
tags: [misc]

---

Yup. The right time to work on revamping my site is just when exams are announced for courses I did about a year ago. No, god forbid I do it when I was literally having nothing to do when the first lockdown happened in March. It has to be now.

## Nord-ify everything
So the [old color scheme](https://cdn.aklsh.me/blog/palette/palette.png) I made became increasingly difficult to use as there were only 4 colors in total, and it made it hard to... well do anything that required me to use colors - syntax highlighting, backgrounds etc. Also, I was beginning to become bored of it.

So, I was browsing the web (mainly r/unixporn) for some color-schemes when I came across [Nord](www.nordtheme.com). Although at first, I didn't like it very much, I disliked it the least compared to other schemes I saw.

I decided to try out it's vim-port for a week or so before deciding. Turned out to be really good. Now I can actually use RED to show error messages with linting xD.

Huge shoutout to [arcticicestudio](https://github.com/arcticicestudio) for coming up with this. There's also many other community-made ports for various programs - zathura, KDE Plasma are some that come to my mind now.

## Jekyll is CANCELLED

If you noticed, the footer at the bottom now says "Made with Neovim and _Hugo_". That's right. I just wanted to try out Hugo, and see if it was much simpler to use than Jekyll. I couldn't find any difference other than the fact that Hugo had much faster reloads when previewing the site on `localhost`.

Sometimes Jekyll would take a good 10secs and 100 clicks of the refresh button before it actually reflected the change I made. Maybe I was doing something wrong, or maybe it had a flag to do incremental builds. But Hugo worked fast OOTB. Also, Jekyll was such a pain to manage without knowledge of Ruby. Hugo just needed `sudo pacman -S hugo` and I was good to go.

## Friendship ended with gh-pages. Now Vercel is my best friend

I came across [Ashish's website](https://ashishpanigrahi.now.sh) when I learnt about the existence of Vercel, and it's free `.now.sh` domains.

Obviously, `aklsh.now.sh` sounds and looks much cooler than `aklsh.github.io`.

## Other changes

Remember I had a contact form in my old website? Turns out spammers have the patience to fill it. I received about 10 emails in a span of 2 weeks around October when I decided to stop the contact form from sending me emails. Not that I received any other emails anyways, other than a kind senior of mine who was surprised, and I quote "sophomores had their own websites". You underestimate how free I am lol.

During the revamping, I decided to drop the contact form idea, as it was just pure, clumsy HTML, and I didn't want to go through the trouble of tweaking it to match the current theme. There's always my mail if you need to contact me. My inbox is always open for comments, and I'll definitely reply!
