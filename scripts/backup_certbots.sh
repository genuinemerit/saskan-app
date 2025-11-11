# detect how certbot is installed
command -v certbot || true
snap list certbot 2>/dev/null || true
dpkg -l | grep certbot 2>/dev/null || true

# create a safe tarball of certbot state
sudo tar -czvf /root/letsencrypt-backup-$(date +%Y%m%d).tgz \
  /etc/letsencrypt /var/lib/letsencrypt /var/log/letsencrypt 2>/dev/null || true

# verify
ls -lh /root/letsencrypt-backup-*.tgz
