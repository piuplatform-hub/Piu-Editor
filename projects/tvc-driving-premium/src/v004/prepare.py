"""Prepare v004 with the project-bundled FFmpeg and Python 3.10 stdlib.

Inputs are read only. Derived assets are kept in public/v004 and working/v004.
"""
from pathlib import Path
import argparse
import array
import hashlib
import json
import math
import random
import shutil
import subprocess
import sys
import wave
import urllib.request

PROJECT = Path(__file__).resolve().parents[2]
ROOT = PROJECT.parents[1]
WORK = PROJECT / 'working/v004'
PUBLIC = PROJECT / 'public/v004'
CONFIG = json.loads((Path(__file__).parent / 'timeline.json').read_text(encoding='utf-8'))
RATE = 48000


def binary(name):
    bundled = PROJECT / 'node_modules/@remotion/compositor-win32-x64-msvc' / (name + '.exe')
    found = shutil.which(name)
    if bundled.is_file():
        return str(bundled)
    if found:
        return found
    raise RuntimeError(f'{name} is not available')


def run(args, log):
    WORK.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    (WORK / log).write_text(result.stdout + result.stderr, encoding='utf-8')
    if result.returncode:
        raise RuntimeError(f'{log}: {result.stderr[-1500:]}')
    return result.stdout


def verify_sources():
    assets = json.loads((PROJECT / 'assets.json').read_text(encoding='utf-8-sig'))['assets']
    checked = []
    for asset in assets:
        if not asset.get('selected'):
            continue
        source = ROOT / asset['path']
        digest = hashlib.sha256()
        with source.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
        if digest.hexdigest() != asset.get('sha256'):
            raise RuntimeError(f'Source changed: {asset["path"]}')
        checked.append({'path': asset['path'], 'sha256': digest.hexdigest()})
    return checked


def video():
    (PUBLIC / 'video').mkdir(parents=True, exist_ok=True)
    (PUBLIC / 'fonts').mkdir(exist_ok=True)
    for name in ['Manrope.ttf', 'OFL.txt']:
        shutil.copy2(PROJECT / 'public/fonts' / name, PUBLIC / 'fonts' / name)
    for row in json.loads((Path(__file__).parent/'font-sources.json').read_text(encoding='utf-8')):
        target=PUBLIC/'fonts'/row['name']
        if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest()==row['sha256']:
            continue
        with urllib.request.urlopen(row['source'],timeout=30) as response:
            data=response.read()
        if hashlib.sha256(data).hexdigest()!=row['sha256']:
            raise RuntimeError(f'Font source changed; inspect before using: {row["name"]}')
        target.write_bytes(data)
    for shot in CONFIG['shots']:
        frames = shot['end'] - shot['start']
        source = PROJECT / f'public/video/clip-{shot["clip"]:02d}.mp4'
        target = PUBLIC / f'video/{shot["id"]}.mp4'
        spec = WORK / f'prepare-{shot["id"]}-spec.json'
        expected = {'clip': shot['clip'], 'sourceStart': shot['sourceStart'], 'frames': frames}
        cache_valid = target.is_file() and spec.is_file() and json.loads(spec.read_text()) == expected
        if not cache_valid:
            run([binary('ffmpeg'), '-v', 'error', '-y', '-ss', str(shot['sourceStart']),
                 '-i', str(source), '-frames:v', str(frames), '-an', '-c:v', 'libx264',
                 '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p', '-threads', '3',
                 '-movflags', '+faststart', str(target)], f'prepare-{shot["id"]}.log')
            spec.write_text(json.dumps(expected, indent=2), encoding='utf-8')
        probe = json.loads(run([binary('ffprobe'), '-v', 'error', '-count_frames',
                               '-show_streams', '-of', 'json', str(target)],
                              f'probe-{shot["id"]}.json'))
        assert len(probe['streams']) == 1, 'Prepared picture must contain no source audio'
        stream = probe['streams'][0]
        assert (stream['width'], stream['height'], stream['avg_frame_rate'],
                int(stream['nb_read_frames'])) == (1920, 1080, '24/1', frames)
        print(f'Prepared {shot["id"]}: {frames} frames, video only', flush=True)


