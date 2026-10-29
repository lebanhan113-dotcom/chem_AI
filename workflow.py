"""Durable 14-step workflow; isolated scene invalidation, scene-specific retries."""
import copy
import hashlib
import json
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import settings as cfg
import store
from media import MediaError,probe,merge,write_scene_subtitles,burn_subtitles
from providers import ProviderError,gemini_json,make_image,submit_veo,poll_veo,store_veo_result

STEP_NAMES=['Nhận dữ liệu','Phân tích bài học','Xác định trọng tâm','Tạo kịch bản','Chia cảnh','Khóa Bible','Prompt ảnh','Prompt video','Tạo ảnh tham chiếu','Gửi sang Veo','Tạo video từng cảnh','Kiểm tra kết quả','Ghép video','Xuất MP4']
STAGE_INDICES=[[1,2,3],[4],[5,6],[7,8],[9],[10,11,12],[13],[14]]
_executor=ThreadPoolExecutor(max_workers=1,thread_name_prefix='eduvideo')
_active=set()
_guard=threading.RLock()

class WorkflowError(RuntimeError):pass

def digest(data):return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,default=str).encode()).hexdigest()

def validate_project_input(data):
    source=str(data.get('content','')).strip()
    if not source or len(source)>cfg.MAX_SOURCE_CHARS:raise WorkflowError(f'Nội dung bài học phải từ 1 đến {cfg.MAX_SOURCE_CHARS} ký tự')
    if str(data.get('grade','')) not in [str(i) for i in range(1,13)]:raise WorkflowError('Lớp không hợp lệ')
    if int(data.get('duration',0)) not in range(8,65,8):raise WorkflowError('Thời lượng phải là 8,16,...,64 giây')
    for key in ['subject','title','video_type','style','character_mode']:
        if not str(data.get(key,'')).strip():raise WorkflowError('Thiếu trường: '+key)

def new_project(data):
    validate_project_input(data)
    p={'id':uuid.uuid4().hex,'title':str(data['title']).strip()[:180], 'config':copy.deepcopy(data), 'step':1,'status':'READY', 'steps':{str(i):('COMPLETED' if i==1 else 'LOCKED') for i in range(1,15)},'analysis':None,'blueprint':None,'script':None,'bible':None,'reference_lock':{},'scenes':[],'video':None,'errors':[],'created_at':store.now(),'updated_at':store.now(),'version':1}
    return store.save(p)

def fail(p,step,exc,scene=None):
    msg=str(exc)[:1200]
    p['errors'].append({'at':store.now(),'step':step,'scene_id':scene,'message':msg})
    if scene:
        s=find_scene(p,scene);s['status']='FAILED';s['error']=msg
    p['status']='FAILED';p['steps'][str(step)]='FAILED'
    store.save(p)

def mark(p,step,status):
    p['step']=step;p['steps'][str(step)]=status
    p['status']='RUNNING' if status=='RUNNING' else p['status']
    store.save(p)

def step_done(p,step):
    p['steps'][str(step)]='COMPLETED'
    if step<14 and p['steps'][str(step+1)]=='LOCKED':p['steps'][str(step+1)]='READY'
    p['step']=step;p['status']='RUNNING'
    store.save(p)

def required(obj,names,where='response'):
    if not isinstance(obj,dict) or any(k not in obj for k in names):
        raise WorkflowError(f'{where} thiếu các trường bắt buộc: {names}')
    return obj

def ask(task,payload,fields):
    for attempt in range(2):
        obj=gemini_json(task,payload)
        try:return required(obj,fields)
        except WorkflowError:
            if attempt:raise
    raise WorkflowError('Gemini chưa tạo đúng cấu trúc')

def script_payload(p):
    return {'config':p['config'],'analysis':p['analysis'],'blueprint':p['blueprint']}

