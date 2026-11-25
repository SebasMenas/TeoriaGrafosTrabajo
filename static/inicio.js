const formulario = document.getElementById('formulario');
const selector = document.getElementById('caso');
const boton = formulario.querySelector('button');
const aviso = document.getElementById('aviso');
const resultado = document.getElementById('resultado');

let ultimoResultado = null;
let modoVistaActual = 'ruta';

// Los escenarios derivados permiten comprobar el contrato antes de crear el editor.
function modificarCaso(grafo, caso) {
  for (const arco of grafo.arcos) {
    if (caso === 'bloqueo' && arco.origen === 'D' && arco.destino === 't') {
      arco.activo = false;
    }
    if (caso === 'desconectado' && arco.destino === 't') arco.activo = false;
  }
  if (caso === 'atajo') grafo.arcos.push({ origen: 'C', destino: 't', activo: true });
}

// Configura los botones para alternar entre ver ruta mínima, caminos disjuntos o corte.
document.querySelectorAll('.btn-vista').forEach(botonVista => {
  botonVista.addEventListener('click', () => {
    document.querySelectorAll('.btn-vista').forEach(b => b.classList.remove('activo'));
    botonVista.classList.add('activo');
    modoVistaActual = botonVista.dataset.modo;
    if (ultimoResultado) {
      Plano.aplicarModoVista(modoVistaActual, ultimoResultado);
    }
  });
});

async function analizar() {
  const caso = selector.value;
  resultado.hidden = true;
  selector.disabled = true;
  boton.disabled = true;
  aviso.classList.remove('error');
  aviso.textContent = 'Calculando…';
  try {
    const nombre = caso === 'manual' ? 'manual' : 'original';
    const carga = await fetch(`/casos/${nombre}`);
    if (!carga.ok) throw new Error('No se pudo cargar la configuración.');
    const grafo = await carga.json();
    modificarCaso(grafo, caso);
    // Se dibuja antes de analizar para que el plano exista aunque falle la API.
    Plano.dibujarRed(grafo, { caso });

    const respuesta = await fetch('/analizar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(grafo)
    });
    const datos = await respuesta.json();
    if (!respuesta.ok) throw new Error(datos.error);

    ultimoResultado = datos;

    const activos = grafo.arcos.filter(arco => arco.activo).length;
    document.getElementById('modelo').textContent = `${grafo.vertices.length} espacios y ${activos} pasillos activos. Entrada ${grafo.entrada}, salida ${grafo.salida}.`;
    document.getElementById('ruta').textContent = datos.ruta ? datos.ruta.join(' → ') : 'Sin ruta disponible';
    document.getElementById('distancia').textContent = datos.distancia ?? 'Sin longitud';

    // Poblar familia de rutas disjuntas
    const elemMaximo = document.getElementById('maximo');
    if (elemMaximo) {
      elemMaximo.textContent = datos.maximo !== null ? `${datos.maximo} ${datos.maximo === 1 ? 'ruta' : 'rutas'}` : 'Sin valor';
    }
    const listaCaminos = document.getElementById('lista-caminos');
    if (listaCaminos) {
      if (Array.isArray(datos.caminos) && datos.caminos.length > 0) {
        listaCaminos.innerHTML = datos.caminos
          .map((camino, idx) => `<div>Ruta ${idx + 1}: ${camino.join(' → ')}</div>`)
          .join('');
      } else {
        listaCaminos.textContent = 'Ninguna ruta disponible';
      }
    }

    // Poblar corte mínimo
    const elemTamanoCorte = document.getElementById('tamano-corte');
    if (elemTamanoCorte) {
      elemTamanoCorte.textContent = datos.corte !== null ? `${datos.corte.length} ${datos.corte.length === 1 ? 'pasillo' : 'pasillos'}` : 'Sin valor';
    }
    const listaCorte = document.getElementById('lista-corte');
    if (listaCorte) {
      if (Array.isArray(datos.corte) && datos.corte.length > 0) {
        listaCorte.innerHTML = datos.corte
          .map(([u, v]) => `<div>${u} → ${v}</div>`)
          .join('');
      } else {
        listaCorte.textContent = 'Corte vacío (0 arcos)';
      }
    }

    let mensaje = 'Todos los cálculos están disponibles en la respuesta del servidor.';
    if (datos.ruta === null) {
      mensaje = 'La red está desconectada. Hay cero rutas disponibles y el conjunto vacío es un corte mínimo.';
      Plano.limpiarResaltes();
    } else {
      // Conectar los resultados recibidos al plano SVG
      Plano.aplicarModoVista(modoVistaActual, datos);
    }
    document.getElementById('pendientes').textContent = mensaje;
    document.getElementById('entrada-json').textContent = JSON.stringify(grafo, null, 2);
    document.getElementById('salida-json').textContent = JSON.stringify(datos, null, 2);
    resultado.hidden = false;
    aviso.textContent = 'Cálculo completado.';
  } catch (error) {
    aviso.textContent = error.message;
    aviso.classList.add('error');
  } finally {
    selector.disabled = false;
    boton.disabled = false;
  }
}

formulario.addEventListener('submit', evento => {
  evento.preventDefault();
  analizar();
});
selector.addEventListener('change', analizar);
analizar();

