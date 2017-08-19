# Vlc

**run vlc via root**
```bash
sudo sed -i 's/geteuid/getppid/' /usr/bin/vlc
```