def find_scene(p,scene_id):
    scene=next((x for x in p['scenes'] if x['id']==scene_id),None)
    if not scene:raise WorkflowError('Không tìm thấy Scene ID')
    return scene

def make_scenes(p,obj):
    arr=obj.get('scenes')
    count=p['config']['duration']//8
    if not isinstance(arr,list) or len(arr)!=count:raise WorkflowError(f'Gemini phải tạo chính xác {count} cảnh')
    required_scene=['goal','environment','characters','action','expression','props','shot','camera_motion','lighting','sound','dialogue','start_point','end_point']
    scenes=[]
    for i,item in enumerate(arr):
        required(item,required_scene,'cảnh')
        if len(str(item['dialogue']).split())>26:raise WorkflowError(f'Lời thoại cảnh {i+1} quá dài cho 8 giây')
        item={k:(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False)) for k,v in item.items()}
        item['start_state']=item.get('start_state') or item['start_point']
        item['end_state']=item.get('end_state') or item['end_point']
        s={**item,'id':f'SCENE_{i+1:03d}','order':i+1,'start_time':8*i,'end_time':8*(i+1),'duration':8,'image_prompt':'','video_prompt':'','image_file':None,'video_file':None,'image_version':0,'video_version':0,'accepted':False,'status':'DRAFT','error':None,'render_job':None,'render_fingerprint':None, 'render_started_at':None,'version':1,'dialogue_locked':True,'dialogue_hash':digest(item['dialogue']),'image_accepted':False}
        if i>0:
            s['continuity_from']=scenes[-1]['end_state']
        else:
            s['continuity_from']='START_OF_VIDEO'
        scenes.append(s)
    return scenes

