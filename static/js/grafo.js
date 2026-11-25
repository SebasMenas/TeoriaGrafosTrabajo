// Dibujo del plano dirigido (T05). El trazado no depende de la respuesta del
// análisis: se dibuja igual con o sin resultados, antes de consultar la API.
'use strict';

const NS_SVG = 'http://www.w3.org/2000/svg';
const RADIO_VERTICE = 18;
const HOLGURA_BORDE = 1; // el trazo del círculo ocupa parte del borde

// Crea un elemento SVG y aplica todos sus atributos.
function crearEtiqueta(nombre, atributos = {}) {
  const elemento = document.createElementNS(NS_SVG, nombre);
  for (const [clave, valor] of Object.entries(atributos)) {
    elemento.setAttribute(clave, valor);
  }
  return elemento;
}

// Recorta el segmento en ambos círculos: la punta queda en el borde del destino.
function recortarArco(origen, destino) {
  const dx = destino.x - origen.x;
  const dy = destino.y - origen.y;
  const largo = Math.hypot(dx, dy) || 1;
  const ux = dx / largo;
  const uy = dy / largo;
  return {
    x1: origen.x + ux * RADIO_VERTICE,
    y1: origen.y + uy * RADIO_VERTICE,
    x2: destino.x - ux * (RADIO_VERTICE + HOLGURA_BORDE),
    y2: destino.y - uy * (RADIO_VERTICE + HOLGURA_BORDE)
  };
}

// Dibuja un arco como línea con flecha; el estado bloqueado se anuncia en <title>.
function dibujarArco(arco, posiciones) {
  const desde = posiciones[arco.origen];
  const hasta = posiciones[arco.destino];
  if (!desde || !hasta) return null;

  const activo = arco.activo !== false;
  const linea = crearEtiqueta('line', {
    ...recortarArco(desde, hasta),
    class: activo ? 'arco' : 'arco bloqueado',
    'marker-end': `url(#flecha-${activo ? 'activa' : 'bloqueada'})`,
    'data-origen': arco.origen,
    'data-destino': arco.destino
  });

  const titulo = crearEtiqueta('title');
  titulo.textContent = `Pasillo ${arco.origen} → ${arco.destino}${activo ? '' : ': bloqueado'}`;
  linea.append(titulo);
  return linea;
}

// Coloca la palabra “bloqueado” junto al arco para no depender solo del color.
function dibujarEtiquetaBloqueado(arco, posiciones) {
  const desde = posiciones[arco.origen];
  const hasta = posiciones[arco.destino];
  const etiqueta = crearEtiqueta('text', {
    x: (desde.x + hasta.x) / 2,
    y: (desde.y + hasta.y) / 2 - 7,
    class: 'etiqueta-bloqueado',
    'text-anchor': 'middle',
    'pointer-events': 'none'
  });
  etiqueta.textContent = 'bloqueado';
  return etiqueta;
}

// Dibuja un vértice relleno y con etiqueta; entrada y salida usan otra clase.
function dibujarVertice(nombre, posicion, esEntrada, esSalida) {
  const clases = ['vertice'];
  if (esEntrada) clases.push('entrada');
  if (esSalida) clases.push('salida');

  const grupo = crearEtiqueta('g', { class: clases.join(' ') });
  const circulo = crearEtiqueta('circle', {
    cx: posicion.x,
    cy: posicion.y,
    r: RADIO_VERTICE
  });
  const etiqueta = crearEtiqueta('text', {
    x: posicion.x,
    y: posicion.y,
    'text-anchor': 'middle',
    'dominant-baseline': 'central'
  });
  etiqueta.textContent = nombre;

  const roles = [];
  if (esEntrada) roles.push('entrada');
  if (esSalida) roles.push('salida');
  const titulo = crearEtiqueta('title');
  titulo.textContent = `Vértice ${nombre}${roles.length ? ` (${roles.join(', ')})` : ''}`;

  grupo.append(titulo, circulo, etiqueta);
  return grupo;
}

