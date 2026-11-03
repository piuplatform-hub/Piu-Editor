"""Verify the actual v003 MP4, compare its audio with the authored master, and export review frames."""
from pathlib import Path
import array
import hashlib
import json
import math
import shutil
import subprocess
import sys
import wave

from prepare import PROJECT, ROOT, WORK, PUBLIC, CONFIG, binary, verify_sources

OUTPUT = ROOT/'output/tvc-driving-premium'
TARGET = OUTPUT/'yen-thanh-tvc-v003.mp4'
PREVIEW = PROJECT/'previews/v003'


def command(args, log):
    result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    (WORK/log).write_text(result.stdout+result.stderr,encoding='utf-8')
    if result.returncode:
        raise RuntimeError(f'QA command failed: {log}: {result.stderr[-1200:]}')
    return result


def digest(path):
    value=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024), b''):
            value.update(chunk)
    return value.hexdigest()


def decode_audio(path, filename):
    raw=WORK/filename
    command([binary('ffmpeg'),'-v','error','-y','-i',str(path),'-vn','-ac','1','-ar','8000',
             '-c:a','pcm_s16le','-f','wav',str(raw)],filename+'.log')
    with wave.open(str(raw),'rb') as source:
        samples=array.array('h',source.readframes(source.getnframes()))
    if sys.byteorder!='little':samples.byteswap()
    return samples


def main():
    info=json.loads(command([binary('ffprobe'),'-v','error','-count_frames','-show_format',
                             '-show_streams','-of','json',str(TARGET)],'ffprobe-final.json').stdout)
    videos=[s for s in info['streams'] if s['codec_type']=='video']
    audios=[s for s in info['streams'] if s['codec_type']=='audio']
    assert len(videos)==len(audios)==1
    v,a=videos[0],audios[0]
    assert (v['codec_name'],v['width'],v['height'],v['avg_frame_rate'],int(v['nb_read_frames']))==('h264',1920,1080,'24/1',975)
    assert v['pix_fmt']=='yuv420p'
    assert (v.get('color_range'),v.get('color_space'),v.get('color_transfer'),v.get('color_primaries'))==('tv','bt709','bt709','bt709')
    assert (a['codec_name'],a['channels'],a['sample_rate'])==('aac',2,'48000')
    assert abs(float(info['format']['duration'])-975/24)<.05
    command([binary('ffmpeg'),'-v','error','-xerror','-i',str(TARGET),'-map','0:v:0','-map','0:a:0',
             '-c:v','rawvideo','-c:a','pcm_s16le','-f','null','-'],'decode-final.log')
    measure=command([binary('ffmpeg'),'-hide_banner','-i',str(TARGET),'-vn','-af',
                     'loudnorm=I=-14.5:TP=-1.5:LRA=8:print_format=json','-f','null','-'],'loudness-final.log')
    loudness,_=json.JSONDecoder().raw_decode(measure.stderr[measure.stderr.rfind('{'):])
    assert float(loudness['input_tp'])<=-1.0, 'True peak exceeds delivery target'
    assert -16<=float(loudness['input_i'])<=-13, 'Unexpected integrated loudness'
    master=decode_audio(PUBLIC/'soundtrack.wav','master-8k.pcm')
    final=decode_audio(TARGET,'final-8k.pcm')
    # AAC container trimming can move a boundary by a few samples. Check small lags.
    correlations=[]
    for lag in [-16,-8,0,8,16]:
        start=max(0,-lag);end=min(len(master),len(final)-lag)
        xx=yy=xy=0.0
        for i in range(start,end,4):
            x=master[i]/32768;y=final[i+lag]/32768
            xx+=x*x;yy+=y*y;xy+=x*y
        correlations.append({'lagSamplesAt8k':lag,'correlation':xy/math.sqrt(xx*yy)})
    match=max(correlations,key=lambda x:x['correlation'])
    assert match['correlation']>.98, 'Final audio does not match the authored soundtrack'
    originals=verify_sources()
    for shot in CONFIG['shots']:
        probe=json.loads(command([binary('ffprobe'),'-v','error','-show_streams','-of','json',
                                  str(PUBLIC/f'video/{shot["id"]}.mp4')],f'qa-video-only-{shot["id"]}.json').stdout)
        assert all(s['codec_type']=='video' for s in probe['streams'])
    for frame in [0,52,132,220,272,334,420,530,620,695,755,812,855,916,947,974]:
        command([binary('ffmpeg'),'-v','error','-y','-ss',str(frame/24),'-i',str(TARGET),
                 '-frames:v','1',str(PREVIEW/f'final-{frame:04d}.png')],f'extract-{frame:04d}.log')
    baseline=WORK/'prior-output-hashes.json'
    preserved=[]
    if baseline.is_file():
        for row in json.loads(baseline.read_text(encoding='utf-8')):
            path=ROOT/row['path']
            assert digest(path)==row['sha256'], f'Previous deliverable changed: {path}'
            preserved.append(row['path'])
    report={'file':TARGET.relative_to(ROOT).as_posix(),'sha256':digest(TARGET),'bytes':TARGET.stat().st_size,
            'duration':info['format']['duration'],'video':v,'audio':a,'loudness':loudness,
            'fullDecode':'passed','masterAudioCorrelation':match,'unchangedOriginals':originals,
            'preservedPriorDeliverables':preserved,'preparedClipsContainSourceAudio':False,
            'auditoryReview':'Not performed by the assistant; user listening review remains',
            'visualPipeline':'Native Remotion + GSAP 3.15.0 / DrawSVG / CustomEase; bundled Chromium',
            'framesExtracted':[0,52,132,220,272,334,420,530,620,695,755,812,855,916,947,974]}
    (WORK/'qa-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    shutil.copy2(PUBLIC/'soundtrack.wav',OUTPUT/'yen-thanh-soundtrack-v003.wav')
    print(json.dumps({k:report[k] for k in ['file','bytes','duration','loudness','fullDecode','masterAudioCorrelation']},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