def steps_2_to_8(p):
    conf=p['config']
    if p['steps']['2']!='COMPLETED':
        mark(p,2,'RUNNING')
        p['analysis']=ask('Phân tích bài học, trả keys: summary, learning_objectives (array), core_knowledge (array), misconceptions (array), uncertainties (array), chemistry_checks (array). Duy trì đúng nội dung nguồn.',conf,['summary','learning_objectives','core_knowledge','uncertainties'])
        step_done(p,2)
    if p['steps']['3']!='COMPLETED':
        mark(p,3,'RUNNING')
        p['blueprint']=ask('Trả keys: main_message, learning_goal, video_structure (array), scope_limits (array), style_adaptation, character_adaptation. Chọn nội dung có thể diễn đạt trong thời lượng ngắn.',{'config':conf,'analysis':p['analysis']},['main_message','learning_goal','video_structure'])
        step_done(p,3)
    if p['steps']['4']!='COMPLETED':
        mark(p,4,'RUNNING')
        p['script']=ask('Viết kịch bản video tổng thể: keys synopsis, full_script, visual_direction, narration_direction, ending. Hạn chế lời thoại phù hợp thời lượng; không bịa kiến thức, chuyển công thức sang overlay hậu kỳ.',script_payload(p),['synopsis','full_script','visual_direction'])
        step_done(p,4)
    if p['steps']['5']!='COMPLETED':
        mark(p,5,'RUNNING')
        n=conf['duration']//8
        task=f'Tách chính xác {n} cảnh, mỗi cảnh 8 giây. Trả key scenes là array {n} object. TỪNG object PHẢI có: goal, environment, characters, action, expression, props, shot, camera_motion, lighting, sound, dialogue, start_point, end_point. Lời thoại không quá 22 từ/cảnh, không có gián đoạn. Cung cấp thêm start_state và end_state mô tả trạng thái nhân vật, đạo cụ, bối cảnh; start_state của cảnh sau phải kế thừa end_state của cảnh trước (nếu chuyển bối cảnh, ghi lý do rõ trong action). Không tạo chữ/công thức lên ảnh; đề xuất chèn đồ họa hậu kỳ nếu cần.'
        arr=ask(task,{'config':conf,'analysis':p['analysis'],'blueprint':p['blueprint'],'script':p['script']},['scenes'])
        p['scenes']=make_scenes(p,arr)
        step_done(p,5)
    if p['steps']['6']!='COMPLETED':
        mark(p,6,'RUNNING')
        p['bible']=ask('Tạo bộ bible thống nhất cho toàn video với keys character_bible, environment_bible, visual_style_bible, voice_bible, audio_bible. Nếu video không có nhân vật: character_bible = NO_CHARACTER. Hãy mô tả đặc điểm cố định, giọng tiếng Việt, không tự thêm phụ đề.',{'config':conf,'scenes':p['scenes'],'analysis':p['analysis']},['character_bible','environment_bible','visual_style_bible','voice_bible','audio_bible'])
        p['bible']['lock_id']=digest(p['bible']);p['bible']['version']=p['version']
        p.setdefault('reference_lock',{})
        step_done(p,6)
    if p['steps']['7']!='COMPLETED':
        mark(p,7,'RUNNING')
        missing=[s for s in p['scenes'] if not s.get('image_prompt')]
        if missing:
            ids=[s['id'] for s in missing]
            obj=ask('Viết prompt ảnh tiếng Anh chỉ cho các Scene ID được yêu cầu; trả prompts = array {scene_id,image_prompt} có đủ và chỉ các ID đó. 16:9, dùng bible khóa, start_state, end_state và continuity_from. Không thay lời thoại, không sinh chữ/phụ đề.',{'config':conf,'bible':p['bible'],'scenes_to_update':missing,'all_scene_continuity':[{k:v for k,v in sc.items() if k in ('id','start_state','end_state','continuity_from','environment','characters')} for sc in p['scenes']]},['prompts'])
            attach_prompts(p,obj,'image',scope_ids=ids)
        step_done(p,7)
    if p['steps']['8']!='COMPLETED':
        mark(p,8,'RUNNING')
        missing=[s for s in p['scenes'] if not s.get('video_prompt')]
        if missing:
            ids=[s['id'] for s in missing]
            obj=ask('Viết prompt video tiếng Anh chỉ cho các Scene ID được yêu cầu; trả prompts = array {scene_id,video_prompt} đủ và chỉ các ID đó. 8 giây, 16:9, bối cảnh và nhân vật không đổi, kế thừa start_state/end_state/continuity_from. Lời thoại ĐÃ KHÓA trong Scene: KHÔNG sửa, thêm hay đảo thoại. Không thêm chữ/phụ đề khi không được yêu cầu.',{'config':conf,'bible':p['bible'],'scenes_to_update':missing,'all_scene_continuity':[{k:v for k,v in sc.items() if k in ('id','start_state','end_state','continuity_from','environment','characters')} for sc in p['scenes']]},['prompts'])
            attach_prompts(p,obj,'video',scope_ids=ids)
        step_done(p,8)

def attach_prompts(p,obj,kind,scope_ids=None):
    prompts=obj.get('prompts')
    expected=set(scope_ids) if scope_ids is not None else {s['id'] for s in p['scenes']}
    if not isinstance(prompts,list) or len(prompts)!=len(expected):
        raise WorkflowError('Thiếu hoặc thừa prompt trong danh sách cảnh cần cập nhật')
    mapping={}
    for x in prompts:
        required(x,['scene_id',f'{kind}_prompt'])
        if x['scene_id'] in mapping:raise WorkflowError('Trùng Scene ID trong prompt')
        mapping[x['scene_id']]=str(x[f'{kind}_prompt']).strip()
    if set(mapping)!=expected or not all(mapping.values()):raise WorkflowError('Prompt không khớp Scene ID cần cập nhật')
    for scene in p['scenes']:
        if scene['id'] in expected:scene[f'{kind}_prompt']=mapping[scene['id']]
    store.save(p)

