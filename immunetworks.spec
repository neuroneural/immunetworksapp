# my_flask_app.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


added_files = [
    ('appresources', 'appresources'),
    ('resources', 'resources'),
]

a = Analysis(['app.py'],
             pathex=['.'],
             binaries=[],
             datas=added_files,
             hiddenimports=['flask', 'requests','nibabel','pandas','torch','numpy','torchvision'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='my_flask_app',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='my_flask_app')