def read_pcm(path):
    with wave.open(str(path), 'rb') as source:
        assert source.getsampwidth() == 2 and source.getnchannels() == 2
        data = array.array('h', source.readframes(source.getnframes()))
    if sys.byteorder != 'little':
        data.byteswap()
    return data


def write_pcm(path, samples):
    values = array.array('h', (round(math.tanh(float(x)) * 32767) for x in samples))
    if sys.byteorder != 'little':
        values.byteswap()
    with wave.open(str(path), 'wb') as target:
        target.setnchannels(2)
        target.setsampwidth(2)
        target.setframerate(RATE)
        target.writeframes(values.tobytes())


def effect(kind, seed):
    rng = random.Random(seed)
    duration = {'impact': 1.5, 'air': .62, 'rise': 1.45, 'type': .24, 'resolve': 2.2}[kind]
    result = array.array('f')
    low = 0.0
    phase = 0.0
    previous = 0.0
    for i in range(round(duration * RATE)):
        t = i / RATE
        x = t / duration
        noise = rng.uniform(-1, 1)
        low += (.025 + .10 * x) * (noise - low)
        high = noise - previous
        previous = noise
        if kind == 'impact':
            phase += 2 * math.pi * (42 + 88 * math.exp(-22 * t)) / RATE
            v = (.63 * math.sin(phase) * math.exp(-4.2 * t)
                 + .15 * low * math.exp(-6 * t) + .045 * high * math.exp(-45 * t))
            v *= min(1, t * 700)
        elif kind == 'air':
            env = math.sin(math.pi * x) ** 3
            v = (low * 1.6 + .04 * high) * env * .50
        elif kind == 'rise':
            phase += 2 * math.pi * (72 + 480 * x * x) / RATE
            v = (low * .60 + .10 * math.sin(phase)) * x ** 2 * min(1, (1-x)*25)
        elif kind == 'type':
            phase += 2 * math.pi * (320 - 160 * x) / RATE
            v = (.20 * math.sin(phase) + .08 * low) * math.exp(-22 * t) * min(1, t*1800)
        else:
            env = min(1, t * 6) * math.exp(-1.8 * t)
            v = (.14 * math.sin(2 * math.pi * 110 * t)
                 + .065 * math.sin(2 * math.pi * 165 * t)
                 + .04 * math.sin(2 * math.pi * 220 * t) + .04 * low) * env
        pan = -.6 + 1.2 * x if kind == 'air' else .08 * math.sin(x * math.pi)
        result.extend([v * math.sqrt((1-pan)/2), v * math.sqrt((1+pan)/2)])
    return result