def scene_path(p,scene,kind):
    ext='png' if kind=='image' else 'mp4'
    ver=scene[f'{kind}_version']+1
    return store.file_dir(p['id'])/scene['id']/f'{kind}_v{ver}.{ext}'

def image_one(p,scene):
    if not scene['image_prompt'] or not p['bible'] or not scene['video_prompt']:
        raise WorkflowError('Thiếu prompt/Bible cho ảnh')
    scene['status']='IMAGE_RUNNING';scene['error']=None
    store.save(p)
    imgpath=scene_path(p,scene,'image')
    previous=None
    if scene['order']>1:
        prev=p['scenes'][scene['order']-2]
        if prev.get('image_file') and Path(prev['image_file']).is_file():previous=prev['image_file']
    locked=p.get('reference_lock') or {}
    references=[]
    for ref in locked.values():
        if isinstance(ref,dict) and ref.get('image_file') and Path(ref['image_file']).is_file():
            references.append(ref['image_file'])
    prompt=f'{scene["image_prompt"]}\nLOCKED BIBLE (do not change): {json.dumps(p["bible"],ensure_ascii=False)}\nScene action: {scene["action"]}\nSTART STATE: {scene.get("start_state",scene.get("start_point"))}\nEND STATE: {scene.get("end_state",scene.get("end_point"))}\nCONTINUITY FROM PREVIOUS: {scene.get("continuity_from","")}\n16:9, no subtitles, no textual formulas. Use reference images to preserve identity and environment; do not clone previous frame.'
    result=make_image(prompt,imgpath,previous=previous,references=references)
    scene['image_version']+=1
    scene['image_accepted']=False
    scene['image_file']=result
    scene['video_file']=None
    scene['render_job']=None
    scene['render_fingerprint']=None
    scene['accepted']=False
    scene['status']='IMAGE_READY'
    store.save(p)

def scene_render_payload(p,scene):
    if not scene.get('image_file') or not Path(scene['image_file']).is_file():raise WorkflowError('Chưa có ảnh cảnh')
    if not scene.get('video_prompt') or not scene.get('dialogue'):raise WorkflowError('Thiếu video prompt hoặc lời thoại')
    if not scene.get('dialogue_locked',True) or scene.get('dialogue_hash',digest(scene['dialogue']))!=digest(scene['dialogue']):
        raise WorkflowError('Lời thoại không khớp phiên bản khóa; cần lưu lại kịch bản cảnh')
    bible=p.get('bible') or {}
    payload={'scene_id':scene['id'],'bible_lock_id':bible.get('lock_id'), 'image_file_sha':hashlib.sha256(Path(scene['image_file']).read_bytes()).hexdigest(),'video_prompt':scene['video_prompt'],'dialogue':scene['dialogue'],'script_version':scene['version'],'start_state':scene.get('start_state'),'end_state':scene.get('end_state'),'continuity_from':scene.get('continuity_from')}
    prompt=scene['video_prompt']+f'\nStart state: {scene.get("start_state",scene.get("start_point"))}; End state: {scene.get("end_state",scene.get("end_point"))}; Previous ending: {scene.get("continuity_from","")}.\nExact Vietnamese speech, with natural pronunciation: "{scene["dialogue"]}". Preserve all spoken words. Maintain visual and voice rules: {json.dumps({"character":bible.get("character_bible"),"environment":bible.get("environment_bible"),"voice":bible.get("voice_bible"),"audio":bible.get("audio_bible"),"visual":bible.get("visual_style_bible")},ensure_ascii=False)}. Duration exactly 8 seconds. NO subtitles, watermarks, onscreen labels or extra dialogue unless specifically requested.'
    return digest(payload),prompt

