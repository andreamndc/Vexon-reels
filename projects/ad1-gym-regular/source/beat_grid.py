import wave,numpy as np,sys
w=wave.open(sys.argv[1]);sr=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),np.int16)/32768.
hop=256;n=1024;win=np.hanning(n)
fr=np.array([np.abs(np.fft.rfft(x[i:i+n]*win)) for i in range(0,len(x)-n,hop)])
L=np.log1p(100*fr); flux=np.maximum(0,np.diff(L,axis=0)).sum(1); flux=np.r_[0,flux]
flux=(flux-np.convolve(flux,np.ones(16)/16,'same')).clip(0)
fps=sr/hop
# low-band flux (kick)
lo=np.maximum(0,np.diff(L[:,:int(150/(sr/n))],axis=0)).sum(1);lo=np.r_[0,lo]
ac=np.correlate(flux,flux,'full')[len(flux)-1:]
best=[]
for bpm in np.arange(70,181,0.25):
    lag=60/bpm*fps; i=int(lag); f=lag-i
    v=ac[i]*(1-f)+ac[i+1]*f; best.append((v,bpm))
best.sort(reverse=True); print('tempo candidates',[(round(b,2)) for v,b in best[:8]])
bpm=float(sys.argv[2]) if len(sys.argv)>2 else best[0][1]
per=60/bpm*fps; T=np.arange(len(flux))/fps
sc=[]
for ph in np.linspace(0,per,200,endpoint=False):
    idx=(ph+np.arange(0,len(flux)-ph,per)).astype(int); sc.append((flux[idx].sum(),ph/fps))
sc.sort(reverse=True); off=sc[0][1]; print('bpm',bpm,'first beat at',round(off,3),'s')
# strongest onsets
pk=[i for i in range(2,len(flux)-2) if flux[i]==flux[i-2:i+3].max() and flux[i]>np.percentile(flux,97)]
print('strong onsets',[round(T[i],2) for i in pk])
lpk=[i for i in range(2,len(lo)-2) if lo[i]==lo[i-2:i+3].max() and lo[i]>np.percentile(lo,95)]
print('low hits',[round(T[i],2) for i in lpk])
# energy per 0.25s
e=[20*np.log10(np.sqrt((x[int(s*sr):int((s+.25)*sr)]**2).mean())+1e-9) for s in np.arange(0,len(x)/sr,0.25)]
print('rms',' '.join(f'{v:.0f}' for v in e))
