"""
Script para procesar muestras aleatorias del dataset FOLIO.

Descarga el dataset, selecciona 3 registros al azar, y para cada uno:
1. Parsea premisas y conclusión
2. Calcula métricas
3. Genera JSON y SVG
4. Crea un PDF con toda la información (ID, premisas, conclusión, SVG, JSON)
"""

import sys
from pathlib import Path
import json
import random
from datetime import datetime

# Agregar src/ al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from download_folio import download_folio_dataset
from build_conditionals import parse_global_conditional, build_global_conditional
from metrics import calculate_all_metrics
from serialize import export_complete_analysis


def create_pdf_report(record_id, premises_text, conclusion_text, premises_fol, conclusion_fol, svg_path, json_path, output_path, png_path=None, png_scope_path=None):
    """
    Crea un PDF con toda la información del registro.
    
    Args:
        record_id: ID del registro
        premises_text: Lista de premisas en texto natural
        conclusion_text: Conclusión en texto natural
        premises_fol: Lista de premisas en formato FOL
        conclusion_fol: Conclusión en formato FOL
        svg_path: Ruta al archivo SVG
        json_path: Ruta al archivo JSON
        output_path: Ruta donde guardar el PDF
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Preformatted, PageBreak
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
        import cairosvg
    except ImportError as e:
        print(f"⚠ Advertencia: Faltan dependencias para PDF: {e}")
        print("  Instala con: pip install reportlab pillow cairosvg")
        return None
    
    # Crear PDF
    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor='#0066CC',
        spaceAfter=12,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor='#333333',
        spaceAfter=6,
        spaceBefore=12
    )
    body_style = styles['Normal']
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Code'],
        fontSize=8,
        fontName='Courier',
        leftIndent=20,
        rightIndent=20
    )
    
    # Contenido del PDF
    story = []
    
    # Título
    story.append(Paragraph(f"Análisis FOL - Registro ID: {record_id}", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Información del registro
    story.append(Paragraph("<b>Información del Registro</b>", heading_style))
    story.append(Paragraph(f"<b>ID del ejemplo:</b> {record_id}", body_style))
    story.append(Paragraph(f"<b>Fecha de procesamiento:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Premisas en texto natural
    story.append(Paragraph("<b>Premisas (texto natural):</b>", heading_style))
    if isinstance(premises_text, list):
        for i, premise in enumerate(premises_text, 1):
            story.append(Paragraph(f"<b>{i}.</b> {premise}", body_style))
    else:
        story.append(Paragraph(str(premises_text), body_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Conclusión en texto natural
    story.append(Paragraph("<b>Conclusión (texto natural):</b>", heading_style))
    story.append(Paragraph(str(conclusion_text), body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Premisas FOL
    story.append(Paragraph("<b>Premisas FOL:</b>", heading_style))
    if isinstance(premises_fol, list):
        for i, premise in enumerate(premises_fol, 1):
            story.append(Paragraph(f"<b>{i}.</b> {premise}", body_style))
    else:
        story.append(Paragraph(str(premises_fol), body_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Conclusión FOL
    story.append(Paragraph("<b>Conclusión FOL:</b>", heading_style))
    story.append(Paragraph(str(conclusion_fol), body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # SVG/PNG (imagen del árbol básico)
    story.append(Paragraph("<b>Árbol Sintáctico (AST):</b>", heading_style))
    
    # Intentar incluir imagen (PNG preferido, luego SVG convertido)
    image_added = False
    temp_png_to_clean = None
    
    # Priorizar PNG si está disponible
    if png_path and Path(png_path).exists() and Path(png_path).stat().st_size > 0:
        try:
            from PIL import Image as PILImage
            pil_img = PILImage.open(png_path)
            img_width, img_height = pil_img.size
            
            # Escalar manteniendo alta resolución para preservar símbolos Unicode
            # El PNG generado por graphviz ya tiene los símbolos correctamente renderizados
            max_width = 6.5 * inch  # Un poco más de espacio para mejor legibilidad
            if img_width > max_width:
                scale = max_width / img_width
                img_width = max_width
                img_height = img_height * scale
            else:
                # Si la imagen es pequeña, escalar menos para mantener calidad
                # Mantener al menos 80% del tamaño original para preservar detalles
                img_width = min(img_width * 0.85, max_width)
                img_height = img_height * 0.85
            
            # Usar ruta absoluta y verificar que el archivo existe antes de crear Image
            png_abs = Path(png_path).absolute()
            if not png_abs.exists():
                raise FileNotFoundError(f"PNG no existe: {png_abs}")
            
            img = Image(str(png_abs), width=img_width, height=img_height)
            story.append(img)
            story.append(Spacer(1, 0.2*inch))
            image_added = True
        except Exception as e:
            print(f"⚠ Error al agregar PNG al PDF: {e}")
            # Continuar sin imagen si falla
    
    # Si no se agregó PNG, intentar convertir SVG
    # NOTA: Preferir usar PNG generado directamente por graphviz (mejor calidad Unicode)
    if not image_added and svg_path and Path(svg_path).exists():
        try:
            svg_abs_path = Path(svg_path).absolute()
            temp_png_path = Path(output_path).absolute().parent / f"{Path(output_path).stem}_temp.png"
            
            with open(svg_abs_path, 'rb') as svg_file:
                svg_data = svg_file.read()
            
            # Convertir SVG a PNG con alta resolución y preservación de Unicode
            # Leer dimensiones del SVG para mantener proporciones
            try:
                import xml.etree.ElementTree as ET
                tree = ET.fromstring(svg_data)
                root = tree
                # Buscar viewBox o width/height
                viewbox = root.get('viewBox', '')
                if viewbox:
                    parts = viewbox.split()
                    svg_width = int(float(parts[2])) if len(parts) > 2 else 1200
                    svg_height = int(float(parts[3])) if len(parts) > 3 else 800
                else:
                    width_attr = root.get('width', '800')
                    height_attr = root.get('height', '600')
                    svg_width = int(float(width_attr.replace('pt', '').replace('px', '').replace('in', '')))
                    svg_height = int(float(height_attr.replace('pt', '').replace('px', '').replace('in', '')))
            except:
                svg_width = 1200
                svg_height = 800
            
            # Convertir con alta resolución (DPI alto) para preservar símbolos Unicode
            cairosvg.svg2png(
                bytestring=svg_data, 
                write_to=str(temp_png_path),
                output_width=svg_width * 2,  # Mayor resolución
                output_height=svg_height * 2,
                dpi=300  # Alta resolución para preservar detalles y símbolos
            )
            
            if temp_png_path.exists() and temp_png_path.stat().st_size > 0:
                from PIL import Image as PILImage
                pil_img = PILImage.open(temp_png_path)
                img_width, img_height = pil_img.size
                
                max_width = 6 * inch
                if img_width > max_width:
                    scale = max_width / img_width
                    img_width = max_width
                    img_height = img_height * scale
                else:
                    img_width = img_width * 0.75
                    img_height = img_height * 0.75
                
                img = Image(str(temp_png_path.absolute()), width=img_width, height=img_height)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
                image_added = True
                temp_png_to_clean = temp_png_path
        except Exception as e:
            pass  # Continuar sin imagen si falla
    
    # Si no se pudo agregar imagen, mostrar mensaje
    if not image_added:
        if svg_path:
            story.append(Paragraph(f"<i>Imagen del árbol no disponible. SVG disponible en: {svg_path}</i>", body_style))
        else:
            story.append(Paragraph("<i>Imagen del árbol no disponible</i>", body_style))
        story.append(Spacer(1, 0.1*inch))
    
    # Árbol con alcance y ligadura (si está disponible)
    if png_scope_path and Path(png_scope_path).exists() and Path(png_scope_path).stat().st_size > 0:
        story.append(PageBreak())
        story.append(Paragraph("<b>Árbol Sintáctico con Alcance y Ligadura:</b>", heading_style))
        story.append(Paragraph(
            "<i>Los nodos coloreados muestran el alcance de cada cuantificador. "
            "Las líneas punteadas conectan cuantificadores con las variables que ligan.</i>", 
            body_style
        ))
        story.append(Spacer(1, 0.1*inch))
        
        try:
            from PIL import Image as PILImage
            pil_img = PILImage.open(png_scope_path)
            img_width, img_height = pil_img.size
            
            # Escalar manteniendo alta resolución
            max_width = 6.5 * inch
            if img_width > max_width:
                scale = max_width / img_width
                img_width = max_width
                img_height = img_height * scale
            else:
                img_width = min(img_width * 0.85, max_width)
                img_height = img_height * 0.85
            
            png_scope_abs = Path(png_scope_path).absolute()
            if png_scope_abs.exists():
                img = Image(str(png_scope_abs), width=img_width, height=img_height)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
        except Exception as e:
            print(f"⚠ Error al agregar PNG con alcance/ligadura al PDF: {e}")
            story.append(Paragraph("<i>Imagen con alcance y ligadura no disponible</i>", body_style))
            story.append(Spacer(1, 0.1*inch))
    
    # JSON
    story.append(Paragraph("<b>Métricas y AST (JSON):</b>", heading_style))
    if json_path and Path(json_path).exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_content = json.load(f)
                json_str = json.dumps(json_content, ensure_ascii=False, indent=2)
                # Truncar si es muy largo (reportlab tiene límites)
                if len(json_str) > 10000:
                    json_str = json_str[:10000] + "\n... (truncado por longitud)"
                story.append(Preformatted(json_str, code_style))
        except Exception as e:
            story.append(Paragraph(f"<i>Error al leer JSON: {e}</i>", body_style))
    
    # Construir PDF - simplemente construir con el story completo
    # Si falla la imagen, ya está manejado arriba (no se agrega al story)
    try:
        doc.build(story)
        # Limpiar archivo temporal PNG DESPUÉS de construir el PDF exitosamente
        if temp_png_to_clean and temp_png_to_clean.exists():
            try:
                temp_png_to_clean.unlink(missing_ok=True)
            except:
                pass
        return output_path
    except Exception as e:
        # Limpiar archivo temporal incluso si falla
        if temp_png_to_clean and temp_png_to_clean.exists():
            try:
                temp_png_to_clean.unlink(missing_ok=True)
            except:
                pass
        print(f"⚠ Error al construir PDF: {e}")
        import traceback
        traceback.print_exc()
        raise


def process_random_samples(num_samples=3, output_dir='outputs', fixed_example_id=None):
    """
    Descarga FOLIO, procesa un ejemplo fijo y luego muestras aleatorias.
    
    Args:
        num_samples: Número de registros aleatorios a procesar
        output_dir: Directorio donde guardar resultados
        fixed_example_id: ID del ejemplo fijo a procesar siempre (default: 329). 
                         Si es None, no se procesa ningún ejemplo fijo.
    """
    print("=" * 80)
    print("Procesamiento de Muestras Aleatorias - Dataset FOLIO")
    print("=" * 80)
    if fixed_example_id is not None:
        print(f"Ejemplo fijo: example_id={fixed_example_id}")
    print(f"Muestras aleatorias: {num_samples}")
    
    # Crear directorio de salida
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Descargar dataset
    print(f"\n1. Descargando dataset FOLIO...")
    try:
        dataset = download_folio_dataset(save_path='datasets/folio_train.json', split='train')
        print(f"✓ Dataset descargado: {len(dataset)} registros")
    except Exception as e:
        print(f"✗ Error al descargar dataset: {e}")
        return
    
    # 2. Buscar ejemplo fijo si se especificó
    fixed_index = None
    if fixed_example_id is not None:
        print(f"\n2. Buscando ejemplo fijo (example_id={fixed_example_id})...")
        for idx, record in enumerate(dataset):
            if record.get('example_id') == fixed_example_id:
                fixed_index = idx
                print(f"✓ Ejemplo fijo encontrado en índice {idx}")
                break
        if fixed_index is None:
            print(f"⚠ Advertencia: No se encontró registro con example_id={fixed_example_id}")
            print(f"  Continuando solo con registros aleatorios...")
    
    # 3. Seleccionar muestras aleatorias
    print(f"\n3. Seleccionando {num_samples} registros aleatorios...")
    if len(dataset) < num_samples:
        print(f"⚠ Advertencia: Solo hay {len(dataset)} registros, usando todos")
        available_indices = list(range(len(dataset)))
    else:
        available_indices = list(range(len(dataset)))
    
    # Excluir el índice fijo de los aleatorios si existe
    if fixed_index is not None and fixed_index in available_indices:
        available_indices.remove(fixed_index)
    
    if len(available_indices) < num_samples:
        print(f"⚠ Advertencia: Solo hay {len(available_indices)} registros disponibles (excluyendo fijo), usando todos")
        selected_indices = available_indices
    else:
        selected_indices = random.sample(available_indices, num_samples)
    
    print(f"✓ Registros aleatorios seleccionados: {selected_indices}")
    
    # 4. Procesar cada registro (primero el fijo, luego los aleatorios)
    print(f"\n4. Procesando registros...")
    results = []
    
    # Procesar ejemplo fijo primero si existe
    indices_to_process = []
    if fixed_index is not None:
        indices_to_process.append(fixed_index)
        print(f"\n{'='*60}")
        print(f"PROCESANDO EJEMPLO FIJO (example_id={fixed_example_id})")
        print(f"{'='*60}")
    indices_to_process.extend(selected_indices)
    
    for idx in indices_to_process:
        record = dataset[idx]
        # Obtener ID del registro (puede ser 'example_id' o 'story_id')
        record_id = record.get('example_id') or record.get('story_id') or record.get('id', f'record_{idx}')
        
        is_fixed = (idx == fixed_index) if fixed_index is not None else False
        prefix = "[FIJO] " if is_fixed else ""
        print(f"\n{'='*60}")
        print(f"{prefix}Procesando registro {idx} (ID: {record_id})")
        print(f"{'='*60}")
        
        try:
            # Obtener premisas y conclusión en formato FOL
            # El dataset tiene 'premises-FOL' y 'conclusion-FOL' para las fórmulas FOL
            premises_fol = record.get('premises-FOL', [])
            conclusion_fol = record.get('conclusion-FOL', '')
            
            # Si no están en formato FOL, intentar con las columnas normales
            if not premises_fol:
                premises_fol = record.get('premises', [])
            if not conclusion_fol:
                conclusion_fol = record.get('conclusion', '')
            
            # Convertir a lista si es string
            # Las premisas FOL pueden venir como string separado por líneas
            if isinstance(premises_fol, str):
                # Dividir por líneas y limpiar
                premises_fol = [p.strip() for p in premises_fol.split('\n') if p.strip()]
            elif not isinstance(premises_fol, list):
                premises_fol = list(premises_fol) if premises_fol else []
            
            if not premises_fol or not conclusion_fol:
                print(f"⚠ Registro {idx} sin premisas o conclusión FOL, saltando...")
                print(f"   Keys disponibles: {list(record.keys())}")
                continue
            
            premises = premises_fol
            conclusion = conclusion_fol
            
            print(f"Premisas: {len(premises)}")
            print(f"Conclusión: {conclusion[:50]}...")
            
            # Parsear condicional global
            print("Parseando fórmula...")
            try:
                ast = parse_global_conditional(premises, conclusion)
                print(f"✓ AST creado: {ast.node_type}")
            except ValueError as e:
                # Error de parsing - mostrar información y continuar con siguiente registro
                print(f"✗ Error al parsear: {e}")
                print(f"  Premisas problemáticas:")
                for i, p in enumerate(premises, 1):
                    print(f"    {i}. {p[:100]}...")
                print(f"  Conclusión: {conclusion[:100]}...")
                print(f"  ⚠ Saltando este registro debido a error de parsing")
                continue
            
            # Calcular métricas
            print("Calculando métricas...")
            metrics = calculate_all_metrics(ast)
            print(f"✓ Métricas calculadas")
            print(f"  - Profundidad: {metrics['total_depth']}")
            print(f"  - Subfórmulas: {metrics['num_subformulas']}")
            print(f"  - Cuantificadores: {metrics['num_quantifiers']}")
            
            # Construir fórmula original
            formula = build_global_conditional(premises, conclusion)
            
            # Crear directorio específico para este registro
            record_output_dir = Path(output_dir) / 'random_test' / str(record_id)
            record_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Exportar JSON y SVG
            print("Exportando JSON y SVG...")
            base_name = f"registro_{record_id}"
            files = export_complete_analysis(
                ast,
                original_formula=formula,
                output_dir=str(record_output_dir),
                base_name=base_name
            )
            
            json_path = files.get('json')
            svg_path = files.get('svg')
            png_path = files.get('png')
            png_scope_path = files.get('png_scope')
            
            # Asegurar que las rutas sean absolutas o relativas al directorio del registro
            if json_path:
                json_path = str(record_output_dir / Path(json_path).name)
            if svg_path:
                svg_path = str(record_output_dir / Path(svg_path).name)
            if png_path:
                png_path = str(record_output_dir / Path(png_path).name)
            if png_scope_path:
                png_scope_path = str(record_output_dir / Path(png_scope_path).name)
            
            print(f"✓ JSON: {json_path}")
            if svg_path:
                print(f"✓ SVG: {svg_path}")
            if png_path:
                print(f"✓ PNG: {png_path}")
            else:
                print(f"⚠ PNG no disponible en files: {list(files.keys())}")
            if png_scope_path:
                print(f"✓ PNG con alcance/ligadura: {png_scope_path}")
            
            # Obtener textos originales (no FOL) del registro
            premises_text_raw = record.get('premises', '')
            conclusion_text = record.get('conclusion', '')
            
            # Procesar premises_text: siempre convertir a lista si es string multilínea
            if isinstance(premises_text_raw, str):
                # Dividir por líneas si hay múltiples premisas
                premises_text_list = [p.strip() for p in premises_text_raw.split('\n') if p.strip()]
                if len(premises_text_list) > 1:
                    premises_text = premises_text_list
                else:
                    premises_text = premises_text_raw  # Mantener como string si es una sola línea
            else:
                premises_text = premises_text_raw
            
            # Crear PDF en el directorio del registro
            pdf_path = record_output_dir / f"{record_id}.pdf"
            pdf_result = None
            try:
                print("Generando PDF...")
                pdf_result = create_pdf_report(
                    record_id=record_id,
                    premises_text=premises_text,
                    conclusion_text=conclusion_text,
                    premises_fol=premises,
                    conclusion_fol=conclusion,
                    svg_path=svg_path,
                    json_path=json_path,
                    output_path=pdf_path,
                    png_path=png_path,
                    png_scope_path=png_scope_path
                )
                
                if pdf_result:
                    print(f"✓ PDF generado: {pdf_path}")
                else:
                    print(f"⚠ No se pudo generar PDF (verificar dependencias)")
            except Exception as pdf_error:
                print(f"⚠ Error al generar PDF: {pdf_error}")
                import traceback
                print(f"  Detalles: {traceback.format_exc()}")
                pdf_result = None
            
            # Agregar resultado aunque el PDF haya fallado
            results.append({
                'record_id': record_id,
                'index': idx,
                'is_fixed': is_fixed,
                'json': json_path,
                'svg': svg_path,
                'pdf': str(pdf_path) if pdf_result else None
            })
            
        except Exception as e:
            print(f"✗ Error procesando registro {idx}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Resumen
    print(f"\n{'='*80}")
    print("Resumen")
    print(f"{'='*80}")
    total_expected = num_samples + (1 if fixed_index is not None else 0)
    fixed_count = len([r for r in results if r.get('is_fixed', False)])
    random_count = len([r for r in results if not r.get('is_fixed', False)])
    print(f"Registros procesados: {len(results)}/{total_expected}")
    if fixed_index is not None:
        print(f"  - Ejemplo fijo: {fixed_count}/1")
    print(f"  - Aleatorios: {random_count}/{num_samples}")
    print(f"\nArchivos generados:")
    for result in results:
        print(f"\n  Registro {result['record_id']}:")
        print(f"    - JSON: {result['json']}")
        if result['svg']:
            print(f"    - SVG: {result['svg']}")
        if result['pdf']:
            print(f"    - PDF: {result['pdf']}")
    
    return results


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Procesar muestras aleatorias de FOLIO')
    parser.add_argument('--num-samples', type=int, default=3,
                       help='Número de registros aleatorios a procesar (default: 3)')
    parser.add_argument('--output-dir', type=str, default='outputs',
                       help='Directorio de salida (default: outputs)')
    parser.add_argument('--fixed-example-id', type=int, default=329,
                       help='ID del ejemplo fijo a procesar siempre (default: 329). Usar 0 o negativo para desactivar')
    parser.add_argument('--seed', type=int, default=None,
                       help='Seed para reproducibilidad (opcional)')
    
    args = parser.parse_args()
    
    # Configurar seed si se proporciona
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Seed configurado: {args.seed}")
    
    # Procesar fixed_example_id: si es 0 o negativo, no procesar ejemplo fijo
    fixed_id = args.fixed_example_id if args.fixed_example_id > 0 else None
    
    process_random_samples(
        num_samples=args.num_samples,
        output_dir=args.output_dir,
        fixed_example_id=fixed_id
    )

