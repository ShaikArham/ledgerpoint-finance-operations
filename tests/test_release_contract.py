"""Release asset integrity and financial safeguards, independently of hosting."""
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]

def test_approved_assets_are_byte_identical():
    expected = {'ledgerpoint-intro-web.mp4': 'a10b7b287f45111f0361ce795bd35a30a653e0f876a08020dd395b5365359a8a', 'ledgerpoint-thumbnail.jpg': '6a71f302882d5ae4b48ab9e504e58c0c21a13b53238188efc31d2b73d984e79a', 'Shaik_Arham_Saquib_DataPoint.pdf': '3fedddde8052ac6e42a97f2755f8e74acaeb6441b8c4950e57a336ef676974a2', 'ledgerpoint-intro-en.vtt': '5dbbd622729da56182835b6f6953998ef6a891ddac1443d8b57366ae559a5312'}
    for name, checksum in expected.items():
        assert hashlib.sha256((ROOT / 'assets' / name).read_bytes()).hexdigest() == checksum

def test_caption_intervals_are_ordered_and_within_film():
    text = (ROOT / 'assets/ledgerpoint-intro-en.vtt').read_text()
    assert text.startswith('WEBVTT')
    intervals = re.findall(r'00:(\d\d):(\d\d)\.(\d{3}) --> 00:(\d\d):(\d\d)\.(\d{3})', text)
    assert len(intervals) == 12
    previous = 0
    for sm, ss, sms, em, es, ems in intervals:
        start = int(sm)*60+int(ss)+int(sms)/1000
        end = int(em)*60+int(es)+int(ems)/1000
        assert previous <= start < end <= 90
        previous = end
