# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['UImain.py'],
    pathex=['book_epub_reader.py', 'book_excel_import.py', 'book_single_entry.py', 'book_editor.py','todo_create.py','todo_edit.py','todo_query.py','todo_search.py','file_helper.py','constant.py'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='UImain',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
