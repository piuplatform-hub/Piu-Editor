"""Encode the verified Remotion browser frame sequence and the v002 sound master."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess

P = Path(__file__).resolve().parents[1]
ROOT = P.parents[1]
WORK = P / 'working/v002'
FRAMES = WORK / 'remotion-frames'
OUT = ROOT / 'output/tvc-driving-premium'
N, FPS = 975, 24
DURATION = N / FPS

def binary(name):
    found = shutil.which(name)
    if found:
        return found
    fallback = Path(r'C:\Users\Hero\tools\ffmpeg\bin') / (name + '.exe')
    if fallback.is_file():
        return str(fallback)
    raise RuntimeError(f'{name} is not available')

def run(args, log):
    with (WORK / log).open('w', encoding='utf8') as stream:
        result = subprocess.run(args, stdout=stream, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f'Command failed: see {WORK / log}')

def verify_sources():
    manifest = json.loads((P / 'assets.json').read_text(encoding='utf8'))
    checked = []
    for asset in manifest['assets']:
        if not asset.get('selected'):
            continue
        source = ROOT / asset['path']
        with source.open('rb') as stream:
            actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        if actual != asset['sha256']:
            raise RuntimeError(f'Original changed: {asset["path"]}')
        checked.append(asset['path'])
    return checked

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--qa-only', action='store_true')
    args = parser.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / 'yen-thanh-tvc-v002.mp4'
    ffmpeg, ffprobe = binary('ffmpeg'), binary('ffprobe')
    if not args.qa_only:
        expected = {f'f{frame:04d}.jpg' for frame in range(N)}
        actual = {p.name for p in FRAMES.glob('f*.jpg') if p.stat().st_size > 1000}
        if expected != actual:
            raise RuntimeError(f'Incomplete frame sequence: {len(actual)}/{N}')
        state = json.loads((WORK / 'export-status.json').read_text(encoding='utf8'))
        if state.get('event') != '/complete' or json.loads(state['data']) != {'preview': False, 'frames': N}:
            raise RuntimeError('Full browser export has not completed successfully')
        run([ffmpeg, '-hide_banner', '-n', '-framerate', str(FPS), '-start_number', '0',
             '-i', str(FRAMES / 'f%04d.jpg'), '-i', str(P / 'public/soundtrack-v002.wav'),
             '-map', '0:v:0', '-map', '1:a:0', '-t', str(DURATION),
             '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p',
             '-threads', '4', '-c:a', 'aac', '-b:a', '320k', '-ar', '48000',
             '-movflags', '+faststart', str(target)], 'encode.log')
        shutil.copy2(P / 'public/soundtrack-v002.wav', OUT / 'yen-thanh-soundtrack-v002.wav')
        shutil.copy2(P / 'previews/v002/f0088.jpg', OUT / 'yen-thanh-tvc-v002-poster.jpg')

    probe = subprocess.run([ffprobe, '-v', 'error', '-count_frames', '-show_format',
                            '-show_streams', '-of', 'json', str(target)],
                           capture_output=True, text=True, check=True)
    info = json.loads(probe.stdout)
    video = [s for s in info['streams'] if s['codec_type'] == 'video']
    audio = [s for s in info['streams'] if s['codec_type'] == 'audio']
    assert len(video) == len(audio) == 1
    v, a = video[0], audio[0]
    assert (v['width'], v['height'], v['avg_frame_rate'], int(v['nb_read_frames'])) == (1920, 1080, '24/1', N)
    assert a['channels'] == 2 and a['sample_rate'] == '48000'
    assert abs(float(info['format']['duration']) - DURATION) < .05
    run([ffmpeg, '-hide_banner', '-v', 'error', '-xerror', '-i', str(target),
         '-map', '0:v:0', '-map', '0:a:0', '-f', 'null', '-'], 'decode-qa.log')
    measure = subprocess.run([ffmpeg, '-hide_banner', '-i', str(target), '-vn', '-af',
                              'loudnorm=I=-14.5:TP=-1.5:LRA=8:print_format=json', '-f', 'null', '-'],
                             capture_output=True, text=True, check=True)
    (WORK / 'loudness-qa.log').write_text(measure.stderr, encoding='utf8')
    loudness, _ = json.JSONDecoder().raw_decode(measure.stderr[measure.stderr.rfind('{'):])
    assert float(loudness['input_tp']) < -.5
    sources = verify_sources()
    report = {'file': str(target.relative_to(ROOT)), 'bytes': target.stat().st_size,
              'duration': info['format']['duration'], 'video': v, 'audio': a,
              'loudness': loudness, 'unchangedOriginals': sources,
              'fullDecode': 'passed', 'auditoryReview': 'not available in this environment',
              'visualPipeline': 'Remotion Player deterministic seek + local DOM rasterization; FFmpeg H.264 encode'}
    (WORK / 'qa-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps({k: report[k] for k in ['file', 'bytes', 'duration', 'loudness', 'fullDecode']}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
