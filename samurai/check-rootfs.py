#!/usr/bin/env python3
"""Check a newly built offline root tree; never start its hardware services."""
from pathlib import Path
import argparse,base64,hashlib,json,os,re,struct,subprocess,tomllib
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--root',type=Path,required=True)
p.add_argument('--packages',type=Path,required=True,help='This build packages/edge directory')
p.add_argument('--user',default='user')
p.add_argument('--require-maintenance-clean',action='store_true')
a=p.parse_args();root=a.root.resolve();packages=a.packages.resolve()
if root==Path('/') or not (root/'etc/alpine-release').is_file():p.error('Offline Alpine root required')
db=(root/'lib/apk/db/installed').read_text()
records={};file_checks=[];selected=set()
required=['device-realme-samurai','device-realme-samurai-kernel-none','samurai-camera-config','samurai-camera-stack',
 'libcamera','libcamera-ipa','libcamera-tools','libcamera-gstreamer','libcamera-v4l2',
 'mesa-vulkan-freedreno-samurai','modemmanager','libmm-glib','geoclue','pipewire','pipewire-libs',
 'pipewire-spa-libcamera','gst-plugin-pipewire','samurai-libssc','samurai-hexagonrpcd',
 'samurai-radio-tools','samurai-platform','samurai-gnss-assist','samurai-ssc','samurai-openrc','samurai-desktop']
for block in db.split('\n\n'):
 row={}
 for line in block.splitlines():
  k,sep,v=line.partition(':')
  if k in ['P','V','A','o','c']:row[k]=v
 if 'P' in row:records[row['P']]=row
for name in required:
 assert name in records,'Missing package: '+name
 row=records[name]
 apk=name+'-'+row['V']+'.apk'
 assert any((directory/apk).is_file() for directory in [packages,packages/'aarch64',packages/'noarch']),apk
 selected.add(name)
checks=0;elfs=0;mutations=[]
for block in db.split('\n\n'):
 current='';directory='';path=None
 for line in block.splitlines():
  k,sep,value=line.partition(':')
  if k=='P':current=value
  elif k=='F':directory=value
  elif k=='R':path=directory+'/'+value
  elif k=='Z' and current in selected and path:
   f=root/path
   assert f.exists() or f.is_symlink(),'Missing installed file: '+path
   if path=='etc/greetd/samurai-phosh.toml':mutations.append(path);continue
   if not f.is_file() or f.is_symlink():continue
   if value.startswith(('Q1','Q2')):
    data=f.read_bytes();algorithm='sha1' if value[:2]=='Q1' else 'sha256'
    assert hashlib.new(algorithm,data).digest()==base64.b64decode(value[2:]),'Package file changed: '+path
    checks+=1
    if data.startswith(bytes([127])+b'ELF'):
     assert data[4:6]==bytes([2,1]) and struct.unpack('<H',data[18:20])[0]==183,'Non-ARM64 ELF: '+path
     elfs+=1
assert checks>50,'Unrecognized installed-file checksum format'
greet=tomllib.loads((root/'etc/greetd/samurai-phosh.toml').read_text())
assert greet['initial_session']['user']==a.user
assert greet['initial_session']['command']=='/usr/bin/samurai-phosh-session'
assert re.search(r'^rc_need=.*dbus iio-sensor-proxy', (root/'etc/conf.d/greetd').read_text(), re.M)
entries=[line.split(':') for line in (root/'etc/passwd').read_text().splitlines()]
home=root/next(row[5].lstrip('/') for row in entries if row[0]==a.user)
for relative in ['applications/org.gnome.Snapshot.desktop','dbus-1/services/org.gnome.Snapshot.service']:
 assert (home/'.local/share'/relative).read_bytes()==(root/'usr/share/samurai/user-config'/relative).read_bytes()
for service in ['samurai-radio','samurai-usb','samurai-loopback','sshd','bluetooth','elogind','iio-sensor-proxy',
 'greetd','samurai-ssc','samurai-gnss-assist','networkmanager','chronyd','postmarketos-zram-swap']:
 assert (root/'etc/init.d'/service).is_file(),service
 assert any((root/'etc/runlevels'/level/service).is_symlink() for level in ['boot','default']),service
for command in ['usr/lib/bluetooth/bluetoothd','usr/libexec/elogind/elogind','usr/libexec/iio-sensor-proxy',
 'usr/libexec/phrog-greetd-session','usr/sbin/sshd.pam','usr/libexec/samurai-hexagonrpcd','usr/sbin/samurai-usb','usr/bin/samurai-phosh-session']:
 assert (root/command).is_file(),'Missing service executable: '+command
# Integrity manifests were generated after linking; they must survive packaging.
for name in ['ssc-library','ssc-daemon']:
 for line in (root/f'usr/share/samurai/{name}.sha256').read_text().splitlines():
  digest,path=line.split('  ',1)
  assert hashlib.sha256((root/path.lstrip('/')).read_bytes()).hexdigest()==digest,name
# Load public Python GI namespaces without opening a QMI client or location session.
result=subprocess.run(['chroot',str(root),'/usr/bin/python3','-c',
 "import gi; gi.require_version('Qmi','1.0'); from gi.repository import GLib,Qmi; print('GI-QMI-load-ok')"],
 capture_output=True,text=True)
assert result.returncode==0,result.stderr
legacy=[]
for f in (root/'etc/modprobe.d').glob('*.conf'):
 if 'experimental_p_imx319_power' in f.read_text():legacy.append(f.relative_to(root).as_posix())
report={'installed_package_count':len(records),'custom_packages':{n:records[n]['V'] for n in required},
 'installed_files_verified':checks,'arm64_elfs_verified':elfs,'intentional_template_mutations':mutations,
 'gi_qmi_namespace_loaded':True,'legacy_power_profile':legacy,
 'kernel_maintenance_cleanliness':'requires separate source review; not established by this check',
 'hardware_tested':False}
print(json.dumps(report,indent=2))
if a.require_maintenance_clean and legacy:raise SystemExit('Legacy power profile remains; this is a bring-up baseline')
