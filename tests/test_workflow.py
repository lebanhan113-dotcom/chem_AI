import copy
import os
import subprocess
from pathlib import Path
import sys
import tempfile
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import settings as cfg
import store
import workflow as wf
from media import probe, merge

@pytest.fixture
def isolated(monkeypatch,tmp_path):
    monkeypatch.setattr(cfg,'DATA_DIR',tmp_path)
    monkeypatch.setattr(cfg,'DB_PATH',tmp_path/'test.sqlite3')
    monkeypatch.setattr(store,'DB_PATH',tmp_path/'test.sqlite3')
    store.init()
    yield tmp_path

CONFIG={'subject':'Hóa học','grade':10,'title':'Phản ứng oxi hóa - khử','content':'Zn + CuSO4 -> ZnSO4 + Cu. Kẽm nhường electron, Cu2+ nhận electron.','video_type':'Mô phỏng hiện tượng','duration':16,'style':'Khoa học – mô phỏng','character_mode':'Không có nhân vật','subtitles':False}
SCENE_BASE={'goal':'Kiểm tra hiện tượng','environment':'Phòng thí nghiệm','characters':'Không có nhân vật','action':'Mô phỏng thí nghiệm','expression':'Không có','props':'Cốc thủy tinh','shot':'Cận cảnh','camera_motion':'Tĩnh','lighting':'Sáng rõ','sound':'Giọng đọc tiếng Việt','dialogue':'Kẽm nhường electron và bị oxi hóa.','start_point':'Thanh kẽm ở đầu cảnh','end_point':'Ion đồng được khử'}

def test_validation_and_scene_count(isolated):
    p=wf.new_project(CONFIG)
    assert p['step']==1 and p['steps']['2']=='LOCKED'
    scenes=wf.make_scenes(p,{'scenes':[dict(SCENE_BASE),dict(SCENE_BASE)]})
    assert [s['id'] for s in scenes]==['SCENE_001','SCENE_002']
    assert scenes[-1]['end_time']==16
    with pytest.raises(wf.WorkflowError):wf.make_scenes(p,{'scenes':[dict(SCENE_BASE)]})
    bad={**CONFIG,'duration':13}
    with pytest.raises(wf.WorkflowError):wf.new_project(bad)

def test_edit_only_invalidates_selected_scene(isolated):
    p=wf.new_project(CONFIG)
    p['scenes']=wf.make_scenes(p,{'scenes':[dict(SCENE_BASE),dict(SCENE_BASE)]})
    p['bible']={'lock_id':'abc'}
    p['scenes'][0].update({'image_prompt':'prompt 1','video_prompt':'prompt 1','image_file':'/old/i1.png','video_file':'/old/v1.mp4','accepted':True,'status':'ACCEPTED'})
    p['scenes'][1].update({'image_prompt':'prompt 2','video_prompt':'prompt 2','image_file':'/old/i2.png','video_file':'/old/v2.mp4','accepted':True,'status':'ACCEPTED'})
    store.save(p)
    edited=wf.edit_scene(p['id'],'SCENE_001',{'action':'Cận cảnh kẽm hòa tan'})
    assert edited['scenes'][0]['image_file'] is None
    assert edited['scenes'][0]['video_file'] is None
    assert edited['scenes'][0]['image_prompt']==''
    assert edited['scenes'][0]['video_prompt']==''
    assert not edited['scenes'][0]['accepted']
    assert edited['scenes'][1]['video_file']=='/old/v2.mp4'
    assert edited['scenes'][1]['accepted']


def test_dialogue_edit_keeps_image_but_invalidates_video(isolated):
    p=wf.new_project(CONFIG)
    p['scenes']=wf.make_scenes(p,{'scenes':[dict(SCENE_BASE),dict(SCENE_BASE)]})
    s=p['scenes'][1];s['image_prompt']='img prompt';s['video_prompt']='video prompt';s['image_file']='/old/image.png';s['video_file']='/old/video.mp4';s['accepted']=True
    store.save(p)
    edited=wf.edit_scene(p['id'],s['id'],{'dialogue':'Ion đồng nhận electron và bị khử.'})
    assert edited['scenes'][1]['image_file']=='/old/image.png'
    assert edited['scenes'][1]['video_file'] is None
    assert edited['scenes'][1]['video_prompt']==''


