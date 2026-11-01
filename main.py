import os, wave, unicodedata, zipfile
import numpy as np
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.button import Button
from kivy.utils import platform

KV = """
<RootUI>:
    orientation: "vertical"
    padding: "14dp"
    spacing: "8dp"
    canvas.before:
        Color:
            rgba: (.09, .08, .13, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        text: "[b]Utaun Android[/b]"
        markup: True
        font_size: "25sp"
        color: (1, .53, .79, 1)
        size_hint_y: None
        height: "42dp"
    Label:
        text: "Generador de voicebanks CV artificial"
        size_hint_y: None
        height: "26dp"
    TextInput:
        id: char_name
        hint_text: "Nombre del personaje"
        text: "NewVoice"
        multiline: False
        size_hint_y: None
        height: "44dp"
    TextInput:
        id: author
        hint_text: "Autor"
        text: "User"
        multiline: False
        size_hint_y: None
        height: "44dp"
    TextInput:
        id: readme
        hint_text: "Descripción"
        text: "Created by Utaun Android"
        size_hint_y: None
        height: "65dp"
    TextInput:
        id: height
        hint_text: "Altura en Hz"
        text: "475"
        input_filter: "float"
        multiline: False
        size_hint_y: None
        height: "44dp"
    Spinner:
        id: encoding
        text: "UTF-8 (OpenUtau)"
        values: ["UTF-8 (OpenUtau)", "Shift-JIS (UTAU clásico)"]
        size_hint_y: None
        height: "44dp"
    Button:
        text: "Seleccionar oto.ini"
        on_release: app.pick_oto()
        size_hint_y: None
        height: "46dp"
    Label:
        id: oto_label
        text: "Ningún oto.ini seleccionado"
        size_hint_y: None
        height: "24dp"
    Button:
        text: "Seleccionar carpeta de consonantes WAV"
        on_release: app.pick_consonants()
        size_hint_y: None
        height: "46dp"
    Label:
        id: consonant_label
        text: "Ninguna carpeta seleccionada"
        size_hint_y: None
        height: "36dp"
        text_size: self.width, None
    Button:
        text: "GENERAR Y GUARDAR ZIP"
        bold: True
        background_normal: ""
        background_color: (1, .48, .75, 1)
        color: (.12, .08, .14, 1)
        on_release: app.generate()
        size_hint_y: None
        height: "52dp"
    Label:
        id: status
        text: "El ZIP se guardará en Download."
        color: (1, .78, .88, 1)
        text_size: self.width, None
"""

def vowel_data(v_char, height, duration=1.0, sr=44100):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    recipes = {'あ':[800,1200], 'い':[300,2200], 'う':[300,900],
               'え':[500,1700], 'お':[400,800], 'ん':[300,800]}
    targets = [x + max(0, height-200)*.25 for x in recipes.get(v_char,[800,1200])]
    signal = np.zeros_like(t)
    for n in range(1, min(int(sr/2/height), 30)):
        freq = height*n
        amp = sum(np.exp(-(freq-c)**2/50000) for c in targets)
        signal += amp/(n**1.2)*np.sin(2*np.pi*freq*t)
    peak = np.max(np.abs(signal))
    if peak: signal = signal/peak*.7
    return (signal*32767).astype(np.int16)

def write_wav(path, data):
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
        f.writeframes(data.tobytes())

class RootUI(BoxLayout): pass

