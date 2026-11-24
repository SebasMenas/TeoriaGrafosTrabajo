// Coordenadas del plano en el sistema del viewBox 620×220.
// Replican la figura 1 del informe; se indexan por nombre de caso.
// Los escenarios derivados del selector reutilizan la red original.
const POSICIONES = {
  original: {
    s: { x: 40, y: 102 },
    A: { x: 150, y: 20 },
    B: { x: 150, y: 102 },
    C: { x: 150, y: 185 },
    E: { x: 260, y: 75 },
    G: { x: 260, y: 152 },
    D: { x: 360, y: 20 },
    F: { x: 360, y: 102 },
    H: { x: 360, y: 185 },
    I: { x: 470, y: 141 },
    t: { x: 580, y: 58 }
  }
};

POSICIONES.bloqueo = POSICIONES.original;
POSICIONES.atajo = POSICIONES.original;
POSICIONES.desconectado = POSICIONES.original;
