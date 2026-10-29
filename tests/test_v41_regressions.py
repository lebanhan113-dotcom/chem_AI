import copy
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
import settings as cfg
import store
import workflow as wf

CFG={'subject':'Hóa học','grade':10,'title':'Phản ứng oxi hóa khử','content':'Zn nhường electron, Cu2+ nhận electron.','video_type':'Mô phỏng hiện tượng','duration':24,'style':'Khoa học','character_mode':'Không có nhân vật','subtitles':False}
SC={'goal':'Giải thích hiện tượng','environment':'Phòng thí nghiệm','characters':'Không có nhân vật','action':'Quan sát','expression':'Không có','props':'Cốc','shot':'Cận cảnh','camera_motion':'Tĩnh','lighting':'Sáng','sound':'Giọng đọc','dialogue':'Kẽm nhường electron.','start_point':'Dụng cụ tĩnh','end_point':'Dung dịch có biến đổi'}
@pytest.fixture
def sample(tmp_path,monkeypatch):
    monkeypatch.setattr(cfg,'DATA_DIR',tmp_path)
    monkeypatch.setattr(cfg,'DB_PATH',tmp_path/'tests.sqlite3')
    monkeypatch.setattr(store,'DB_PATH',tmp_path/'tests.sqlite3')
    store.init()
    p=wf.new_project(CFG)
    p['scenes']=wf.make_scenes(p,{'scenes':[dict(SC) for _ in range(3)]})
    p['bible']={'lock_id':'bible1','character_bible':'NO_CHARACTER','environment_bible':'Phòng lab'}
    for i,s in enumerate(p['scenes']):
        s['image_prompt']=f'image_{i}';s['video_prompt']=f'video_{i}'
    return store.save(p)

def test_start_end_and_lock(sample):
    scenes=sample['scenes']
    assert scenes[1]['continuity_from']==scenes[0]['end_state']
    assert scenes[2]['dialogue_locked']
    assert scenes[0]['dialogue_hash']==wf.digest(scenes[0]['dialogue'])

def test_edit_end_state_only_invalidates_successor(sample):
    s1,s2,s3=sample['scenes']
    s3['accepted']=True;s3['status']='ACCEPTED';s3['video_file']='keep_third.mp4'
    store.save(sample)
    changed=wf.edit_scene(sample['id'],s1['id'],{'end_state':'Đồng bắt đầu xuất hiện'})
    assert changed['scenes'][1]['continuity_from']=='Đồng bắt đầu xuất hiện'
    assert changed['scenes'][1]['image_prompt']==''
    assert changed['scenes'][1]['video_prompt']==''
    assert changed['scenes'][2]['video_file']=='keep_third.mp4'
    assert changed['scenes'][2]['accepted']

def test_prompt_partial_update_preserves_other_scenes(sample,monkeypatch):
    p=sample
    first=p['scenes'][0]
    first['image_prompt']=''
    p['steps']['7']='READY';p['steps']['8']='COMPLETED'
    calls=[]
    def fake_ask(task,payload,fields):
        assert len(payload['scenes_to_update'])==1
        calls.append(payload['scenes_to_update'][0]['id'])
        return {'prompts':[{'scene_id':first['id'],'image_prompt':'ONLY_FIRST_NEW'}]}
    monkeypatch.setattr(wf,'ask',fake_ask)
    wf.steps_2_to_8.__globals__['ask']=fake_ask
    for n in range(2,7):p['steps'][str(n)]='COMPLETED'
    wf.steps_2_to_8(p)
    assert calls==[first['id']]
    assert p['scenes'][0]['image_prompt']=='ONLY_FIRST_NEW'
    assert p['scenes'][1]['image_prompt']=='image_1'
    assert p['scenes'][2]['video_prompt']=='video_2'

def test_metadata_change_preserves_scenes_and_finished_video(sample):
    sample['video']={'file':'/old/finished.mp4'}
    sample['status']='COMPLETED'
    store.save(sample)
    p=wf.update_input(sample['id'],{**CFG,'title':'Tên mới'})
    assert p['title']=='Tên mới'
    assert len(p['scenes'])==3
    assert p['video']['file']=='/old/finished.mp4'
    assert p['status']=='COMPLETED'

def test_subtitles_change_keeps_clips(sample):
    sample['scenes'][1]['video_file']='myclip.mp4';sample['video']={'file':'old.mp4'}
    store.save(sample)
    p=wf.update_input(sample['id'],{**CFG,'subtitles':True})
    assert p['scenes'][1]['video_file']=='myclip.mp4'
    assert p['video'] is None
    assert p['status']=='AWAITING_ACCEPTANCE'

def test_accept_image_reference_only_selected(sample,tmp_path):
    source=tmp_path/'some.png';source.write_bytes(b'fake bytes')
    sample['scenes'][1]['image_file']=str(source)
    store.save(sample)
    out=wf.accept_scene_image(sample['id'],'SCENE_002')
    assert out['scenes'][1]['image_accepted']
    assert out['reference_lock']['primary']['scene_id']=='SCENE_002'
    assert not out['scenes'][0]['image_accepted']
    public=wf.summarize(out)
    assert 'image_file' not in public['reference_lock']['primary']

def test_dialogue_fingerprint_prevents_silent_change(sample,tmp_path):
    scene=sample['scenes'][0]
    fake=tmp_path/'ref.png';fake.write_bytes(b'pixel data placeholder')
    scene['image_file']=str(fake)
    scene['dialogue']='Lời thoại đổi ngầm.'
    with pytest.raises(wf.WorkflowError,match='Lời thoại'):
        wf.scene_render_payload(sample,scene)


def test_edit_video_prompt_keeps_image_and_other_scenes(sample):
    first=sample['scenes'][0]
    first.update({'image_file':'keep_image.png','video_file':'remove_clip.mp4','accepted':True,'status':'ACCEPTED'})
    second=sample['scenes'][1]
    second.update({'image_file':'other_image.png','video_file':'other_clip.mp4','accepted':True,'status':'ACCEPTED'})
    store.save(sample)
    changed=wf.edit_scene(sample['id'],first['id'],{'video_prompt':'prompt riêng mới'})
    assert changed['scenes'][0]['image_file']=='keep_image.png'
    assert changed['scenes'][0]['video_file'] is None
    assert changed['scenes'][1]['video_file']=='other_clip.mp4'
    assert changed['scenes'][1]['accepted']


def test_api_image_approval_route(sample,tmp_path):
    from fastapi.testclient import TestClient
    import server
    sample['scenes'][0]['image_file']=str(tmp_path/'sample.png')
    Path(sample['scenes'][0]['image_file']).write_bytes(b'fake')
    store.save(sample)
    with TestClient(server.app) as client:
        r=client.post(f"/api/projects/{sample['id']}/scenes/{sample['scenes'][0]['id']}/accept-image")
        assert r.status_code==200, r.text
        assert r.json()['scenes'][0]['image_accepted']
