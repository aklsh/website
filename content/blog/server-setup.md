---
title: Server Setup
tags: [selfhost, setup]
date: 2023-12-29
description: "This is why the website was down for a while."
---

If you've been following me on twitter/fedi — or even this website — you would've observed that I've been increasingly trying to selfhost applications whenever I can. Why? Because I got a ~~$7~~ $12 (upgraded to 2GB RAM because 1GB was starting to swap at times) DO droplet and I'm trying to take full advantage of it. Also, it's a fun hobby — breaking your head over why your application isn't showing up when the logs don't show any failures, only to realise that you've mistyped the port number :p

## What I host on the droplet
### Public access
- This website.
- [My browser startpage](https://startpage.aklsh.me).
- [Personal fediverse instance](https://social.aklsh.me) with [GoToSocial](https://gotosocial.org).
- [Notes/wiki](https://wiki.aklsh.me) with [Bookstack](https://www.bookstackapp.com/).

### Internal access
- [znc](https://wiki.znc.in/ZNC) bouncer for IRC.
- [freshrss](https://www.freshrss.org/) for RSS feeds.
- [vaultwarden](https://github.com/dani-garcia/vaultwarden) for passwords (yet to migrate completely though).
- [healthcheck](https://healthchecks.io/) for checking on status of a few cron jobs I have set up on my personal laptop.

Apart from these services, I also have a few to ease in monitoring/managing all of these, again in internal access only:
- [portainer](https://www.portainer.io/) for easy container management.
- [glances](https://nicolargo.github.io/glances/) to keep a watch on the system load, memory etc [^1] 
- [watchtower](https://containrrr.dev/watchtower/) to automagically update my containers.

All of this is behind [traefik](https://traefik.io/traefik/). I chose traefik because it was easiest to get working with docker containers, mainly because of its label-based configuration — I didn't need to keep track of a separate "config" file like in nginx.

## Network Overview
I was inspired by [mrkaran's](https://mrkaran.dev) post on [exposing services while self-hosting](https://mrkaran.dev/posts/exposing-services/). I was already using tailscale to secure ssh access to my droplet and laptop (to connect from my phone) and also for its taildrop feature. I initially tried to copy his architecture exactly with 2 caddy instances, with one listening on the droplet's floating IP interface and the other on the tailscale IP interface, but I decided to switch from bare-metal to containers with docker-compose. Why you ask? Because I've always struggled with understanding docker and this gave me a chance to understand how it works, along with being able to handle updates and backups more easily (with docker volumes).

![architecture](https://cdn.aklsh.me/blog/server-setup/architecture.png)

Traefik was pretty straightforward to setup. The config from the [basic example](https://doc.traefik.io/traefik/user-guides/docker-compose/basic-example/) was enough to get me started. I mapped ports 80/443 of the container to those of the tailscale IP's interface and mapped 81/444 to the floating IP's interface's 80/443 ports. Since I like having each service on a subdomain (instead of a subdirectory under the apex domain), I create A records pointing to the droplet's tailscale IP for DNS. This isn't an insecurity since the IP range falls in the CGNAT space and hence is treated as a private IP address.

One downside with traefik compared to caddy was HTTPS — caddy required no configuration out of the box for automatic HTTPS. However, setting up automatic https for all hosts with traefik is a breeze compared to nginx (which is what I was using previously). I use cloudflare for my nameservers[^2] and manage everything on it and hence I configured cloudflare as the provider as [described here](https://doc.traefik.io/traefik/https/acme/#dnschallenge).

```yaml
  command:
    ...
    - "--certificatesresolvers.letsencrypt.acme.dnschallenge.provider=cloudflare"
    - "--certificatesresolvers.letsencrypt.acme.email=aklsh@tuta.io"
    - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
  environment:
    - CLOUDFLARE_EMAIL=xxxxxxxxxxx
    - CLOUDFLARE_DNS_API_TOKEN=xxxxxxxxxxxxxxxxx
```

I also wanted to route all HTTP traffic to HTTPS and the following established that.

```yaml
  labels:
    ...
    - "traefik.http.routers.http-catchall.rule=hostregexp(`{host:.+}`)"
    - "traefik.http.routers.http-catchall.middlewares=redirect-to-https"
    - "traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https"
    - "traefik.http.middlewares.redirect-to-https.redirectscheme.permanent=true"
```

Adding a new container to the network is super easy — just a few labels for the container in `docker-compose.yml`, and adding it to the `traefik-network`.

```yaml
  network:
    - traefik-network
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.dashboard.rule=Host(`<subdomain>.aklsh.me`)"
    - "traefik.http.routers.dashboard.tls.certresolver=letsencrypt"
    - "traefik.http.services.<service name>.loadbalancer.server.port=<port>"
    - "traefik.http.routers.dashboard.entrypoints=<private/public>"
```

[^1]: [do-agent](https://github.com/digitalocean/do-agent) is great, but not very comprehensive.
[^2]: trying to transfer my domain to cloudflare, but neither of the payment methods work for me :(
