import os, sys, time, queue, threading, tempfile, wave
from pathlib import Path
from datetime import datetime
import tkinter as tk
import numpy as np
import pyaudiowpatch as pyaudio
import keyboard
from faster_whisper import WhisperModel
from scipy.signal import resample_poly

APP = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
OUT = APP / 'Transcripts'; OUT.mkdir(exist_ok=True)
MODEL_DIR = APP / 'model'
RATE = 16000; CHUNK_SECONDS = 8

class Overlay:
    def __init__(self):
        self.root=tk.Tk(); self.root.overrideredirect(True); self.root.attributes('-topmost',True); self.root.attributes('-alpha',.78)
        self.root.configure(bg='#141414'); self.label=tk.Label(self.root,bg='#141414',fg='white',font=('Segoe UI',10),padx=14,pady=9)
        self.label.pack(); self.root.update_idletasks(); self.place(); self.root.after(500,self.tick)
        self.state='PRET'; self.started=None; self.visible_until=0
    def place(self):
        self.root.update_idletasks(); w=self.root.winfo_width(); h=self.root.winfo_height(); sw=self.root.winfo_screenwidth(); sh=self.root.winfo_screenheight()
        self.root.geometry(f'+{sw-w-22}+{sh-h-62}')
    def show(self,state,sticky=True):
        self.state=state; self.visible_until=0 if sticky else time.time()+3; self.root.deiconify(); self.place()
    def tick(self):
        elapsed='00:00:00'
        if self.started: elapsed=time.strftime('%H:%M:%S',time.gmtime(time.time()-self.started))
        icons={'PRET':'○','ENREGISTREMENT':'●','PAUSE':'Ⅱ','TERMINE':'✓','ERREUR':'!'}
        colors={'PRET':'#d0d0d0','ENREGISTREMENT':'#ff5252','PAUSE':'#ffcc4d','TERMINE':'#61d095','ERREUR':'#ff5252'}
        self.label.config(text=f"{icons.get(self.state,'○')}  {self.state}   {elapsed}",fg=colors.get(self.state,'white'))
        self.place()
        if self.visible_until and time.time()>self.visible_until: self.root.withdraw()
        self.root.after(500,self.tick)

class Recorder:
    def __init__(self,ui):
        self.ui=ui; self.running=False; self.paused=False; self.stop_evt=threading.Event(); self.audio_q=queue.Queue(); self.threads=[]
        model_ref=str(MODEL_DIR) if MODEL_DIR.exists() else 'small'
        self.model=WhisperModel(model_ref,device='cpu',compute_type='int8')
        self.transcript=None
    def devices(self):
        p=pyaudio.PyAudio(); info=p.get_host_api_info_by_type(pyaudio.paWASAPI)
        default_out=p.get_device_info_by_index(info['defaultOutputDevice'])
        loop=None
        for d in p.get_loopback_device_info_generator():
            if default_out['name'] in d['name'] or d['name'] in default_out['name']: loop=d; break
        if loop is None: loop=p.get_default_wasapi_loopback()
        mic=p.get_default_input_device_info(); return p,mic,loop
    def capture(self,p,dev,label):
        rate=int(dev['defaultSampleRate']); channels=max(1,min(2,int(dev['maxInputChannels'])))
        stream=p.open(format=pyaudio.paFloat32,channels=channels,rate=rate,input=True,input_device_index=dev['index'],frames_per_buffer=1024)
        buf=[]; target=rate*CHUNK_SECONDS
        try:
            while not self.stop_evt.is_set():
                data=stream.read(1024,exception_on_overflow=False)
                if self.paused: buf=[]; continue
                a=np.frombuffer(data,dtype=np.float32).reshape(-1,channels).mean(axis=1); buf.append(a)
                if sum(len(x) for x in buf)>=target:
                    raw=np.concatenate(buf); buf=[]
                    audio=resample_poly(raw,RATE,rate).astype(np.float32)
                    self.audio_q.put((time.time(),label,audio))
        finally: stream.stop_stream(); stream.close()
    def transcribe(self):
        while not self.stop_evt.is_set() or not self.audio_q.empty():
            try: ts,label,audio=self.audio_q.get(timeout=.5)
            except queue.Empty: continue
            segs,_=self.model.transcribe(audio,language='fr',vad_filter=True,beam_size=1)
            text=' '.join(s.text.strip() for s in segs).strip()
            if text and self.transcript:
                stamp=datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                with self.transcript.open('a',encoding='utf-8') as f: f.write(f'[{stamp}] **{label}** : {text}\n\n')
    def start(self):
        if self.running: return
        self.stop_evt.clear(); self.paused=False; self.running=True
        self.transcript=OUT/f"Transcript_{datetime.now():%Y-%m-%d_%H-%M-%S}.md"
        self.transcript.write_text(f"# Transcript du {datetime.now():%d/%m/%Y %H:%M}\n\n",encoding='utf-8')
        try:
            p,mic,loop=self.devices()
            self.threads=[threading.Thread(target=self.capture,args=(p,mic,'Micro'),daemon=True),threading.Thread(target=self.capture,args=(p,loop,'PC'),daemon=True),threading.Thread(target=self.transcribe,daemon=True)]
            for t in self.threads:t.start()
            self.ui.started=time.time(); self.ui.show('ENREGISTREMENT')
        except Exception as e:
            self.running=False; self.ui.show('ERREUR',False); (APP/'error.log').write_text(str(e),encoding='utf-8')
    def pause(self):
        if not self.running:return
        self.paused=not self.paused; self.ui.show('PAUSE' if self.paused else 'ENREGISTREMENT')
    def stop(self):
        if not self.running:return
        self.stop_evt.set(); self.running=False; self.paused=False; self.ui.show('TERMINE',False); self.ui.started=None
    def toggle(self): self.stop() if self.running else self.start()

ui=Overlay(); rec=Recorder(ui)
keyboard.add_hotkey('ctrl+alt+r',rec.toggle)
keyboard.add_hotkey('ctrl+alt+p',rec.pause)
keyboard.add_hotkey('ctrl+alt+q',lambda:(rec.stop(),ui.root.destroy()))
ui.show('PRET',False)
ui.root.mainloop()