def audio():
    PUBLIC.mkdir(parents=True, exist_ok=True)
    duration = CONFIG['totalFrames'] / CONFIG['fps']
    manifest = json.loads((PROJECT / 'assets.json').read_text(encoding='utf-8-sig'))
    music = [a for a in manifest['assets'] if a.get('selected') and a.get('role') == 'background music supplied by user']
    assert len(music) == 1
    run([binary('ffmpeg'), '-v', 'error', '-y', '-ss', str(CONFIG['musicStart']),
         '-i', str(ROOT / music[0]['path']), '-t', str(duration), '-ar', str(RATE),
         '-ac', '2', '-c:a', 'pcm_s16le', str(WORK / 'music-decoded.wav')], 'music-decode.log')
    pcm = read_pcm(WORK / 'music-decoded.wav')
    count = round(duration * RATE)
    mix = array.array('f', [0]) * (count * 2)
    events = []

    def cue(kind, frame, gain):
        events.append({'kind': kind, 'frame': frame, 'time': frame/CONFIG['fps'], 'gain': gain})

    for f in [0, 93, 372, 581, 674, 790, 860]:
        cue('impact', f, .85 if f in [93, 674, 860] else .55)
    for f in [93, 186, 302, 372, 488, 581, 674, 720, 766, 790, 836, 860]:
        cue('air', f-6, .72 if f in CONFIG['graphicTransitions'] else .44)
    for f in [93, 372, 674, 860]:
        cue('rise', f-34, .45)
    for f in [9, 20, 112, 128, 202, 214, 316, 385, 399, 504, 518, 598, 612, 680, 796, 874, 887]:
        cue('type', f, .55)
    cue('resolve', 865, .75)

    for i in range(min(count, len(pcm)//2)):
        t = i / RATE
        fade = min(1.0, t/.16, max(0.0, (duration-t)/1.3))
        # Space under the brand signature, with full energy at the montage.
        gain = .76 if t < 36.8 else .76 - .22 * min(1, (t-36.8)/1.0)
        mix[2*i] = pcm[2*i]/32768 * gain * fade
        mix[2*i+1] = pcm[2*i+1]/32768 * gain * fade
    effects = {}
    for number, event in enumerate(events):
        kind = event['kind']
        if kind not in effects:
            effects[kind] = effect(kind, 20261103 + len(effects) * 19)
        samples = effects[kind]
        start = round(event['time'] * RATE) * 2
        for j, value in enumerate(samples):
            target = start + j
            if 0 <= target < len(mix):
                mix[target] += value * event['gain']
    # Apply the finish to the whole mix, including reverb/effect tails.
    for i in range(max(0, count-round(.75*RATE)), count):
        gain = (count-i)/(.75*RATE)
        mix[2*i] *= gain
        mix[2*i+1] *= gain
    write_pcm(WORK / 'premaster.wav', mix)
    measure = subprocess.run([binary('ffmpeg'), '-hide_banner', '-i', str(WORK/'premaster.wav'),
                              '-af', 'loudnorm=I=-14.5:TP=-1.5:LRA=8:print_format=json',
                              '-f', 'null', '-'], capture_output=True, text=True, check=True)
    (WORK/'loudness-analysis.log').write_text(measure.stderr, encoding='utf-8')
    stats, _ = json.JSONDecoder().raw_decode(measure.stderr[measure.stderr.rfind('{'):])
    norm = (f"loudnorm=I=-14.5:TP=-1.5:LRA=8:measured_I={stats['input_i']}:"
            f"measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}:"
            f"measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}:linear=true")
    run([binary('ffmpeg'), '-v', 'error', '-y', '-i', str(WORK/'premaster.wav'),
         '-af', norm, '-ar', str(RATE), '-ac', '2', '-c:a', 'pcm_s24le',
         str(PUBLIC/'soundtrack.wav')], 'master.log')
    run([binary('ffmpeg'), '-v', 'error', '-y', '-i', str(PUBLIC/'soundtrack.wav'),
         '-c:a', 'aac', '-b:a', '320k', '-f', 'mp4', str(PUBLIC/'soundtrack.m4a')], 'audio-preview.log')
    (WORK/'sound-design.json').write_text(json.dumps({'music': music[0]['path'],
        'musicStart': CONFIG['musicStart'], 'seed': 20261103, 'events': events,
        'mastering': stats}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Mastered {duration:.3f}s with {len(events)} sound cues', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['all', 'video', 'audio', 'verify'], nargs='?', default='all')
    args = parser.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    originals = verify_sources()
    (WORK/'originals-verified.json').write_text(json.dumps(originals, ensure_ascii=False, indent=2), encoding='utf-8')
    if args.mode in ['all', 'video']:
        video()
    if args.mode in ['all', 'audio']:
        audio()
    print(f'Originals unchanged: {len(originals)} SHA-256 matches', flush=True)
