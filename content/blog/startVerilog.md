---
title: Getting Started with Verilog®
description: Verilog learning resources
date: 2019-06-27
tags: [tutorials, verilog]
math: false

---

So, over the summer I was having a lot of time (literally 3 months of free time xD). I decided to learn a language called *Verilog*, which I first came across in my Digital Systems course in the preceding semester.

So, what is Verilog?
In a nutshell, it is used to describe hardware circuits in a way that is easy to understand and also to simulate it.

Verilog is a *Hardware Description Language*, used to model electronic systems, usually digital circuits, at the *Register Transfer Level* or, even at the *switch-level*, i.e. at the level of transistors.

Simple as it may sound, the first time I wrote a Verilog program, there were a lot of errors. And the error message that I got from the compiler—[Icarus Verilog](http://iverilog.icarus.com/)—was this:

```terminal
example.v:1: syntax error
I give up.
```

Coming from a programming background of C, C++ and Python, Verilog had a steep learning curve. Since Verilog is used to model an actual hardware circuit, it is very different from the programming languages mentioned above—Verilog follows a "concurrent-style code execution", while the others are sequential.

When a hardware is used in the real world, all parts of it run/work simultaneously. But when, we write programs in C/C++, the statements are executed one after the other. So, moving from sequential to concurrent-style logic was a bit difficult initially.

After a lot of learning, StackOverflowing (is that even a word? xD), debugging, simulating etc. (I've attached links to every resource that I used in this post), I finally got the hang of it. In hindsight, it isn't that difficult, once you realize that code isn't executed sequentially.

I did have a difficult time getting good resources to learn from. I highly recommend the following resources for an absolute beginner to the language, who has done a basic digital systems course:

* [Hardware modelling using Verilog](https://nptel.ac.in/courses/106105165/): An online [NPTEL](https://nptel.ac.in) MOOC by [Prof. Indranil Sengupta](http://www.facweb.iitkgp.ac.in/~isg/). VERY VERY VERY helpful!!! He starts from the very basics of the language - from why it came to existence to why each and every part of the language is made in such a way. There might be some parts of the course which might be a bit tough for someone who is just starting out with Digital Systems/VLSI, but they can be skipped.

* [Verilog HDL: A Guide to Digital Design and Synthesis](https://books.google.co.in/books/about/Verilog_HDL.html?id=uAIwcAKo_VIC&printsec=frontcover&source=kp_read_button&redir_esc=y#v=onepage&q&f=false): One of the best books written about the Verilog language. EVER. Samir Palnitkar has gone over the syntax in great detail. Do give this book a read at least once.

* [HDLBits](https://hdlbits.01xz.net/wiki/Main_Page): Basically HackerRank (minus competitions) for Verilog.

Also, I've made a few modules on my own, which are very fundamental to any VLSI circuit. You can access the github repository [here](https://github.com/aklsh/getting-started-with-verilog). I'll keep updating the repository whenever I can, with newer modules. Do star the repository!! You can also submit pull requests with your own modules.
