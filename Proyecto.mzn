% Proyecto de Análisis de Algoritmos II
% Problema de Minimizar la Polarización presente en una Población (MinPol)
%
% Los valores de opinión y los costos se reciben como enteros escalados.
% Esto evita errores de punto flotante y mantiene el modelo compatible con
% solvers de programación entera.

% ---------------------------------------------------------------------------
% Datos de entrada
% ---------------------------------------------------------------------------

int: n;
int: m;
set of int: OPINIONES = 1..m;

array[OPINIONES] of int: p;

% v[i] = v_original[i] * escala_v
int: escala_v;
array[OPINIONES] of int: v;

% c, ce y ct están multiplicados por escala_costo.
int: escala_costo;
array[OPINIONES, OPINIONES] of int: c;
array[OPINIONES] of int: ce;
int: ct;

% ---------------------------------------------------------------------------
% Validaciones estáticas
% ---------------------------------------------------------------------------

constraint n > 0;
constraint m > 0;
constraint escala_v > 0;
constraint escala_costo > 0;
constraint forall(i in OPINIONES)(p[i] >= 0);
constraint sum(i in OPINIONES)(p[i]) = n;
constraint forall(i in OPINIONES)(v[i] >= 0 /\ v[i] <= escala_v);
constraint forall(i, j in OPINIONES)(c[i, j] >= 0);
constraint forall(j in OPINIONES)(ce[j] >= 0);
constraint ct >= 0;

% ---------------------------------------------------------------------------
% Variables de movimientos y distribución final
% ---------------------------------------------------------------------------

% x[i,j]: personas que pasan de la opinión inicial i a la opinión j.
array[OPINIONES, OPINIONES] of var 0..n: x;

% No se considera movimiento permanecer en la misma opinión.
constraint forall(i in OPINIONES)(x[i, i] = 0);

% Solo pueden moverse las personas que pertenecían inicialmente al origen.
constraint forall(i in OPINIONES)(
    sum(j in OPINIONES where j != i)(x[i, j]) <= p[i]
);

% Distribución después de aplicar todos los movimientos.
array[OPINIONES] of var 0..n: distribucion_final;

constraint forall(i in OPINIONES)(
    distribucion_final[i] =
        p[i]
        - sum(j in OPINIONES where j != i)(x[i, j])
        + sum(j in OPINIONES where j != i)(x[j, i])
);

% Es redundante con los balances, pero documenta y comprueba la conservación.
constraint sum(i in OPINIONES)(distribucion_final[i]) = n;

% ---------------------------------------------------------------------------
% Costo
% ---------------------------------------------------------------------------

% El costo real por persona es:
%   c[i,j] * (1 + p[i]/n) + ce[j], si p[j] = 0.
%
% costo_unitario_numerador está escalado por n * escala_costo.
array[OPINIONES, OPINIONES] of int: costo_unitario_numerador =
    array2d(OPINIONES, OPINIONES, [
        c[i, j] * (n + p[i])
        + (if p[j] = 0 then ce[j] * n else 0 endif)
        | i, j in OPINIONES
    ]);

var 0..sum(i, j in OPINIONES)(
    costo_unitario_numerador[i, j] * p[i]
): costo_total_numerador =
    sum(i, j in OPINIONES where i != j)(
        costo_unitario_numerador[i, j] * x[i, j]
    );

% ct también está escalado por escala_costo.
constraint costo_total_numerador <= ct * n;

% ---------------------------------------------------------------------------
% Mediana ponderada y polarización
% ---------------------------------------------------------------------------

% seleccion_mediana[k] = 1 si v[k] es la mediana elegida.
array[OPINIONES] of var 0..1: seleccion_mediana;
constraint sum(k in OPINIONES)(seleccion_mediana[k]) = 1;

% producto_mediana[i,k] linealiza:
% distribucion_final[i] * seleccion_mediana[k].
array[OPINIONES, OPINIONES] of var 0..n: producto_mediana;

constraint forall(i, k in OPINIONES)(
    producto_mediana[i, k] <= distribucion_final[i] /\
    producto_mediana[i, k] <= n * seleccion_mediana[k] /\
    producto_mediana[i, k] >=
        distribucion_final[i] - n * (1 - seleccion_mediana[k])
);

var 1..m: indice_mediana =
    sum(k in OPINIONES)(k * seleccion_mediana[k]);

var 0..escala_v: valor_mediana_escalado =
    sum(k in OPINIONES)(v[k] * seleccion_mediana[k]);

% polarizacion_escalada = polarización real * escala_v.
var 0..n * escala_v: polarizacion_escalada =
    sum(i, k in OPINIONES)(
        abs(v[i] - v[k]) * producto_mediana[i, k]
    );

solve minimize polarizacion_escalada;

% ---------------------------------------------------------------------------
% Salida legible y estable para la interfaz gráfica
% ---------------------------------------------------------------------------

output [
    "MATRIZ_MOVIMIENTOS\n",
    concat([
        concat([
            show(x[i, j]) ++
            (if j < m then "," else "\n" endif)
            | j in OPINIONES
        ])
        | i in OPINIONES
    ]),
    "DISTRIBUCION_FINAL=" ++
        show([distribucion_final[i] | i in OPINIONES]) ++ "\n",
    "COSTO_TOTAL=" ++ show(costo_total_numerador) ++ "/" ++
        show(n * escala_costo) ++ "\n",
    "COSTO_TOTAL_NUMERADOR=" ++ show(costo_total_numerador) ++ "\n",
    "COSTO_TOTAL_DENOMINADOR=" ++ show(n * escala_costo) ++ "\n",
    "POLARIZACION=" ++ show(polarizacion_escalada) ++ "/" ++
        show(escala_v) ++ "\n",
    "POLARIZACION_ESCALADA=" ++ show(polarizacion_escalada) ++ "\n",
    "POLARIZACION_ESCALA=" ++ show(escala_v) ++ "\n",
    "INDICE_MEDIANA=" ++ show(indice_mediana) ++ "\n",
    "VALOR_MEDIANA=" ++ show(valor_mediana_escalado) ++ "/" ++
        show(escala_v) ++ "\n",
    "VALOR_MEDIANA_ESCALADO=" ++ show(valor_mediana_escalado) ++ "\n",
    "VALOR_MEDIANA_ESCALA=" ++ show(escala_v) ++ "\n"
];