// Respaldo sin posiciones: columnas por distancia BFS desde la entrada.
function layoutPorCapas(grafo) {
  const capas = new Map();
  const adyacencia = new Map(grafo.vertices.map(v => [v, []]));
  for (const arco of grafo.arcos) {
    if (arco.activo !== false && adyacencia.has(arco.origen)) {
      adyacencia.get(arco.origen).push(arco.destino);
    }
  }

  if (grafo.vertices.includes(grafo.entrada)) {
    capas.set(grafo.entrada, 0);
    const cola = [grafo.entrada];
    while (cola.length > 0) {
      const actual = cola.shift();
      for (const vecino of adyacencia.get(actual) || []) {
        if (!capas.has(vecino)) {
          capas.set(vecino, capas.get(actual) + 1);
          cola.push(vecino);
        }
      }
    }
  }

  // Los vértices inalcanzables comparten una capa final para no perderlos.
  const capaFinal = capas.size > 0 ? Math.max(...capas.values()) + 1 : 0;
  for (const nombre of grafo.vertices) {
    if (!capas.has(nombre)) capas.set(nombre, capaFinal);
  }

  const totalCapas = Math.max(...capas.values()) + 1;
  const grupos = Array.from({ length: totalCapas }, () => []);
  for (const nombre of grafo.vertices) grupos[capas.get(nombre)].push(nombre);

  const posiciones = {};
  const xInicial = 50;
  const xFinal = 570;
  const yInicial = 40;
  const yFinal = 180;
  grupos.forEach((nombres, indice) => {
    const x = totalCapas === 1
      ? 310
      : xInicial + ((xFinal - xInicial) * indice) / (totalCapas - 1);
    nombres.forEach((nombre, fila) => {
      const y = nombres.length === 1
        ? 110
        : yInicial + ((yFinal - yInicial) * fila) / (nombres.length - 1);
      posiciones[nombre] = { x, y };
    });
  });
  return posiciones;
}

// Prefiere posiciones del propio grafo y luego el catálogo indexado por caso.
function resolverPosiciones(grafo, caso) {
  if (grafo.posiciones && grafo.vertices.every(v => grafo.posiciones[v])) {
    return { posiciones: grafo.posiciones, definidas: true };
  }
  const catalogo = typeof POSICIONES === 'object' && POSICIONES !== null ? POSICIONES : {};
  const delCaso = caso ? catalogo[caso] : null;
  if (delCaso && grafo.vertices.every(v => delCaso[v])) {
    return { posiciones: delCaso, definidas: true };
  }
  return { posiciones: layoutPorCapas(grafo), definidas: false };
}

// Texto de estado: el color de un pasillo bloqueado nunca queda solo.
function describirRed(grafo, definidas) {
  const bloqueados = grafo.arcos
    .filter(arco => arco.activo === false)
    .map(arco => `${arco.origen} → ${arco.destino}`);
  const partes = [];

  if (!definidas) {
    partes.push('Este caso no tiene posiciones definidas: se usa un diseño por capas BFS desde la entrada.');
  }
  partes.push(`${grafo.vertices.length} vértices y ${grafo.arcos.length} arcos dibujados.`);
  if (bloqueados.length === 0) {
    partes.push('Ningún pasillo bloqueado.');
  } else if (bloqueados.length === 1) {
    partes.push(`1 pasillo bloqueado: ${bloqueados[0]}.`);
  } else {
    partes.push(`${bloqueados.length} pasillos bloqueados: ${bloqueados.join(', ')}.`);
  }
  return partes.join(' ');
}

