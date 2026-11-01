# Proyecto Aranza v1.37

## Detección conservadora de posibles contradicciones

- La comprobación de recuerdos identifica pares de expresiones afirmativas/negativas sobre un tema léxicamente cercano, por ejemplo “me gusta X” frente a “no me gusta X”.
- Los candidatos se etiquetan como `posible_contradiccion` y se acompañan de una nota para revisión humana.
- La interfaz diferencia posibles contradicciones, posibles duplicados y recuerdos relacionados.
- No se modifica, archiva ni elimina ningún recuerdo automáticamente.
- No se añadieron dependencias externas.

## Limitaciones

La detección se basa en patrones de texto y proximidad léxica. Puede omitir contradicciones expresadas de otra manera y puede señalar falsos positivos. La etiqueta no es una conclusión semántica.
