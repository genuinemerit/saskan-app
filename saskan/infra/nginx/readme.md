# Nginx deployment

Copy `saskan.conf.example` to `/etc/nginx/sites-available/sfp.conf`
and symlink into `sites-enabled/`.  Adjust paths and domains as needed.

To reload after edits:
    sudo nginx -t && sudo systemctl reload nginx

At present, it is associated with a little-used static toy gaming website:

- [https://sfp.genuinemerit.org/saskan](https://sfp.genuinemerit.org/saskan)

Will eventually set up a new certbot, etc. just for saskan web-hosted assets.
