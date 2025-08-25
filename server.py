from flask import Flask, request, Response, jsonify
import os, time

app = Flask(__name__)

# ---------- Frontend HTML ----------
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cytra SpeedTest</title>
<style>
  body {margin:0; background:#0b1220; color:#eef2ff; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; flex-direction:column;}
  h1 {font-size:64px; margin:0; font-weight:900; background: linear-gradient(90deg,#4f7cff,#7f9dff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
  .sub {margin-top:12px; color:#96a0c8; font-size:16px; text-align:center;}
  .brand {position:absolute; top:12px; right:20px; color:#96a0c8; opacity:0.8; font-weight:bold;}
  .bar {width:300px; height:10px; background:#101a31; border-radius:999px; margin-top:24px; overflow:hidden;}
  .bar > div {height:100%; width:0%; background: linear-gradient(90deg,#4f7cff,#7f9dff); transition:width .2s;}
</style>
</head>
<body>
<div class="brand">by Cytra 🚀</div>
<h1 id="speed">… Mbps</h1>
<div class="sub" id="info">Measuring download speed...</div>
<div class="bar"><div id="bar"></div></div>

<script>
const $ = (id)=>document.getElementById(id);
let abort = false;

async function startTest(){
  const base="http://127.0.0.1:5000";
  try {
    // Ping
    const t0=performance.now();
    await fetch(base+"/ping");
    const ping=Math.round(performance.now()-t0);
    $("info").textContent="Ping: "+ping+" ms | Measuring download...";

    // Download
    const size=20*1024*1024;
    const chunk=64*1024;
    const url=base+"/download?size="+size+"&chunk="+chunk+"&_="+Math.random();
    const resp=await fetch(url,{cache:"no-store"});
    const reader=resp.body.getReader();
    let received=0;
    const start=performance.now();
    while(true){
      const {done,value}=await reader.read();
      if(done) break;
      received+=value.length;
      const secs=(performance.now()-start)/1000;
      const mbps=(received*8)/(secs*1024*1024);
      $("speed").textContent=mbps.toFixed(1)+" Mbps";
      $("bar").style.width=Math.min(100,received/size*100)+"%";
      if(abort) break;
    }
    const totalSecs=(performance.now()-start)/1000;
    $("info").textContent="Ping: "+ping+" ms | Completed in "+totalSecs.toFixed(2)+"s";
  }catch(e){
    $("info").textContent="Error: "+e;
  }
}

window.onload=startTest;
</script>
</body>
</html>
"""

# ---------- Routes ----------
@app.route("/")
def index():
    return HTML

@app.route("/ping")
def ping():
    return "pong", 200

@app.route("/download")
def download():
    size = int(request.args.get("size", 10*1024*1024))
    chunk = int(request.args.get("chunk", 64*1024))
    def generate():
        sent=0
        buf=os.urandom(chunk)
        while sent<size:
            to_send=min(chunk,size-sent)
            yield buf[:to_send]
            sent+=to_send
    return Response(generate(), mimetype="application/octet-stream")

@app.route("/upload", methods=["POST"])
def upload():
    data=request.get_data()
    size=len(data)
    return jsonify({"status":"ok","size":size})

# ---------- Run ----------
if __name__=="__main__":
    app.run(host="0.0.0.0", port=3000)
