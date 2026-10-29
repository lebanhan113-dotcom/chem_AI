"""V4.2 instructional media regression checks (no AI credentials required)."""
import json
import subprocess
from pathlib import Path
from fastapi.testclient import TestClient
import server

ROOT=Path(__file__).resolve().parents[1]

def guides():
    text=(ROOT/'static'/'guides.js').read_text(encoding='utf-8')
    return json.loads(text.split('const HELP_GUIDES = ',1)[1].removesuffix(';\n'))

def test_all_21_video_guides_exist_and_match_topics():
    data=guides()
    assert len(data)==21
    assert sum(g['kind']=='type' for g in data)==12
    assert sum(g['kind']=='stage' for g in data)==8
    assert sum(g['kind']=='overview' for g in data)==1
    for g in data:
        video=ROOT/'static'/'tutorials'/g['video']
        assert video.is_file() and video.stat().st_size>40000
        assert len(g['steps'])==3

def test_tutorials_have_valid_mp4():
    for g in guides():
        target=ROOT/'static'/'tutorials'/g['video']
        result=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(target)],capture_output=True,text=True,check=True)
        assert 15.5<float(result.stdout.strip())<16.5

def test_help_available_on_root_and_static_mp4_served():
    with TestClient(server.app) as client:
        text=client.get('/index.html').text
        assert 'id="help"' in text
        assert 'Hướng dẫn sử dụng' in text
        assert 'id="finalUsage"' in text
        assert 'const HELP_GUIDES' in text
        resp=client.get('/static/tutorials/'+guides()[0]['video'])
        assert resp.status_code==200
        assert resp.headers['content-type'].startswith('video/mp4')
        assert len(resp.content)>40000