def video_one(p,scene):
    if not scene['image_file']:raise WorkflowError('Không được tạo video khi chưa có ảnh')
    fingerprint,prompt=scene_render_payload(p,scene)
    if scene.get('render_job') and scene.get('render_fingerprint')==fingerprint:
        job=scene['render_job']
    else:
        scene['status']='SUBMITTING';scene['error']=None;store.save(p)
        job=submit_veo(prompt,scene['image_file'])
        scene['render_job']=job;scene['render_fingerprint']=fingerprint;scene['render_started_at']=time.time();store.save(p)
    scene['status']='RENDERING';store.save(p)
    started=scene.get('render_started_at') or time.time()
    while time.time()-started<cfg.VEO_WAIT_SECONDS:
        response=poll_veo(job)
        if response.get('done'):
            dest=scene_path(p,scene,'video')
            store_veo_result(response,dest)
            info=probe(dest)
            if not 7.2 <= max(info['duration'],info['audio_duration']) <= 8.8:
                raise WorkflowError(f'Video {scene["id"]} có thời lượng {info["duration"]:.2f}s, không đủ điều kiện ghép an toàn')
            _,current_prompt=scene_render_payload(p,scene)
            current_fp=digest({'scene_id':scene['id'],'bible_lock_id':p['bible']['lock_id'],'image_file_sha':hashlib.sha256(Path(scene['image_file']).read_bytes()).hexdigest(),'video_prompt':scene['video_prompt'],'dialogue':scene['dialogue'],'script_version':scene['version'],'start_state':scene.get('start_state'),'end_state':scene.get('end_state'),'continuity_from':scene.get('continuity_from')})
            if current_fp!=fingerprint:raise WorkflowError('Dữ liệu đã đổi trong lúc render. Không dùng clip phiên bản cũ.')
            scene['video_version']+=1;scene['video_file']=str(dest);scene['status']='VIDEO_READY';scene['accepted']=False;scene['render_job']=None
            store.save(p)
            return
        time.sleep(cfg.VEO_POLL_SECONDS)
    raise ProviderError('Veo vượt thời gian chờ. Mã tác vụ đã được lưu, thử lại để tiếp tục truy vấn, không gửi trùng job.',True)

def process(p,mode='full',scene_id=None):
    try:
        if mode=='full':
            steps_2_to_8(p)
            for step in [9,10,11,12]:
                if p['steps'][str(step)]!='COMPLETED':mark(p,step,'RUNNING')
                if step==9:
                    for scene in p['scenes']:
                        if not scene['image_file'] or not Path(scene['image_file']).exists():image_one(p,scene)
                elif step==10:
                    for scene in p['scenes']:
                        scene_render_payload(p,scene)
                elif step==11:
                    for scene in p['scenes']:
                        if not scene['video_file'] or not Path(scene['video_file']).exists():video_one(p,scene)
                else:
                    for scene in p['scenes']:
                        if not scene['video_file'] or not Path(scene['video_file']).exists():raise WorkflowError('Còn cảnh thiếu video')
                        probe(scene['video_file'])
                step_done(p,step)
            p['status']='AWAITING_ACCEPTANCE';p['step']=12;store.save(p)
        elif mode=='image':
            s=find_scene(p,scene_id)
            image_one(p,s)
            p['status']='AWAITING_ACCEPTANCE';refresh_scene_steps(p);store.save(p)
        elif mode=='video':
            s=find_scene(p,scene_id)
            video_one(p,s)
            p['status']='AWAITING_ACCEPTANCE';refresh_scene_steps(p);store.save(p)
        elif mode=='prompts':
            s=find_scene(p,scene_id)
            regenerate_scene_prompts(p,s)
            p['status']='AWAITING_ACCEPTANCE';refresh_scene_steps(p);store.save(p)
        elif mode=='merge':
            if not p['scenes'] or not all(s['accepted'] and s['status']=='ACCEPTED' and s['video_file'] and Path(s['video_file']).is_file() for s in p['scenes']):
                raise WorkflowError('Chưa chấp nhận đầy đủ các cảnh hợp lệ')
            mark(p,13,'RUNNING')
            ordered=sorted(p['scenes'],key=lambda s:s['order'])
            if [s['order'] for s in ordered]!=list(range(1,len(ordered)+1)):
                raise WorkflowError('Thứ tự cảnh không liên tục')
            dest=store.file_dir(p['id'])/'final'/f'EDUVIDEO_{p["id"]}_v{p["version"]}.mp4'
            result=merge([s['video_file'] for s in ordered],dest)
            step_done(p,13)
            mark(p,14,'RUNNING')
            subtitle_file=None
            if p['config'].get('subtitles'):
                subtitle_file=write_scene_subtitles(ordered,dest.parent/'captions.srt')
                subtitled=dest.parent/f'EDUVIDEO_{p["id"]}_v{p["version"]}_subtitled.mp4'
                result=burn_subtitles(dest,subtitled,subtitle_file)
                dest=subtitled
            probe(dest)
            p['video']={'file':str(dest),'subtitles_srt':str(subtitle_file) if subtitle_file else None,'duration':result['duration'],'width':result['width'],'height':result['height'],'created_at':store.now(),'version':p['version']}
            p['status']='COMPLETED';step_done(p,14);p['status']='COMPLETED';store.save(p)
        else:raise WorkflowError('Chế độ xử lý không hợp lệ')
    except Exception as exc:
        step=p.get('step',1)
        if mode in ('image','video','prompts'):
            step={'image':9,'video':11,'prompts':7}[mode]
        if mode=='merge':step=max(13,p.get('step',13))
        active_scene=scene_id
        if active_scene is None and mode=='full' and step in (9,10,11,12):
            candidates=[s for s in p.get('scenes',[]) if s.get('status') in ('IMAGE_RUNNING','SUBMITTING','RENDERING')]
            if candidates:active_scene=candidates[-1]['id']
        fail(p,step,exc,active_scene)

