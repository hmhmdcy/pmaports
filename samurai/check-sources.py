#!/usr/bin/env python3
"""Check published local source hashes, syntax, and deployment-path independence."""
from pathlib import Path
import ast,hashlib,json,re,subprocess
root=Path(__file__).resolve().parents[1]
recipes=[root/'cross/crossdirect',root/'temp/libcamera',root/'temp/modemmanager',root/'temp/geoclue',root/'temp/pipewire']
recipes+=sorted((root/'device/testing').glob('samurai-*'))
recipes+=[root/'device/testing/mesa-vulkan-freedreno-samurai',root/'device/testing/device-realme-samurai']
hashes=0;checked=0;key_scan=0;libcamera_patches=[]
private_build_path=re.compile(r'/(?:home/[A-Za-z0-9._-]+|mnt/[A-Za-z])/')
windows_user_path=re.compile(r'(?i)(?<![A-Za-z0-9])[A-Z]:\\Users\\[^\\\s]+')
private_key_header=re.compile(r'-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----|-----BEGIN PGP PRIVATE KEY BLOCK-----|PuTTY-User-Key-File')
for directory in recipes:
 recipe=(directory/'APKBUILD').read_text()
 subprocess.run(['sh','-n',str(directory/'APKBUILD')],check=True)
 # abuild expects the checksum sequence to follow source, not just contain
 # a correct filename-to-hash map. Parse these deliberately simple recipes
 # without evaluating APKBUILD shell code on the host.
 values={}
 for key in ['pkgname','pkgver','_pkgver','_commit','_tuning_files']:
  m=re.search(r'^'+key+r'=(?:"([^"]*)"|([^\n]+))',recipe,re.M)
  if m:values[key]=m[1] if m[1] is not None else m[2]
 def expand(text):
  for _ in range(5):
   text=re.sub(r'\$(?:\{([A-Za-z_][A-Za-z_0-9]*)\}|([A-Za-z_][A-Za-z_0-9]*))',
    lambda m:values.get(m[1] or m[2],m[0]),text)
  return text
 m=re.search(r'^source="([^"]*)"',recipe,re.M);assert m,str(directory)
 sources=expand(m[1]).split()
 source_names=[t.split('::',1)[0] if '::' in t else t.rsplit('/',1)[-1] for t in sources]
 checksum_names=re.findall(r'^[0-9a-f]{128}  (.+)$',recipe,re.M)
 assert source_names==checksum_names,'Source/checksum order mismatch: '+str(directory)
 if directory==root/'temp/libcamera':
  libcamera_patches=sorted(name for name in source_names if name.endswith('.patch'))
 for digest,name in re.findall(r'^([0-9a-f]{128})  (.+)$',recipe,re.M):
  p=directory/name
  if p.is_file():assert hashlib.sha512(p.read_bytes()).hexdigest()==digest,str(p);hashes+=1
 for p in directory.iterdir():
  if not p.is_file():continue
  data=p.read_bytes()
  assert not data.startswith(b'\x7fELF'),str(p)
  text=data.decode()
  assert not private_key_header.search(text),str(p)
  if p.suffix not in {'.patch','.diff'}:
   assert not private_build_path.search(text),str(p)
   assert not windows_user_path.search(text),str(p)
  assert not re.search(r'/var/lib/samurai/k[0-9]',text),str(p)
  if p.suffix=='.py' or text.startswith('#!/usr/bin/python3'):ast.parse(text)
  if text.startswith(('#!/bin/sh','#!/sbin/openrc-run')):subprocess.run(['sh','-n',str(p)],check=True)
  checked+=1
for p in root.rglob('*'):
 if not p.is_file() or p.is_symlink() or '.git' in p.parts or p.resolve()==Path(__file__).resolve():continue
 data=p.read_bytes()
 if b'\0' in data:continue
 assert not private_key_header.search(data.decode(errors='replace')),str(p)
 key_scan+=1
for p in (root/'samurai').glob('*.py'):ast.parse(p.read_text())
tool_patches=json.loads((root/'samurai/sources.json').read_text()).get('pmbootstrap_patches',[])
for item in tool_patches:
 p=root/'samurai'/item['path']
 assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],str(p)
lock=json.loads((root/'samurai/libcamera-source-lock.json').read_text())
libcamera_recipe=(root/'temp/libcamera/APKBUILD').read_text()
libcamera_rel=re.search(r'^pkgrel=([0-9]+)$',libcamera_recipe,re.M)[1]
camera_recipe=(root/'device/testing/samurai-camera-config/APKBUILD').read_text()
camera_ver=re.search(r'^pkgver=([^\n]+)$',camera_recipe,re.M)[1]
camera_rel=re.search(r'^pkgrel=([0-9]+)$',camera_recipe,re.M)[1]
assert lock['source_version']=='0.7.2'
assert lock['package_version']=='99990.7.2-r'+libcamera_rel
assert lock['configuration_version']==camera_ver+'-r'+camera_rel
assert lock['patch_count']==len(libcamera_patches)
sources=json.loads((root/'samurai/sources.json').read_text())
for name,commit in sources['kernel']['branches'].items():
 assert re.fullmatch(r'[0-9a-f]{40}',commit),(name,commit)
assert sources['kernel']['commit']==sources['kernel']['branches'][sources['kernel']['branch']]
baseline=json.loads((root/'samurai/observed-packages-248.json').read_text())
assert len(baseline)==958
assert len(libcamera_patches)==52
assert sorted(p.name for p in (root/'temp/libcamera').glob('00*.patch'))==libcamera_patches
print(json.dumps({'recipes':len(recipes),'local_sha512_checks':hashes,'source_files_checked':checked,
 'tool_patches_verified':len(tool_patches),'libcamera_patches':len(libcamera_patches),'private_key_scan_files':key_scan,'observed_package_records':len(baseline),
 'private_build_paths_required':False,'hardware_tested':False},indent=2))