// Redibuja la red: primero los arcos y después los vértices para quedar encima.
function dibujarRed(grafo, opciones = {}) {
  const capaArcos = document.getElementById('capa-arcos');
  const capaVertices = document.getElementById('capa-vertices');
  if (!capaArcos || !capaVertices) return;

  const { posiciones, definidas } = resolverPosiciones(grafo, opciones.caso);

  capaArcos.replaceChildren();
  capaVertices.replaceChildren();

  for (const arco of grafo.arcos) {
    const linea = dibujarArco(arco, posiciones);
    if (!linea) continue;
    if (typeof opciones.alSeleccionarArco === 'function') {
      linea.addEventListener('click', () => opciones.alSeleccionarArco(arco.origen, arco.destino));
    }
    capaArcos.append(linea);
    if (arco.activo === false) {
      capaArcos.append(dibujarEtiquetaBloqueado(arco, posiciones));
    }
  }
  for (const nombre of grafo.vertices) {
    const posicion = posiciones[nombre];
    if (!posicion) continue;
    capaVertices.append(
      dibujarVertice(nombre, posicion, nombre === grafo.entrada, nombre === grafo.salida)
    );
  }

  const titulo = capaArcos.ownerSVGElement.querySelector('title');
  if (titulo) {
    titulo.textContent = `Plano dirigido de la red con ${grafo.vertices.length} vértices y ${grafo.arcos.length} arcos`;
  }

  const aviso = document.getElementById('plano-aviso');
  if (aviso) aviso.textContent = describirRed(grafo, definidas);
}

// Busca un elemento arco en el SVG mediante sus atributos de origen y destino.
function obtenerElementoArco(origen, destino) {
  return Array.from(document.querySelectorAll('#capa-arcos line')).find(linea => (
    linea.dataset.origen === origen && linea.dataset.destino === destino
  )) || null;
}

// Remueve las clases de resalte y restablece el marcador original de cada arco.
function limpiarResaltes() {
  const lineas = document.querySelectorAll('#capa-arcos line');
  for (const linea of lineas) {
    linea.classList.remove('ruta', 'familia', 'familia-0', 'familia-1', 'corte');
    const bloqueado = linea.classList.contains('bloqueado');
    linea.setAttribute('marker-end', `url(#flecha-${bloqueado ? 'bloqueada' : 'activa'})`);
  }
}

// Resalta la ruta mínima (lista de vértices de s a t).
function resaltarRuta(ruta) {
  if (!Array.isArray(ruta) || ruta.length < 2) return;
  for (let i = 0; i < ruta.length - 1; i++) {
    const linea = obtenerElementoArco(ruta[i], ruta[i + 1]);
    if (linea) {
      linea.classList.add('ruta');
      linea.setAttribute('marker-end', 'url(#flecha-ruta)');
      // Reinsertar al final de la capa para que se dibuje por encima de arcos comunes
      linea.parentElement.append(linea);
    }
  }
}

// Resalta la familia de caminos disjuntos (lista de listas de vértices).
function resaltarFamilia(caminos) {
  if (!Array.isArray(caminos) || caminos.length === 0) return;
  caminos.forEach((camino, indice) => {
    const claseVariante = `familia-${indice % 2}`;
    const idFlecha = indice % 2 === 0 ? 'url(#flecha-familia)' : 'url(#flecha-familia-alt)';
    for (let i = 0; i < camino.length - 1; i++) {
      const linea = obtenerElementoArco(camino[i], camino[i + 1]);
      if (linea) {
        linea.classList.add('familia', claseVariante);
        linea.setAttribute('marker-end', idFlecha);
        linea.parentElement.append(linea);
      }
    }
  });
}

// Resalta los arcos del corte mínimo (lista de pares [origen, destino]).
function resaltarCorte(corte) {
  if (!Array.isArray(corte) || corte.length === 0) return;
  for (const par of corte) {
    if (!Array.isArray(par) || par.length < 2) continue;
    const [origen, destino] = par;
    const linea = obtenerElementoArco(origen, destino);
    if (linea) {
      linea.classList.add('corte');
      linea.setAttribute('marker-end', 'url(#flecha-corte)');
      linea.parentElement.append(linea);
    }
  }
}

// Aplica el modo de visualización seleccionado según los datos recibidos del servidor.
function aplicarModoVista(modo, datos) {
  limpiarResaltes();
  if (!datos || datos.ruta === null) return;

  if (modo === 'ruta') {
    resaltarRuta(datos.ruta);
  } else if (modo === 'familia') {
    resaltarFamilia(datos.caminos);
  } else if (modo === 'corte') {
    resaltarCorte(datos.corte);
  }
}

window.Plano = {
  dibujarRed,
  dibujarArco,
  dibujarVertice,
  limpiarResaltes,
  resaltarRuta,
  resaltarFamilia,
  resaltarCorte,
  aplicarModoVista
};