class UtaunApp(App):
    oto_path = None
    consonant_dir = None

    def build(self):
        self.title = "Utaun Android"
        Builder.load_string(KV)
        if platform == "android":
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            except Exception: pass
        return RootUI()

    def picker(self, title, callback, directory=False):
        start = "/storage/emulated/0/Download" if platform == "android" else os.path.expanduser("~")
        chooser = FileChooserListView(path=start, dirselect=directory,
                                      filters=[] if directory else ["*.ini"])
        layout = BoxLayout(orientation="vertical", spacing=5, padding=5)
        layout.add_widget(chooser)
        row = BoxLayout(size_hint_y=None, height="46dp", spacing=5)
        pop = Popup(title=title, content=layout, size_hint=(.95,.9))
        row.add_widget(Button(text="Cancelar", on_release=pop.dismiss))
        def accept(*_):
            chosen = chooser.selection[0] if chooser.selection else chooser.path
            callback(chosen); pop.dismiss()
        row.add_widget(Button(text="Usar selección", on_release=accept))
        layout.add_widget(row); pop.open()

    def pick_oto(self):
        def cb(p):
            if os.path.isfile(p):
                self.oto_path=p; self.root.ids.oto_label.text=os.path.basename(p)
        self.picker("Elegir oto.ini", cb)

    def pick_consonants(self):
        def cb(p):
            if os.path.isdir(p):
                self.consonant_dir=p; self.root.ids.consonant_label.text=p
        self.picker("Elegir carpeta WAV", cb, True)

    def generate(self):
        try:
            if not self.oto_path or not os.path.isfile(self.oto_path):
                raise ValueError("Seleccioná oto.ini.")
            if not self.consonant_dir or not os.path.isdir(self.consonant_dir):
                raise ValueError("Seleccioná la carpeta de consonantes.")
            name=unicodedata.normalize("NFC",self.root.ids.char_name.text.strip() or "NewVoice")
            name="".join(c for c in name if c not in '\\\\/:*?"<>|') or "NewVoice"
            author=self.root.ids.author.text.strip() or "User"
            readme=self.root.ids.readme.text or "Created by Utaun Android"
            height=float(self.root.ids.height.text or "475")
            if height <= 0: raise ValueError("La altura debe ser mayor que cero.")
            encoding="shift_jis" if self.root.ids.encoding.text.startswith("Shift") else "utf-8"
            vowels={v:vowel_data(v,height) for v in "あいうえおん"}
            roma={'あ':'a','い':'i','う':'u','え':'e','お':'o','ん':'nn'}
            out="/storage/emulated/0/Download" if platform=="android" else os.path.join(os.path.expanduser("~"),"Downloads")
            if not os.path.isdir(out): out=self.user_data_dir
            os.makedirs(out,exist_ok=True)
            dest=os.path.join(out,name+".zip")
            with zipfile.ZipFile(dest,"w",zipfile.ZIP_DEFLATED) as z:
                tmp=os.path.join(self.user_data_dir,"temp.wav")
                def addwav(filename,data):
                    write_wav(tmp,data); z.write(tmp,name+"/"+filename); os.remove(tmp)
                for v,data in vowels.items():
                    addwav(v+".wav",data); addwav(roma[v]+".wav",data)
                mapping={'m':('ん',4410,'まみむめも'),'n':('ん',2205,'なにぬねの'),
                         'y':('い',4410,'やゆよ'),'w':('う',4410,'わを')}
                for row,(base,length,hiragana) in mapping.items():
                    sub=vowels[base][:length]
                    targets=[('あ','a',0),('い','i',1),('う','u',2),('え','e',3),('お','o',4)] if row in "mn" else ([('あ','a',0),('う','u',1),('お','o',2)] if row=="y" else [('あ','a',0),('お','o',1)])
                    for vh,vr,idx in targets:
                        combined=np.concatenate([sub,vowels[vh]])
                        addwav(row+vr+".wav",combined); addwav(hiragana[idx]+".wav",combined)
                rows=[
                    ('ka','か','ka'),('ki','き','ki'),('ku','く','ku'),('ke','け','ke'),('ko','こ','ko'),
                    ('sa','さ','sa'),('si','し','shi'),('su','す','su'),('se','せ','se'),('so','そ','so'),
                    ('ta','た','ta'),('ti','ち','chi'),('tu','つ','tsu'),('te','て','te'),('to','と','to'),
                    ('na','な','na'),('ni','に','ni'),('nu','ぬ','nu'),('ne','ね','ne'),('no','の','no'),
                    ('ha','は','ha'),('hi','ひ','hi'),('hu','ふ','hu'),('he','へ','he'),('ho','ほ','ho'),
                    ('ma','ま','ma'),('mi','み','mi'),('mu','む','mu'),('me','め','me'),('mo','も','mo'),
                    ('ya','や','ya'),('yu','ゆ','yu'),('yo','よ','yo'),('ra','ら','ra'),('ri','り','ri'),
                    ('ru','る','ru'),('re','れ','re'),('ro','ろ','ro'),('wa','わ','wa'),('wo','を','wo'),
                    ('ga','が','ga'),('gi','ぎ','gi'),('gu','ぐ','gu'),('ge','げ','ge'),('go','ご','go'),
                    ('za','ざ','za'),('zi','じ','ji'),('zu','ず','zu'),('ze','ぜ','ze'),('zo','ぞ','zo'),
                    ('da','だ','da'),('di','ぢ','di'),('du','づ','du'),('de','で','de'),('do','ど','do'),
                    ('ba','ば','ba'),('bi','び','bi'),('bu','ぶ','bu'),('be','べ','be'),('bo','ぼ','bo'),
                    ('pa','ぱ','pa'),('pi','ぴ','pi'),('pu','ぷ','pu'),('pe','ぺ','pe'),('po','ぽ','po')]
                wavs=[f for f in os.listdir(self.consonant_dir) if f.lower().endswith(".wav")]
                made=0
                for _,hira,alias in rows:
                    match=next((f for f in wavs if alias in unicodedata.normalize("NFC",f) or hira in unicodedata.normalize("NFC",f)),None)
                    if not match: continue
                    with wave.open(os.path.join(self.consonant_dir,match),"rb") as w:
                        cdata=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16)
                    vowel={'a':'あ','i':'い','u':'う','e':'え','o':'お'}.get(alias[-1],'あ')
                    combined=np.concatenate([cdata,vowels[vowel]])
                    addwav(alias+".wav",combined)
                    if hira!=alias: addwav(hira+".wav",combined)
                    made+=1
                with open(self.oto_path,"rb") as f: z.writestr(name+"/oto.ini",f.read())
                z.writestr(name+"/character.txt",f"name={name}\\nauthor={author}".encode(encoding,errors="replace"))
                z.writestr(name+"/readme.txt",readme.encode(encoding,errors="replace"))
            self.root.ids.status.text=f"¡Listo!\\n{dest}\\nSílabas CV: {made}"
        except Exception as e:
            self.root.ids.status.text="Error: "+str(e)

if __name__=="__main__":
    UtaunApp().run()
