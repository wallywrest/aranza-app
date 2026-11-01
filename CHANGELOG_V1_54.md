# Proyecto Aranza v1.54

## Evaluación estratificada del recuperador de memoria

- Añade el campo opcional `group` a los escenarios del benchmark; por defecto usa `general`.
- El fingerprint incluye el grupo, por lo que un cambio de clasificación queda registrado como cambio de definición.
- El informe JSON incluye `group` por escenario y `group_summary` con promedios macro de precisión, recall y F1, además de totales de recuerdos omitidos e inesperados.
- Amplía los escenarios integrados para cubrir recuperación de múltiples recuerdos y distractores de tema cercano.
- Mantiene las métricas por escenario y el formato de informe compatible con el comparador.

## Uso

```bash
python ejecutar_benchmark_memoria.py --output benchmark.json
```

Los grupos son etiquetas de evaluación, no juicios semánticos automáticos. Los promedios macro dan el mismo peso a cada escenario de un grupo y pueden ocultar variaciones individuales; revisar siempre `cases`.
