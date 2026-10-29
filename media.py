"""FFmpeg operations: validate inputs, normalize without chopping dialogue, concatenate, verify."""
import json
import subprocess
from pathlib import Path
import settings as cfg

class MediaError(RuntimeError): pass

def run(argv, timeout=240):
    try:
        p=subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError,subprocess.TimeoutExpired) as e:raise MediaError(str(e)) from e
    if p.returncode:
        raise MediaError((p.stderr or p.stdout or 'FFmpeg error')[-1400:])
    return p.stdout

def probe(path):
    path=Path(path)
    if not path.is_file() or path.stat().st_size<1024:raise MediaError('File media không tồn tại hoặc rỗng')
    raw=run([cfg.FFPROBE,'-v','error','-show_format','-show_streams','-of','json',str(path)])
    info=json.loads(raw)
    streams=info.get('streams') or []
    v=next((s for s in streams if s.get('codec_type')=='video'),None)
    if v is None:raise MediaError('Video không có luồng hình ảnh')
    a=next((s for s in streams if s.get('codec_type')=='audio'),None)
    dur=float(info.get('format',{}).get('duration') or v.get('duration') or 0)
    if dur<=0:raise MediaError('Không xác định được thời lượng video')
    return {'duration':dur,'width':v.get('width'), 'height':v.get('height'), 'audio':bool(a), 'audio_duration':float(a.get('duration') or dur) if a else 0}

def normalize(input_path, output_path):
    info=probe(input_path)
    # Keep *all* recorded speech. Reject out-of-range clips instead of cutting them.
    if not 7.2<=max(info['duration'],info['audio_duration'])<=8.8:
        raise MediaError(f'Cảnh dài {info["duration"]:.2f}s, ngoài khoảng cho phép; cần tạo lại để tránh cắt lời thoại.')
    original=max(info['duration'],info['audio_duration'])
    speed=original/8.0
    vf=f'setpts=(PTS-STARTPTS)/{speed:.8f},scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=24,format=yuv420p'
    output_path=Path(output_path);output_path.parent.mkdir(parents=True,exist_ok=True)
    args=[cfg.FFMPEG,'-y','-hide_banner','-loglevel','error','-i',str(input_path)]
    if info['audio']:
        args.extend(['-filter_complex',f'[0:v:0]{vf}[v];[0:a:0]aresample=48000,atempo={speed:.8f},apad,atrim=0:8,asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-1.5:LRA=11[a]','-map','[v]','-map','[a]'])
    else:
        args.extend(['-f','lavfi','-i','anullsrc=channel_layout=stereo:sample_rate=48000','-filter_complex',f'[0:v:0]{vf}[v]','-map','[v]','-map','1:a:0'])
    args.extend(['-t','8','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-ac','2','-movflags','+faststart',str(output_path)])
    run(args,timeout=400)
    final=probe(output_path)
    if abs(final['duration']-8)>.22 or final['width']!=1280 or final['height']!=720:
        raise MediaError('Clip chuẩn hóa sai độ dài/độ phân giải')
    return str(output_path)

def merge(inputs,final_path):
    """Normalized clips are consistent H.264/AAC/24FPS/1280x720."""
    if not inputs:raise MediaError('Không có cảnh để ghép')
    final_path=Path(final_path)
    final_path.parent.mkdir(parents=True,exist_ok=True)
    norm_dir=final_path.parent/'normalized'
    norm_dir.mkdir(parents=True,exist_ok=True)
    normalized=[]
    for i,input_path in enumerate(inputs):
        np=norm_dir/f'clip_{i+1:03d}.mp4'
        normalized.append(normalize(input_path,np))
    concat_file=final_path.parent/'concat.txt'
    concat_file.write_text(''.join("file '"+str(Path(f).resolve()).replace("'","'\\''")+"'\n" for f in normalized),encoding='utf-8')
    run([cfg.FFMPEG,'-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(concat_file),'-c','copy','-movflags','+faststart',str(final_path)],timeout=500)
    info=probe(final_path)
    if abs(info['duration']-(len(inputs)*8))>.7:
        raise MediaError('Video ghép sai tổng thời lượng')
    return info

def to_srt_time(seconds):
    whole=int(seconds);ms=int(round((seconds-whole)*1000))
    if ms==1000:whole+=1;ms=0
    return f'{whole//3600:02d}:{(whole%3600)//60:02d}:{whole%60:02d},{ms:03d}'

def write_scene_subtitles(scenes,path):
    """Only called if user explicitly checks the subtitle option."""
    path=Path(path)
    records=[]
    for n,scene in enumerate(scenes,1):
        line=str(scene.get('dialogue','')).strip()
        if not line:continue
        start=scene['start_time']+.15
        end=scene['end_time']-.15
        records.append(f'{n}\n{to_srt_time(start)} --> {to_srt_time(end)}\n{line}\n')
    if not records:raise MediaError('Không có lời thoại để sinh phụ đề')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(records),encoding='utf-8')
    return path

def burn_subtitles(input_path,output_path,srt_path):
    # Filepaths generated internally; escaped for ffmpeg filter parser.
    subtitle_file=str(Path(srt_path).resolve()).replace('\\','/').replace(':','\\:').replace("'","\\'")
    style='FontName=DejaVu Sans,FontSize=22,Outline=2,Shadow=0,Alignment=2,MarginV=32'
    vf=f"subtitles=filename='{subtitle_file}':force_style='{style}'"
    run([cfg.FFMPEG,'-y','-hide_banner','-loglevel','error','-i',str(input_path),'-vf',vf,'-c:v','libx264','-preset','medium','-crf','20','-c:a','copy','-movflags','+faststart',str(output_path)],timeout=500)
    info=probe(output_path)
    return info