def enqueue(project_id,mode='full',scene_id=None):
    with _guard:
        if project_id in _active:raise WorkflowError('Dự án đang chạy một tác vụ khác')
        p=store.get(project_id)
        if not p:raise WorkflowError('Không tìm thấy dự án')
        _active.add(project_id)
        p['status']='QUEUED';store.save(p)
    def job():
        try:
            project=store.get(project_id)
            process(project,mode,scene_id)
        finally:
            with _guard:_active.discard(project_id)
    _executor.submit(job)
    return store.get(project_id)

def invalidate_scene(scene,level):
    scene['accepted']=False;scene['version']+=1;scene['error']=None
    if level in ('image','content'):scene['image_accepted']=False
    if level in ('image','content'):
        scene['image_file']=None;scene['image_version']=scene.get('image_version',0)
    if level in ('image','video','content'):
        scene['video_file']=None;scene['render_job']=None;scene['render_fingerprint']=None
    scene['status']='DRAFT' if level=='content' else ('PROMPTS_READY' if level=='image' else 'IMAGE_READY')

def refresh_scene_steps(p):
    """Recalculate global UI guards without changing valid scene outputs."""
    tests={7: lambda s:bool(s.get('image_prompt')),
           8: lambda s:bool(s.get('video_prompt')),
           9: lambda s:bool(s.get('image_file') and Path(s['image_file']).is_file()),
           10:lambda s:bool(s.get('image_file') and s.get('video_prompt')),
           11:lambda s:bool(s.get('video_file') and Path(s['video_file']).is_file()),
           12:lambda s:bool(s.get('video_file') and Path(s['video_file']).is_file())}
    for step,test in tests.items():
        if p['scenes']:
            p['steps'][str(step)]='COMPLETED' if all(test(s) for s in p['scenes']) else 'READY'
    if p.get('video') is None:
        p['steps']['13']='LOCKED';p['steps']['14']='LOCKED'

