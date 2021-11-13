---
title: Managing dotfiles with `stow(8)`
tags: [dotfiles, setup]
date: 2021-08-04
description: "Stow Away. Cast: my dotfiles. Written and Directed by: me"
---

**DOTFILE** _noun_  
/dɒtfʌɪl/  
Files that begin with a `.` (dot) character, are _hidden_ on all \*nix systems, and allows one to do tasks ranging from _customizing colors_ to _shutting down skynet_.

## How I started with dotfiles

I came across the concept of dotfiles back in 2019, courtesy of HackerNews ;). Back then, I didn't have any "dotfiles" to actually manage—I was using standard macOS applications and GitHub's Atom for all my programming purposes (ik, i was a noob back then).

After a while, around the start of 2020, I started using vim, switched to [`yabai`](https://github.com/koekeishiya/yabai) and started using [`skhd`](https://github.com/koekeishiya/skhd), worked around <mark>$AAPL</mark>'s ridiculous default settings (I'm looking at you, Dock) accessible only through the command-line and I found myself modifying and breaking a lot of my settings more often then not.

Hence I decided to put all my dotfiles scattered everywhere under `git` like any normal person, and manually symlinked them to the necessary locations.[^1]
[^1]: https://github.com/aklsh/dots

## Present day

I then switched to Linux-based distros after I got `zephyrus`. This led to a lot more tools for which I ~~needed to~~ could manage dotfiles - I used `i3` as my WM, `zathura` as my PDF reader, `nvim` for text-editing (believe me, it's sooo much better, especially with lua), `i3status` and `i3blocks`, `tmux` and a _looot_ of colorscheme customisations. Moreover, every other weekend, I was trying out other distros - Manjaro, Debian, Alpine to name a few and needed a way to make my configs portable :).

I now use vanilla Pop!\_OS 21.04 with Gnome and Pop-shell for a simple, just-works™ setup. Over the months, I had a lot of dotfiles and individually symlinking them became a PITA, especially after a clean install.

That was when I found [`stow(8)`](https://www.gnu.org/software/stow/manual/stow.html).

## <code style='color: #fff'>cd ~/dots && stow *</code>

Now, it's as simple as that. All that was needed was a little bit of organisation of files.

Let's take "stow"ing `nvim`'s config files. Typically they need to be placed in `~/.config/nvim/`.

So, for `stow` to symlink your `nvim` files properly, you need to have your files organised like this:

```shell
 ~/dots/
   └─nvim/
     └─.config/
        └─nvim/
           ├─ init.lua
           ├─ lua/
           └─ plugin/
```
When you do `stow nvim`, all the files in the `nvim` directory get symlinked in the **parent directory of your "stow dir"**, which is `~`.

Doing `stow *`, symlinks all "package directories" (essentially the top level folders in stow dir) to the parent directory.
