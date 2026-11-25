'use strict';

const elementos = {
  formularioCaso: document.getElementById('formulario-caso'),
  selectorCaso: document.getElementById('caso'),
  restaurar: document.getElementById('restaurar'),
  recalcular: document.getElementById('recalcular'),
  listaArcos: document.getElementById('lista-arcos'),
  formularioArco: document.getElementById('formulario-arco'),
  arcoOrigen: document.getElementById('arco-origen'),
  arcoDestino: document.getElementById('arco-destino'),
  errorArco: document.getElementById('error-arco'),
  formularioExtremos: document.getElementById('formulario-extremos'),
  extremoEntrada: document.getElementById('extremo-entrada'),
  extremoSalida: document.getElementById('extremo-salida'),
  errorExtremos: document.getElementById('error-extremos'),
  aviso: document.getElementById('aviso'),
  resultado: document.getElementById('resultado'),
  estadoResultado: document.getElementById('estado-resultado')
};

let estado = null;
let cargando = false;
let calculando = false;

// Conserva solo el contrato de la red y explicita el estado de cada pasillo.
function normalizarGrafo(grafo) {
  return {
    vertices: [...grafo.vertices],
    entrada: grafo.entrada,
    salida: grafo.salida,
    arcos: grafo.arcos.map(arco => ({
      origen: arco.origen,
      destino: arco.destino,
      activo: arco.activo !== false
    }))
  };
}

// Convierte cualquier error HTTP en el mensaje enviado por Flask.
async function pedirJSON(url, opciones = {}) {
  const respuesta = await fetch(url, opciones);
  let datos;
  try {
    datos = await respuesta.json();
  } catch {
    throw new Error('El servidor no devolvió una respuesta JSON válida.');
  }
  if (!respuesta.ok) {
    throw new Error(datos.error || `Error HTTP ${respuesta.status}.`);
  }
  return datos;
}

// Borra todos los valores anteriores antes de mostrar otro estado del análisis.
function limpiarResultados(mensaje, visible = true) {
  elementos.resultado.hidden = !visible;
  elementos.resultado.classList.remove('error', 'desactualizado');
  elementos.resultado.setAttribute('aria-busy', 'false');
  elementos.estadoResultado.textContent = mensaje;
  for (const id of ['modelo', 'ruta', 'distancia', 'maximo', 'tamano-corte', 'pendientes', 'entrada-json', 'salida-json']) {
    document.getElementById(id).textContent = '';
  }
  document.getElementById('lista-caminos').replaceChildren();
  document.getElementById('lista-corte').replaceChildren();
}

// Deja el error tanto en el aviso general como dentro del panel de resultados.
function mostrarError(mensaje) {
  limpiarResultados(`Error: ${mensaje}`);
  elementos.resultado.classList.add('error');
  elementos.aviso.textContent = mensaje;
  elementos.aviso.classList.add('error');
}

function limpiarErroresControl() {
  elementos.errorArco.textContent = '';
  elementos.errorExtremos.textContent = '';
  for (const selector of [elementos.arcoOrigen, elementos.arcoDestino, elementos.extremoEntrada, elementos.extremoSalida]) {
    selector.removeAttribute('aria-invalid');
  }
}

function actualizarControles() {
  const ocupado = cargando || calculando;
  elementos.selectorCaso.disabled = ocupado;
  elementos.restaurar.disabled = ocupado;
  elementos.recalcular.disabled = ocupado || !estado;
  for (const boton of elementos.listaArcos.querySelectorAll('button')) {
    boton.disabled = ocupado || !estado;
  }
  for (const control of document.querySelectorAll('#editor-red select, #editor-red button')) {
    control.disabled = ocupado || !estado;
  }
}

// Crea un interruptor nativo, operable con teclado, para cada pasillo.
function crearControlArco(arco) {
  const boton = document.createElement('button');
  boton.type = 'button';
  boton.className = 'interruptor-pasillo';
  boton.dataset.origen = arco.origen;
  boton.dataset.destino = arco.destino;
  boton.setAttribute('role', 'switch');
  boton.setAttribute('aria-checked', String(arco.activo));
  boton.setAttribute('aria-label', `Pasillo ${arco.origen} → ${arco.destino}: ${arco.activo ? 'activo' : 'bloqueado'}. ${arco.activo ? 'Bloquear' : 'Restablecer'}.`);

  const nombre = document.createElement('span');
  nombre.className = 'pasillo-nombre';
  nombre.textContent = `${arco.origen} → ${arco.destino}`;
  const situacion = document.createElement('span');
  situacion.className = 'pasillo-estado';
  situacion.textContent = arco.activo ? 'Activo' : 'Bloqueado';

  boton.append(nombre, situacion);
  return boton;
}

// Rellena un selector solo con vértices existentes y conserva una elección válida.
function pobrarSelector(selector, valorPreferido = '') {
  const anterior = selector.value;
  const preferido = estado && estado.vertices.includes(valorPreferido)
    ? valorPreferido
    : estado && estado.vertices.includes(anterior) ? anterior : '';

  selector.replaceChildren();
  const opcionVacia = document.createElement('option');
  opcionVacia.value = '';
  opcionVacia.textContent = 'Selecciona un vértice';
  selector.append(opcionVacia);
  for (const nombre of estado ? estado.vertices : []) {
    const opcion = document.createElement('option');
    opcion.value = nombre;
    opcion.textContent = nombre;
    selector.append(opcion);
  }
  selector.value = preferido;
}