def regenerate_scene_prompts(p,s):
    if not p['bible'] or not p['script'] or not p['blueprint']:
        raise WorkflowError('Chưa có Bible và kịch bản khóa')
    contextual={'config':p['config'],'bible':p['bible'],'scene':{k:v for k,v in s.items() if k not in ['image_file','video_file','render_job']},'previous_scene':(p['scenes'][s['order']-2] if s['order']>1 else None),'next_scene':(p['scenes'][s['order']] if s['order']<len(p['scenes']) else None),'reference_lock':p.get('reference_lock',{})}
    obj=ask('Viết lại chính xác hai prompt riêng cho MỘT cảnh có Scene ID kèm theo, keys image_prompt và video_prompt (string). Giữ nguyên Bible; thoại đã khóa phải giữ nguyên văn, không tự viết lại hoặc thêm thoại; luôn dùng start_state/end_state và end_state cảnh trước làm continuity. Không tự thêm chữ/phụ đề. Ảnh 16:9, video 8 giây.',contextual,['image_prompt','video_prompt'])
    if not str(obj['image_prompt']).strip() or not str(obj['video_prompt']).strip():
        raise WorkflowError('Gemini trả prompt rỗng')
    invalidate_scene(s,'image')
    s['image_prompt']=obj['image_prompt'];s['video_prompt']=obj['video_prompt']
    s['status']='PROMPTS_READY'
    p['video']=None;p['version']+=1
    store.save(p)

def edit_scene(project_id,scene_id,patch):
    with _guard:
        if project_id in _active:raise WorkflowError('Đang xử lý, vui lòng chỉnh sửa sau khi tác vụ kết thúc')
        p=store.get(project_id)
        if not p:raise WorkflowError('Không tìm thấy dự án')
        s=find_scene(p,scene_id)
        allowed={'goal','environment','characters','action','expression','props','shot','camera_motion','lighting','sound','dialogue','start_point','end_point','start_state','end_state','image_prompt','video_prompt'}
        if not patch or any(k not in allowed for k in patch):raise WorkflowError('Trường chỉnh sửa không hợp lệ')
        for k,v in patch.items():
            if not isinstance(v,str) or not v.strip():raise WorkflowError('Giá trị chỉnh sửa không được rỗng: '+k)
        changed={k for k,v in patch.items() if s.get(k)!=v.strip()}
        if not changed:return p
        for k,v in patch.items():s[k]=v.strip()
        if 'dialogue' in changed:
            if len(s['dialogue'].split())>26:raise WorkflowError('Lời thoại quá dài cho 8 giây')
            s['dialogue_locked']=True;s['dialogue_hash']=digest(s['dialogue'])
        if 'start_point' in changed and 'start_state' not in changed:s['start_state']=s['start_point']
        if 'end_point' in changed and 'end_state' not in changed:s['end_state']=s['end_point']
        content_fields=allowed-{'image_prompt','video_prompt','dialogue'}
        if changed & content_fields:
            # Because the scene changed, old prompts must be authored again.
            if 'image_prompt' not in changed:s['image_prompt']=''
            if 'video_prompt' not in changed:s['video_prompt']=''
            invalidate_scene(s,'content')
        elif 'image_prompt' in changed:
            if 'video_prompt' not in changed:s['video_prompt']=''
            invalidate_scene(s,'image')
        else:
            if 'dialogue' in changed and 'video_prompt' not in changed:s['video_prompt']=''
            invalidate_scene(s,'video')
        # A changed ending only invalidates its direct successor (continuity dependency).
        if changed & {'end_state','end_point'} and s['order']<len(p['scenes']):
            successor=p['scenes'][s['order']]
            successor['continuity_from']=s['end_state']
            successor['image_prompt']='';successor['video_prompt']=''
            invalidate_scene(successor,'content')
        p['video']=None;p['version']+=1;p['status']='AWAITING_ACCEPTANCE'
        refresh_scene_steps(p)
        store.save(p)
        return p

