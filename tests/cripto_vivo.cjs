const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = require('node:path').join(__dirname, '../assets/cripto_vivo.js');
const {parseTicker} = require(source);
const now = Date.now();
const ticker = {e:'24hrTicker',s:'BTCUSDT',E:now,c:'100',P:'-2',b:'99',a:'101',h:'110',l:'90',q:'1000000'};
assert.equal(parseTicker(ticker,'BTCUSDT',now).c,100);
for (const change of [{s:'ETHUSDT'},{E:now-16000},{E:now+61000},{a:'98'},{c:'NaN'},{b:null},{q:-1},{l:0}]) {
  assert.equal(parseTicker({...ticker,...change},'BTCUSDT',now),null);
}
assert.equal(parseTicker(ticker,'BTCUSDT',now,now),null);

const elements = {};
const el = id => elements[id] ||= {value:id==='symbol'?'BTCUSDT':'',textContent:'',dataset:{},
  addEventListener(event,fn){this[event]=fn;},setAttribute(k,v){this[k]=v;}};
const sockets=[], timers=new Map(), intervals=new Map(); let seq=0;
class Socket {
  constructor(url){this.url=url;sockets.push(this);}
  close(){this.closed=true;}
  message(data){this.onmessage({data:JSON.stringify(data)});}
}
const document={hidden:false,getElementById:el,addEventListener(e,fn){this[e]=fn;}};
const window={addEventListener(e,fn){this[e]=fn;}};
vm.runInNewContext(fs.readFileSync(source,'utf8'),{document,window,WebSocket:Socket,Date,
  setTimeout(fn,ms){const id=++seq;timers.set(id,{fn,ms});return id;},clearTimeout(id){timers.delete(id);},
  setInterval(fn){const id=++seq;intervals.set(id,fn);return id;},clearInterval(id){intervals.delete(id);}});
assert.equal(sockets.length,1);
assert.match(sockets[0].url,/btcusdt@ticker$/);
sockets[0].message(ticker);
assert.equal(el('price').textContent,'100');
assert.equal(el('status').dataset.live,'true');
sockets[0].message({...ticker,c:'999',E:now-20000});
assert.equal(el('price').textContent,'100');
el('symbol').value='ETHUSDT';el('symbol').change();
assert.ok(sockets[0].closed);
assert.equal(el('price').textContent,'—');
sockets[0].message({...ticker,E:now+1});
assert.equal(el('price').textContent,'—');
sockets[1].message({...ticker,s:'ETHUSDT',E:now+2,c:'200'});
assert.equal(el('price').textContent,'200');
sockets[1].onclose();
assert.equal(el('status').dataset.live,'false');
assert.equal(timers.size,1);
assert.equal(el('price').textContent,'200');
document.hidden=true;document.visibilitychange();
assert.equal(timers.size,0);
document.hidden=false;document.visibilitychange();
assert.equal(sockets.length,3);
window.pagehide();
assert.ok(sockets[2].closed);
assert.equal(intervals.size,0);
console.log('OK: validación, cambio de par, eventos viejos, reconexión y limpieza.');