function sincronizarSelectores(reiniciar = false) {
  pobrarSelector(elementos.arcoOrigen, reiniciar ? '' : elementos.arcoOrigen.value);
  pobrarSelector(elementos.arcoDestino, reiniciar ? '' : elementos.arcoDestino.value);
  pobrarSelector(elementos.extremoEntrada, estado ? estado.entrada : '');
  pobrarSelector(elementos.extremoSalida, estado ? estado.salida : '');
}

// Refresca el plano y el inventario desde la única fuente de verdad.
function renderizarEditor(reiniciar = false) {
  sincronizarSelectores(reiniciar);
  if (!estado) {
    elementos.listaArcos.replaceChildren();
    document.getElementById('capa-arcos').replaceChildren();
    document.getElementById('capa-vertices').replaceChildren();
    document.getElementById('plano-aviso').textContent = 'No hay una red cargada.';
    actualizarControles();
    return;
  }

  const fragmento = document.createDocumentFragment();
  for (const arco of estado.arcos) fragmento.append(crearControlArco(arco));
  elementos.listaArcos.replaceChildren(fragmento);
  Plano.dibujarRed(estado, {
    caso: elementos.selectorCaso.value,
    alSeleccionarArco: bloquearArco
  });
  actualizarControles();
}

function marcarDesactualizado(mensaje) {
  limpiarResultados('Desactualizado: pulsa Recalcular para analizar los cambios.');
  elementos.resultado.classList.add('desactualizado');
  elementos.aviso.classList.remove('error');
  elementos.aviso.textContent = mensaje;
}

// Alterna el pasillo sin retirarlo del inventario ni calcular automáticamente.
function bloquearArco(origen, destino) {
  if (!estado || cargando || calculando) return;
  const arco = estado.arcos.find(candidato => candidato.origen === origen && candidato.destino === destino);
  if (!arco) {
    mostrarError('Ese pasillo ya no existe en la red.');
    return;
  }

  arco.activo = !arco.activo;
  renderizarEditor();
  limpiarErroresControl();
  marcarDesactualizado(`Pasillo ${origen} → ${destino} ${arco.activo ? 'restablecido' : 'bloqueado'}. Pulsa Recalcular.`);
}

// Valida lazos, duplicados y recíprocos sobre todo el inventario, incluso bloqueados.
function validarArco(origen, destino) {
  if (!estado || !estado.vertices.includes(origen) || !estado.vertices.includes(destino)) {
    return 'Selecciona un origen y un destino que existan en la red.';
  }
  if (origen === destino) {
    return 'No se permiten lazos: el origen y el destino deben ser distintos.';
  }
  if (estado.arcos.some(arco => arco.origen === origen && arco.destino === destino)) {
    return `El arco ${origen} → ${destino} ya existe en el inventario, aunque esté bloqueado.`;
  }
  if (estado.arcos.some(arco => arco.origen === destino && arco.destino === origen)) {
    return `No se permite el arco recíproco: ${destino} → ${origen} ya existe en el inventario, aunque esté bloqueado.`;
  }
  return '';
}

function agregarArco() {
  if (!estado || cargando || calculando) return;
  limpiarErroresControl();
  const origen = elementos.arcoOrigen.value;
  const destino = elementos.arcoDestino.value;
  const error = validarArco(origen, destino);
  if (error) {
    elementos.errorArco.textContent = error;
    elementos.arcoOrigen.setAttribute('aria-invalid', 'true');
    elementos.arcoDestino.setAttribute('aria-invalid', 'true');
    mostrarError(error);
    return;
  }

  estado.arcos.push({ origen, destino, activo: true });
  renderizarEditor();
  elementos.arcoDestino.value = '';
  marcarDesactualizado(`Arco ${origen} → ${destino} agregado. Pulsa Recalcular.`);
}

function validarExtremos(entrada, salida) {
  if (!estado || !estado.vertices.includes(entrada) || !estado.vertices.includes(salida)) {
    return 'Selecciona una entrada y una salida que existan en la red.';
  }
  if (entrada === salida) {
    return 'La entrada y la salida deben ser vértices distintos.';
  }
  return '';
}

function cambiarExtremos() {
  if (!estado || cargando || calculando) return;
  limpiarErroresControl();
  const entrada = elementos.extremoEntrada.value;
  const salida = elementos.extremoSalida.value;
  const error = validarExtremos(entrada, salida);
  if (error) {
    elementos.errorExtremos.textContent = error;
    elementos.extremoEntrada.setAttribute('aria-invalid', 'true');
    elementos.extremoSalida.setAttribute('aria-invalid', 'true');
    mostrarError(error);
    return;
  }

  estado.entrada = entrada;
  estado.salida = salida;
  renderizarEditor();
  marcarDesactualizado(`Entrada ${entrada} y salida ${salida} actualizadas. Pulsa Recalcular.`);
}