def accept_scene_image(project_id,scene_id):
    """Explicit reference locking; locked references can be reused by later Nano Banana calls."""
    with _guard:
        if project_id in _active:raise WorkflowError('Dự án đang xử lý')
        p=store.get(project_id)
        if not p:raise WorkflowError('Không tìm thấy dự án')
        scene=find_scene(p,scene_id)
        path=scene.get('image_file')
        if not path or not Path(path).is_file():raise WorkflowError('Cảnh chưa có ảnh hợp lệ')
        scene['image_accepted']=True
        locks=p.setdefault('reference_lock',{})
        # Shared references are anchored only when explicitly approved.
        if not locks:
            locks['primary']={'scene_id':scene_id,'image_file':path,'image_version':scene['image_version'],'bible_lock_id':(p.get('bible') or {}).get('lock_id')}
        store.save(p)
        return p


def update_input(project_id, new_config):
    """Validate without side effects; preserve scenes for metadata/export-only changes."""
    with _guard:
        if project_id in _active:raise WorkflowError('Không sửa đầu vào khi đang chạy')
        old=store.get(project_id)
        if not old:raise WorkflowError('Không tìm thấy dự án')
        validate_project_input(new_config)
        changed={k for k in (set(new_config)|set(old['config'])) if new_config.get(k)!=old['config'].get(k)}
        if not changed:return old
        old['history']=old.get('history',[])+[{'version':old['version'],'config':copy.deepcopy(old['config']),'at':store.now(),'changed':sorted(changed)}]
        old['config']=copy.deepcopy(new_config);old['title']=new_config['title'];old['version']+=1
        if changed<= {'title'}:
            # Title is metadata, not a media dependency.
            store.save(old);return old
        if changed<= {'title','subtitles'}:
            # Subtitles affect export, not image/video generation or approvals.
            old['video']=None;old['steps']['13']='READY' if all(s.get('accepted') for s in old['scenes']) and old['scenes'] else 'LOCKED'
            old['steps']['14']='LOCKED';old['status']='AWAITING_ACCEPTANCE';store.save(old);return old
        # Changes to teaching content / target / style affect the full production chain.
        old['analysis']=old['blueprint']=old['script']=old['bible']=old['video']=None
        old['reference_lock']={};old['scenes']=[]
        old['steps']={str(i):('COMPLETED' if i==1 else 'LOCKED') for i in range(1,15)}
        old['step']=1;old['status']='READY';store.save(old)
        return old


def summarize(p):
    p=copy.deepcopy(p)
    root=store.file_dir(p['id'])
    for record in (p.get('reference_lock') or {}).values():
        if isinstance(record,dict):record.pop('image_file',None)
    for s in p['scenes']:
        s['image_url']=f'/api/projects/{p["id"]}/scenes/{s["id"]}/image?v={s["image_version"]}' if s.get('image_file') and Path(s['image_file']).is_file() else None
        s['video_url']=f'/api/projects/{p["id"]}/scenes/{s["id"]}/video?v={s["video_version"]}' if s.get('video_file') and Path(s['video_file']).is_file() else None
        s.pop('image_file',None);s.pop('video_file',None)
    if p.get('video'):
        if Path(p['video']['file']).is_file():p['video']['url']=f'/api/projects/{p["id"]}/video'
        p['video'].pop('file',None)
    stage_names=['Phân tích bài học','Tạo kịch bản','Chia cảnh','Tạo câu lệnh','Tạo hình ảnh','Tạo video','Ghép video','Hoàn thành']
    p['stages8']=[]
    for name, group in zip(stage_names,STAGE_INDICES):
        statuses=[p['steps'][str(i)] for i in group]
        if 'FAILED' in statuses: stage_status='FAILED'
        elif all(x=='COMPLETED' for x in statuses):stage_status='COMPLETED'
        elif 'RUNNING' in statuses:stage_status='RUNNING'
        else:stage_status='LOCKED'
        p['stages8'].append({'name':name,'status':stage_status})

    return p
