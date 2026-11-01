# Aranza v1.92 — comparación conservadora de afirmaciones

- Añade comparación entre fragmentos de páginas efectivamente leídas, nunca entre snippets no verificados.
- Detecta candidatos a discrepancia cuando dos fuentes comparten términos relevantes y difieren en cifras o polaridad.
- Devuelve extractos, dominios, enlaces, términos compartidos y motivo de revisión.
- Limita la comparación a cinco fuentes, 80 oraciones por fuente y ocho candidatos.
- Integra `claim_comparison` en `source_assessment`, que ya acompaña a investigación web y al contexto del chat.
- No decide cuál fuente es correcta y advierte que fechas, unidades, población o contexto pueden explicar diferencias.

## Límites

No es un modelo semántico ni una verificación factual. Puede omitir paráfrasis, detectar coincidencias engañosas o no reconocer diferencias de contexto. Los candidatos requieren revisión humana.
