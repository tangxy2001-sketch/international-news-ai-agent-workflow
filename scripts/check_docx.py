#!/usr/bin/env python3
"""Validate generated OOXML and expected presentation formatting."""
import sys
import zipfile
import xml.etree.ElementTree as ET
with zipfile.ZipFile(sys.argv[1]) as archive:
    assert archive.testzip() is None, '损坏的 ZIP'
    for name in archive.namelist():
        if name.endswith(('.xml','.rels')):
            ET.fromstring(archive.read(name))
    document = ET.fromstring(archive.read('word/document.xml'))
ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
assert document.findall('.//w:hyperlink',ns), '缺少来源超链接'
assert document.findall('.//w:highlight',ns), '缺少引用段高亮'
assert '\ufffd' not in ''.join(document.itertext()), '存在乱码'
print('DOCX 容器、XML、超链接和高亮检查通过。')
