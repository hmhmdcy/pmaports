#!/usr/bin/env python3
"""Check published local source hashes, syntax, and deployment-path independence."""
from pathlib import Path
import ast,hashlib,json,re,subprocess
root=Path(__file__).resolve().parents[1]
recipes=[root/'cross/crossdirect',root/'temp/libcamera',root/'temp/modemmanager']
recipes+=sorted((root/'device/testing').glob('samurai-*'))
recipes+=[root/'device/testing/mesa-vulkan-freedreno-samurai',root/'device/testing/device-realme-samurai']
hashes=0;checked=0
for directory in recipes:
 recipe=(directory/'APKBUILD').read_text()
 subprocess.run(['sh','-n',str(directory/'APKBUILD')],check=True)
 for digest,name in re.findall(r'^([0-9a-f]{128})  (.+)$',recipe,re.M):
  p=directory/name
  if p.is_file():assert hashlib.sha512(p.read_bytes()).hexdigest()==digest,str(p);hashes+=1
 for p in directory.iterdir():
  if not p.is_file():continue
  data=p.read_bytes()
  assert not data.startswith(b'\x7fELF'),str(p)
  text=data.decode()
  assert '-----BEGIN PRIVATE KEY-----' not in text and '-----BEGIN OPENSSH PRIVATE KEY-----' not in text,str(p)
  assert '/home/cy122/' not in text and '/mnt/e/' not in text,str(p)
  assert not re.search(r'/var/lib/samurai/k[0-9]',text),str(p)
  if p.suffix=='.py' or text.startswith('#!/usr/bin/python3'):ast.parse(text)
  if text.startswith(('#!/bin/sh','#!/sbin/openrc-run')):subprocess.run(['sh','-n',str(p)],check=True)
  checked+=1
for p in (root/'samurai').glob('*.py'):ast.parse(p.read_text())
baseline=json.loads((root/'samurai/observed-packages-248.json').read_text())
assert len(baseline)==958
assert len(list((root/'temp/libcamera').glob('00*.patch')))==12
print(json.dumps({'recipes':len(recipes),'local_sha512_checks':hashes,'source_files_checked':checked,
 'observed_package_records':len(baseline),'private_build_paths_required':False,'hardware_tested':False},indent=2))
