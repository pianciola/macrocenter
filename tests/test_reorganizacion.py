"""Regresiones de la fila de pestañas."""
import shutil
import subprocess

import pytest

from macrocenter import style


def test_desplazamiento_recupera_inicio_y_respeta_area_libre():
    node = shutil.which("node")
    if not node:
        pytest.skip("Requiere Node")
    inicio = style.JS_PESTANAS.index("  const destinoPara = (tab) => {")
    fin = style.JS_PESTANAS.index("  // Streamlit desliza", inicio)
    codigo = style.JS_PESTANAS[inicio:fin] + '''
const assert = require('node:assert/strict');
const tabs = [];
const c = {scrollWidth: 2200, clientWidth: 700, scrollLeft: 600,
  getBoundingClientRect: () => ({left:100,right:800}), querySelectorAll: () => tabs};
function tab(left,width) { return {closest:()=>c,
  getBoundingClientRect:()=>({left:left-c.scrollLeft,right:left-c.scrollLeft+width,width})}; }
tabs.push({closest:()=>c,getBoundingClientRect:()=>({left:110,right:280,width:170})});
tabs.push(tab(310,100), tab(450,100), tab(1300,200), tab(2000,200));
global.getComputedStyle = () => ({position:'sticky'});
assert.equal(destinoPara(tabs[0]).left,0);
assert.equal(destinoPara(tabs[1]).left,0);
assert.equal(destinoPara(tabs[2]).left,150);
assert.equal(destinoPara(tabs[3]).left,708);
c.scrollLeft=1500;
assert.equal(destinoPara(tabs[4]),null);
global.getComputedStyle = () => ({position:'relative'});
c.scrollLeft=0;
assert.equal(destinoPara(tabs[2]),null);
c.scrollWidth=650;
assert.equal(destinoPara(tabs[0]),null);
'''
    resultado = subprocess.run([node, "-"], input=codigo, capture_output=True, text=True, timeout=15)
    assert resultado.returncode == 0, resultado.stderr