// Llena una lista de resultados sin asumir un orden ni nombres concretos.
function llenarLista(elemento, valores, vacio, formatear) {
  elemento.replaceChildren();
  if (!Array.isArray(valores) || valores.length === 0) {
    elemento.textContent = vacio;
    return;
  }
  const fragmento = document.createDocumentFragment();
  valores.forEach((valor, indice) => {
    const item = document.createElement('div');
    item.textContent = formatear(valor, indice);
    fragmento.append(item);
  });
  elemento.append(fragmento);
}

// Presenta la respuesta del servidor junto con el estado exacto que se envió.
function mostrarResultado(datos, estadoEnviado) {
  limpiarResultados('Resultado correspondiente al estado enviado.');
  const activos = estadoEnviado.arcos.filter(arco => arco.activo).length;
  document.getElementById('modelo').textContent = `${estadoEnviado.vertices.length} espacios y ${activos} pasillos activos. Entrada ${estadoEnviado.entrada}, salida ${estadoEnviado.salida}.`;
  document.getElementById('ruta').textContent = Array.isArray(datos.ruta) && datos.ruta.length > 0
    ? datos.ruta.join(' → ')
    : 'Sin ruta disponible';
  document.getElementById('distancia').textContent = datos.distancia ?? 'Sin longitud';
  document.getElementById('maximo').textContent = datos.maximo === null || datos.maximo === undefined
    ? 'Sin valor'
    : `${datos.maximo} ${datos.maximo === 1 ? 'ruta' : 'rutas'}`;
  document.getElementById('tamano-corte').textContent = Array.isArray(datos.corte)
    ? `${datos.corte.length} ${datos.corte.length === 1 ? 'pasillo' : 'pasillos'}`
    : 'Sin valor';

  llenarLista(
    document.getElementById('lista-caminos'),
    datos.caminos,
    'Ninguna ruta disponible',
    (camino, indice) => `Ruta ${indice + 1}: ${camino.join(' → ')}`
  );
  llenarLista(
    document.getElementById('lista-corte'),
    datos.corte,
    'Corte vacío (0 arcos)',
    par => `${par[0]} → ${par[1]}`
  );

  const pendientes = Array.isArray(datos.calculos_pendientes) ? datos.calculos_pendientes : [];
  document.getElementById('pendientes').textContent = pendientes.length > 0
    ? `Cálculos pendientes: ${pendientes.join(', ')}.`
    : 'Todos los cálculos están disponibles en la respuesta del servidor.';
  document.getElementById('entrada-json').textContent = JSON.stringify(estadoEnviado, null, 2);
  document.getElementById('salida-json').textContent = JSON.stringify(datos, null, 2);
  elementos.aviso.classList.remove('error');
  elementos.aviso.textContent = 'Cálculo completado.';
}

// Envía siempre el inventario completo, incluidos los pasillos bloqueados.
async function recalcular() {
  if (!estado || cargando || calculando) return;
  calculando = true;
  actualizarControles();
  limpiarResultados('Calculando el estado actual…');
  elementos.resultado.setAttribute('aria-busy', 'true');
  elementos.aviso.classList.remove('error');
  elementos.aviso.textContent = 'Calculando…';

  const estadoEnviado = JSON.parse(JSON.stringify(estado));
  try {
    const datos = await pedirJSON('/analizar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(estadoEnviado)
    });
    mostrarResultado(datos, estadoEnviado);
  } catch (error) {
    mostrarError(error.message);
  } finally {
    calculando = false;
    actualizarControles();
  }
}

// Vuelve a GET /casos/<nombre> y descarta cualquier edición local.
async function restaurarRed() {
  cargando = true;
  estado = null;
  renderizarEditor(true);
  actualizarControles();
  limpiarErroresControl();
  limpiarResultados('Cargando la configuración base…', false);
  elementos.aviso.classList.remove('error');
  elementos.aviso.textContent = 'Cargando red…';

  try {
    const grafo = await pedirJSON(`/casos/${encodeURIComponent(elementos.selectorCaso.value)}`);
    estado = normalizarGrafo(grafo);
    renderizarEditor(true);
    limpiarResultados('Red base cargada. Pulsa Recalcular para analizarla.');
    elementos.aviso.textContent = 'Red original restaurada: todos los pasillos están activos.';
  } catch (error) {
    renderizarEditor();
    mostrarError(error.message);
  } finally {
    cargando = false;
    actualizarControles();
  }
}

elementos.listaArcos.addEventListener('click', evento => {
  const boton = evento.target.closest('button[data-origen]');
  if (!boton) return;
  bloquearArco(boton.dataset.origen, boton.dataset.destino);
});
elementos.formularioArco.addEventListener('submit', evento => {
  evento.preventDefault();
  agregarArco();
});
elementos.formularioExtremos.addEventListener('submit', evento => {
  evento.preventDefault();
  cambiarExtremos();
});
elementos.recalcular.addEventListener('click', recalcular);
elementos.formularioCaso.addEventListener('submit', evento => {
  evento.preventDefault();
  restaurarRed();
});

restaurarRed();
