# Translation Guidelines / Guías de Traducción

## English

### Guidelines for Translating README to Spanish

Thank you for helping maintain the Spanish translation of our README! Follow these guidelines to ensure consistency and quality.

#### General Principles
- **Maintain Structure**: Keep the same markdown structure, headers, and formatting
- **Preserve Code**: Leave all code blocks, commands, and technical syntax unchanged
- **Technical Terms**: Keep widely-used technical terms in English (API, GitHub, URL, etc.)
- **Links**: Translate link text but verify URLs still work
- **Consistency**: Use consistent terminology throughout the document

#### Translation Approach
1. **Read the entire README.md first** to understand the context
2. **Translate section by section** maintaining the same order
3. **Keep the same header levels** (# ## ###)
4. **Preserve all markdown formatting** (bold, italic, code blocks, lists)
5. **Test all code examples** to ensure they work the same way

#### Specific Guidelines

**Code Blocks**: Never translate
```bash
# Keep exactly as is
streamlit run main.py
```

**File Names**: Keep in English
- `main.py` ✅
- `principal.py` ❌

**Technical Terms**: Keep in English when commonly used
- API ✅ (not "Interfaz de Programación de Aplicaciones")
- GitHub ✅
- Streamlit ✅
- Python ✅

**Command-line Instructions**: Translate descriptions, keep commands
```bash
# Translate: "Install dependencies"
# To: "Instalar dependencias"
pip install -r requirements.txt
```

#### Review Checklist
- [ ] All headers translated appropriately
- [ ] Code blocks remain unchanged
- [ ] Links work correctly
- [ ] Technical terms are consistent
- [ ] Formatting matches original
- [ ] Instructions are clear in Spanish

---

## Español

### Guías para Traducir el README al Español

¡Gracias por ayudar a mantener la traducción al español de nuestro README! Sigue estas guías para asegurar consistencia y calidad.

#### Principios Generales
- **Mantener Estructura**: Conserva la misma estructura markdown, encabezados y formato
- **Preservar Código**: Deja todos los bloques de código, comandos y sintaxis técnica sin cambios
- **Términos Técnicos**: Mantén términos técnicos ampliamente usados en inglés (API, GitHub, URL, etc.)
- **Enlaces**: Traduce el texto de los enlaces pero verifica que las URLs sigan funcionando
- **Consistencia**: Usa terminología consistente en todo el documento

#### Enfoque de Traducción
1. **Lee todo el README.md primero** para entender el contexto
2. **Traduce sección por sección** manteniendo el mismo orden
3. **Mantén los mismos niveles de encabezado** (# ## ###)
4. **Preserva todo el formato markdown** (negrita, cursiva, bloques de código, listas)
5. **Prueba todos los ejemplos de código** para asegurar que funcionen igual

#### Guías Específicas

**Bloques de Código**: Nunca traducir
```bash
# Mantener exactamente como está
streamlit run main.py
```

**Nombres de Archivos**: Mantener en inglés
- `main.py` ✅
- `principal.py` ❌

**Términos Técnicos**: Mantener en inglés cuando son comúnmente usados
- API ✅ (no "Interfaz de Programación de Aplicaciones")
- GitHub ✅
- Streamlit ✅
- Python ✅

**Instrucciones de Línea de Comandos**: Traducir descripciones, mantener comandos
```bash
# Traducir: "Install dependencies"
# A: "Instalar dependencias"
pip install -r requirements.txt
```

#### Lista de Verificación
- [ ] Todos los encabezados traducidos apropiadamente
- [ ] Bloques de código permanecen sin cambios
- [ ] Enlaces funcionan correctamente
- [ ] Términos técnicos son consistentes
- [ ] Formato coincide con el original
- [ ] Instrucciones son claras en español