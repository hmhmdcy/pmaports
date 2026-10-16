#!/usr/bin/env python3
"""Configure a newly built offline root tree, without mounting or formatting."""
from pathlib import Path
import argparse,os,pwd,re,shutil,json,hashlib,uuid
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--root',type=Path,required=True)
p.add_argument('--user',default='user')
a=p.parse_args();root=a.root.resolve()
if root==Path('/') or not (root/'etc/alpine-release').is_file():p.error('An offline Alpine root directory is required')
if not re.fullmatch('[a-z_][a-z0-9_-]*',a.user):p.error('Invalid username')
assert not os.statvfs(root).f_flag & os.ST_RDONLY,'Destination must be a writable candidate, not a backup'
identity=root/'etc/machine-id'
assert not identity.is_symlink(),'Unexpected machine-id symlink'
if not identity.exists() or not identity.read_text().strip():
 identity.write_text(uuid.uuid4().hex+'\n')
assert re.fullmatch('[0-9a-f]{32}',identity.read_text().strip()),'Invalid installation identity'
entries=[s.split(':') for s in (root/'etc/passwd').read_text().splitlines()]
user=next(e for e in entries if e[0]==a.user)
home=root/user[5].lstrip('/');uid,gid=map(int,user[2:4])
source=root/'usr/share/samurai/user-config'
for pth in source.rglob('*'):
 if pth.is_file():
  dest=home/'.local/share'/pth.relative_to(source);dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists() and dest.read_bytes()!=pth.read_bytes():raise RuntimeError('Existing user override differs: '+str(dest))
  shutil.copyfile(pth,dest);os.chown(dest,uid,gid)
for directory in [home/'.local',home/'.local/share',*(home/'.local/share').rglob('*')]:
 if directory.is_dir():os.chown(directory,uid,gid)
greet=root/'etc/greetd/samurai-phosh.toml'
text=greet.read_text();assert '@USER@' in text or f'user="{a.user}"' in text
greet.write_text(text.replace('@USER@',a.user))
shutil.copyfile(root/'usr/share/samurai/greetd.confd',root/'etc/conf.d/greetd')
levels={'boot':['samurai-loopback','samurai-usb','sshd'],
 'default':['cgroups','dbus','elogind','samurai-radio','networkmanager','chronyd','bluetooth',
 'postmarketos-zram-swap','greetd','samurai-ssc','iio-sensor-proxy','samurai-gnss-assist']}
for level,names in levels.items():
 directory=root/'etc/runlevels'/level;directory.mkdir(parents=True,exist_ok=True)
 for name in names:
  assert (root/'etc/init.d'/name).is_file(),name
  dest=directory/name
  if not dest.is_symlink():
   assert not dest.exists(),str(dest)
   dest.symlink_to('/etc/init.d/'+name)
# Existing pmbootstrap USB gadget services must not race the Samurai gadget.
for directory in (root/'etc/runlevels').iterdir():
 if directory.is_dir():
  for name in ['usb-moded','postmarketos-usb']: 
   f=directory/name
   if f.is_symlink():f.unlink()
release=root/'etc/samurai-rootfs-release'
release.write_text('ROOTFS_ID=samurai-f2fs-rootfs01\nBUILD_PROFILE=github-pmaports-249\n')
# No credentials or machine identity are imported; set a personal login and SSH key before deployment.
print(json.dumps({'offline_configuration_complete':True,'firmware_provisioning_required':True,'hardware_tested':False}))