def test_requires_all_accepted_before_merge(isolated):
    p=wf.new_project(CONFIG)
    p['scenes']=wf.make_scenes(p,{'scenes':[dict(SCENE_BASE),dict(SCENE_BASE)]})
    store.save(p)
    wf.process(p,mode='merge')
    after=store.get(p['id'])
    assert after['status']=='FAILED' and after['steps']['13']=='FAILED'
    assert after['video'] is None


def test_merge_local_ffmpeg_without_cutting(isolated):
    if not Path('/usr/bin/ffmpeg').is_file():pytest.skip('ffmpeg missing')
    clips=[]
    for i in (1,2):
        f=isolated/f'input{i}.mp4'
        cmd=['ffmpeg','-y','-loglevel','error','-f','lavfi','-i',f'color=c={"navy" if i==1 else "teal"}:s=640x360:r=24:d=8','-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration=8','-c:v','libx264','-preset','ultrafast','-c:a','aac','-shortest',str(f)]
        subprocess.run(cmd,check=True,timeout=60)
        clips.append(f)
    result=merge(clips,isolated/'final.mp4')
    assert 15.5 < result['duration'] < 16.5
    assert result['width']==1280 and result['height']==720
    assert result['audio']


def test_api_initial_input_no_fake_video(isolated,monkeypatch):
    # disable the real background queue to examine immediate API result
    from fastapi.testclient import TestClient
    import server
    monkeypatch.setattr(server.wf,'enqueue',lambda id,mode='full',scene_id=None: store.get(id))
    with TestClient(server.app) as client:
        r=client.post('/api/projects',json=CONFIG)
        assert r.status_code==200, r.text
        p=r.json(); assert p['video'] is None
        assert not any(s.get('video_url') for s in p['scenes'])
        assert client.get(f'/api/projects/{p["id"]}/download').status_code==404
        assert client.post(f'/api/projects/{p["id"]}/merge').status_code==409
        assert client.get('/').status_code==200


def test_optional_subtitle_file(isolated):
    from media import write_scene_subtitles
    scenes=[{'start_time':0,'end_time':8,'dialogue':'Kẽm nhường electron.'},{'start_time':8,'end_time':16,'dialogue':'Ion đồng nhận electron.'}]
    f=write_scene_subtitles(scenes,isolated/'subtitles.srt')
    text=f.read_text(encoding='utf-8')
    assert '00:00:00,150 --> 00:00:07,850' in text
    assert '00:00:08,150 --> 00:00:15,850' in text
    assert 'Ion đồng nhận electron.' in text


def test_edit_image_prompt_only_keeps_other_scene_and_requires_video_rewrite(isolated):
    p=wf.new_project(CONFIG)
    p['scenes']=wf.make_scenes(p,{'scenes':[dict(SCENE_BASE),dict(SCENE_BASE)]})
    p['scenes'][0].update({'image_prompt':'old img','video_prompt':'old video','image_file':'/old/pic.png','video_file':'/old/clip.mp4','accepted':True})
    p['scenes'][1].update({'image_prompt':'other img','video_prompt':'other video'})
    store.save(p)
    q=wf.edit_scene(p['id'],'SCENE_001',{'image_prompt':'new image prompt'})
    assert q['scenes'][0]['image_prompt']=='new image prompt'
    assert q['scenes'][0]['video_prompt']==''  # must be authored against the changed image
    assert q['scenes'][0]['image_file'] is None and q['scenes'][0]['video_file'] is None
    assert q['scenes'][1]['video_prompt']=='other video'
