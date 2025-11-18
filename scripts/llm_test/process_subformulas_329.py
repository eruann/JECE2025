"""
Script para procesar TODAS las subfórmulas del ejemplo 329 y generar PDF con alineación LLM.

Orden en PDF:
1. Forma natural
2. Forma FOL
3. Imagen del árbol
4. Análisis de LLM (subfórmula FOL, subfórmula en texto, razonamiento)
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Agregar src/ al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

from download_folio import download_folio_dataset
from build_conditionals import parse_global_conditional
from subformula_alignment import (
    extract_all_subformulas,
    align_subformula,
    FREE_MODELS
)
from serialize import export_complete_analysis


def create_pdf_with_subformula_analysis(record_id, 
                                        premises_text, 
                                        conclusion_text,
                                        premises_fol,
                                        conclusion_fol,
                                        svg_path,
                                        json_path,
                                        subformula_results,
                                        output_path,
                                        png_path=None):
    """
    Crea un PDF con análisis completo incluyendo alineación de subfórmulas.
    
    Orden:
    1. Forma natural
    2. Forma FOL
    3. Imagen del árbol
    4. Análisis de LLM por subfórmula
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Preformatted, PageBreak, KeepTogether
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
        from reportlab.lib.colors import HexColor
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
    subheading_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading3'],
        fontSize=10,
        textColor='#555555',
        spaceAfter=4,
        spaceBefore=8
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
    fol_style = ParagraphStyle(
        'FOLStyle',
        parent=body_style,
        fontSize=9,
        fontName='Courier',
        textColor='#006600',
        leftIndent=10,
        rightIndent=10,
        backColor='#F0F0F0'
    )
    explanation_style = ParagraphStyle(
        'ExplanationStyle',
        parent=body_style,
        fontSize=9,
        leftIndent=15,
        rightIndent=15,
        textColor='#444444',
        alignment=TA_JUSTIFY
    )
    
    # Contenido del PDF
    story = []
    
    # Título
    story.append(Paragraph(f"Análisis FOL con Alineación de Subfórmulas - Registro ID: {record_id}", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Información del registro
    story.append(Paragraph("<b>Información del Registro</b>", heading_style))
    story.append(Paragraph(f"<b>ID del ejemplo:</b> {record_id}", body_style))
    story.append(Paragraph(f"<b>Fecha de procesamiento:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # ========== 1. FORMA NATURAL ==========
    story.append(Paragraph("<b>1. Forma Natural</b>", heading_style))
    
    # Premisas en texto natural
    story.append(Paragraph("<b>Premisas:</b>", subheading_style))
    if isinstance(premises_text, list):
        for i, premise in enumerate(premises_text, 1):
            story.append(Paragraph(f"<b>{i}.</b> {premise}", body_style))
    else:
        story.append(Paragraph(str(premises_text), body_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Conclusión en texto natural
    story.append(Paragraph("<b>Conclusión:</b>", subheading_style))
    story.append(Paragraph(str(conclusion_text), body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # ========== 2. FORMA FOL ==========
    story.append(Paragraph("<b>2. Forma FOL</b>", heading_style))
    
    # Premisas FOL
    story.append(Paragraph("<b>Premisas FOL:</b>", subheading_style))
    if isinstance(premises_fol, list):
        for i, premise in enumerate(premises_fol, 1):
            story.append(Paragraph(f"<b>{i}.</b> <font face='Courier' color='#006600'>{premise}</font>", body_style))
    else:
        story.append(Paragraph(f"<font face='Courier' color='#006600'>{premises_fol}</font>", body_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Conclusión FOL
    story.append(Paragraph("<b>Conclusión FOL:</b>", subheading_style))
    story.append(Paragraph(f"<font face='Courier' color='#006600'>{conclusion_fol}</font>", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # ========== 3. IMAGEN DEL ÁRBOL ==========
    story.append(Paragraph("<b>3. Árbol Sintáctico (AST)</b>", heading_style))
    
    image_added = False
    temp_png_to_clean = None
    
    # Priorizar PNG si está disponible
    if png_path and Path(png_path).exists() and Path(png_path).stat().st_size > 0:
        try:
            from PIL import Image as PILImage
            pil_img = PILImage.open(png_path)
            img_width, img_height = pil_img.size
            
            max_width = 6.5 * inch
            if img_width > max_width:
                scale = max_width / img_width
                img_width = max_width
                img_height = img_height * scale
            else:
                img_width = min(img_width * 0.85, max_width)
                img_height = img_height * 0.85
            
            png_abs = Path(png_path).absolute()
            if png_abs.exists():
                img = Image(str(png_abs), width=img_width, height=img_height)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
                image_added = True
        except Exception as e:
            print(f"⚠ Error al agregar PNG: {e}")
    
    # Si no se agregó PNG, intentar convertir SVG
    if not image_added and svg_path and Path(svg_path).exists():
        try:
            svg_abs_path = Path(svg_path).absolute()
            temp_png_path = Path(output_path).absolute().parent / f"{Path(output_path).stem}_temp.png"
            
            with open(svg_abs_path, 'rb') as svg_file:
                svg_data = svg_file.read()
            
            try:
                import xml.etree.ElementTree as ET
                tree = ET.fromstring(svg_data)
                root = tree
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
            
            cairosvg.svg2png(
                bytestring=svg_data,
                write_to=str(temp_png_path),
                output_width=svg_width * 2,
                output_height=svg_height * 2,
                dpi=300
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
            pass
    
    if not image_added:
        story.append(Paragraph("<i>Imagen del árbol no disponible</i>", body_style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # ========== 4. ANÁLISIS DE LLM POR SUBFÓRMULA ==========
    story.append(Paragraph("<b>4. Análisis de Alineación LLM por Subfórmula</b>", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Información sobre el análisis
    total_subformulas = len(subformula_results)
    successful = sum(1 for r in subformula_results if 'error' not in r.get('alignment', {}))
    story.append(Paragraph(f"<i>Total de subfórmulas analizadas: {total_subformulas} | Exitosas: {successful}</i>", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Procesar cada subfórmula
    for idx, result in enumerate(subformula_results, 1):
        subformula_fol = result.get('subformula_fol', '')
        node_type = result.get('node_type', 'UNKNOWN')
        alignment = result.get('alignment', {})
        
        # Encabezado de subfórmula
        story.append(Paragraph(f"<b>Subfórmula {idx}/{total_subformulas}</b>", subheading_style))
        story.append(Paragraph(f"<i>Tipo: {node_type}</i>", body_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Subfórmula FOL
        story.append(Paragraph("<b>Subfórmula FOL:</b>", body_style))
        # Truncar si es muy larga
        fol_display = subformula_fol[:200] + "..." if len(subformula_fol) > 200 else subformula_fol
        story.append(Paragraph(f"<font face='Courier' color='#006600'>{fol_display}</font>", body_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Subfórmula en texto natural (span encontrado)
        story.append(Paragraph("<b>Subfórmula en Texto Natural:</b>", body_style))
        if 'error' in alignment:
            story.append(Paragraph(f"<font color='#CC0000'>Error: {alignment.get('error', 'Desconocido')}</font>", body_style))
        elif alignment.get('span') and alignment.get('span') != 'NO_ENCONTRADO':
            span = alignment.get('span', '')
            location = alignment.get('location', 'desconocida')
            confidence = alignment.get('confidence', 0)
            
            story.append(Paragraph(f"<b>Span encontrado:</b> \"{span}\"", body_style))
            story.append(Paragraph(f"<b>Ubicación:</b> {location}", body_style))
            story.append(Paragraph(f"<b>Confianza:</b> {confidence:.2f}", body_style))
        else:
            story.append(Paragraph("<font color='#CC6600'>NO_ENCONTRADO</font>", body_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Razonamiento de la LLM
        if 'explanation' in alignment and alignment['explanation']:
            story.append(Paragraph("<b>Razonamiento de la LLM:</b>", body_style))
            explanation = alignment['explanation']
            story.append(Paragraph(explanation, explanation_style))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Separador visual cada 5 subfórmulas
        if idx % 5 == 0 and idx < total_subformulas:
            story.append(Paragraph("<i>---</i>", body_style))
            story.append(Spacer(1, 0.1*inch))
    
    # Construir PDF
    try:
        doc.build(story)
        if temp_png_to_clean and temp_png_to_clean.exists():
            try:
                temp_png_to_clean.unlink(missing_ok=True)
            except:
                pass
        return output_path
    except Exception as e:
        if temp_png_to_clean and temp_png_to_clean.exists():
            try:
                temp_png_to_clean.unlink(missing_ok=True)
            except:
                pass
        print(f"⚠ Error al construir PDF: {e}")
        import traceback
        traceback.print_exc()
        raise


def process_all_subformulas_329(provider: str = "openrouter",
                                  model: str = None,
                                  reasoning_effort: str = "medium"):
    """
    Procesa TODAS las subfórmulas del ejemplo 329 y genera PDF completo.
    
    Args:
        provider: Proveedor de LLM ("openrouter" o "openai")
        model: Modelo específico (opcional)
        reasoning_effort: Nivel de esfuerzo de reasoning ("medium" o "high", default: "medium")
    """
    print("=" * 80)
    print("PROCESAMIENTO COMPLETO DE SUBFÓRMULAS - Ejemplo 329")
    print("=" * 80)
    print(f"Proveedor: {provider}")
    if model:
        model_lower = model.lower()
        if model_lower in FREE_MODELS:
            print(f"Modelo: {model} (GRATIS ✅)")
        else:
            print(f"Modelo: {model}")
    else:
        print(f"Modelo: default")
    print(f"Reasoning effort: {reasoning_effort}")
    
    # 1. Cargar dataset
    print("\n1. Cargando dataset FOLIO...")
    try:
        dataset = download_folio_dataset(split='train')
    except Exception as e:
        print(f"❌ Error al cargar dataset: {e}")
        return
    
    # 2. Encontrar ejemplo 329
    record_329 = None
    for record in dataset:
        if record.get('example_id') == 329:
            record_329 = record
            break
    
    if not record_329:
        print("❌ No se encontró el ejemplo 329")
        return
    
    print("✓ Ejemplo 329 encontrado")
    
    # 3. Extraer datos
    premises_fol = record_329.get('premises-FOL', record_329.get('premises', []))
    conclusion_fol = record_329.get('conclusion-FOL', record_329.get('conclusion', ''))
    
    premises_natural = record_329.get('premises', [])
    conclusion_natural = record_329.get('conclusion', '')
    
    # Normalizar formatos
    if isinstance(premises_natural, str):
        premises_natural = [p.strip() for p in premises_natural.split('\n') if p.strip()]
    if isinstance(premises_fol, str):
        premises_fol = [p.strip() for p in premises_fol.split('\n') if p.strip()]
    if not isinstance(premises_natural, list):
        premises_natural = [premises_natural] if premises_natural else []
    if not isinstance(premises_fol, list):
        premises_fol = [premises_fol] if premises_fol else []
    
    # 4. Parsear AST
    print("\n2. Parseando fórmulas FOL...")
    try:
        ast = parse_global_conditional(premises_fol, conclusion_fol)
        print("✓ AST parseado correctamente")
    except Exception as e:
        print(f"❌ Error al parsear: {e}")
        return
    
    # 5. Extraer TODAS las subfórmulas
    print("\n3. Extrayendo TODAS las subfórmulas del AST...")
    subformulas = extract_all_subformulas(ast)
    print(f"✓ Encontradas {len(subformulas)} subfórmulas")
    
    # 6. Generar archivos de análisis (SVG, JSON, PNG)
    print("\n4. Generando archivos de análisis (SVG, JSON)...")
    output_dir = project_root / 'outputs' / 'random_test' / '329'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    record_id = record_329.get('example_id') or record_329.get('story_id') or '329'
    
    # Construir fórmula original completa
    from build_conditionals import build_global_conditional
    original_formula = build_global_conditional(premises_fol, conclusion_fol)
    
    try:
        files = export_complete_analysis(
            ast=ast,
            original_formula=original_formula,
            output_dir=str(output_dir),
            base_name=f'registro_{record_id}_complete'
        )
        json_path = files.get('json')
        svg_path = files.get('svg')
        png_path = files.get('png')  # PNG puede estar disponible
        print(f"✓ Archivos generados: {json_path}, {svg_path}")
        if png_path:
            print(f"✓ PNG generado: {png_path}")
    except Exception as e:
        print(f"⚠ Error al generar archivos: {e}")
        import traceback
        traceback.print_exc()
        svg_path = None
        json_path = None
        png_path = None
    
    # Si PNG no está disponible, buscar alternativo
    if not png_path:
        png_path_alt = output_dir / f'registro_{record_id}_complete.png'
        if png_path_alt.exists():
            png_path = str(png_path_alt)
        else:
            png_path = None
    
    # 7. Verificar API key
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    if provider == "openrouter":
        api_key = os.getenv('OPENROUTER_API_KEY')
    elif provider == "openai":
        api_key = os.getenv('OPENAI_API_KEY')
    else:
        api_key = None
    
    if not api_key:
        print(f"\n⚠ Advertencia: {provider.upper()}_API_KEY no encontrada")
        print("   El PDF se generará sin análisis de LLM")
        subformula_results = []
    else:
        print("\n5. Procesando alineación con LLM para TODAS las subfórmulas...")
        print(f"   Esto puede tomar varios minutos ({len(subformulas)} subfórmulas)...")
        
        subformula_results = []
        for i, (fol_str, node, meta) in enumerate(subformulas, 1):
            print(f"   [{i}/{len(subformulas)}] Procesando subfórmula tipo {meta['node_type']}...", end=' ')
            
            try:
                alignment = align_subformula(
                    fol_str,
                    premises_natural,
                    conclusion_natural,
                    provider=provider,
                    model=model,
                    reasoning_effort=reasoning_effort
                )
                
                subformula_results.append({
                    'subformula_fol': fol_str,
                    'node_type': meta['node_type'],
                    'metadata': meta,
                    'alignment': alignment
                })
                
                if 'error' in alignment:
                    print(f"❌ Error")
                else:
                    span = alignment.get('span', 'N/A')
                    if span == 'NO_ENCONTRADO':
                        print(f"⚠ No encontrado")
                    else:
                        print(f"✓ Encontrado")
            
            except Exception as e:
                print(f"❌ Excepción: {e}")
                subformula_results.append({
                    'subformula_fol': fol_str,
                    'node_type': meta['node_type'],
                    'metadata': meta,
                    'alignment': {'error': str(e)}
                })
    
    # 8. Guardar resultados JSON
    print("\n6. Guardando resultados JSON...")
    json_output_file = output_dir / 'subformula_alignment_complete.json'
    output_data = {
        'example_id': 329,
        'provider': provider,
        'model': model or 'default',
        'premises_natural': premises_natural,
        'conclusion_natural': conclusion_natural,
        'premises_fol': premises_fol,
        'conclusion_fol': conclusion_fol,
        'total_subformulas': len(subformulas),
        'results': subformula_results
    }
    
    with open(json_output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Resultados guardados en: {json_output_file}")
    
    # 9. Generar PDF
    print("\n7. Generando PDF con análisis completo...")
    pdf_path = output_dir / f'registro_{record_id}_subformulas_complete.pdf'
    
    try:
        create_pdf_with_subformula_analysis(
            record_id=record_id,
            premises_text=premises_natural,
            conclusion_text=conclusion_natural,
            premises_fol=premises_fol,
            conclusion_fol=conclusion_fol,
            svg_path=str(svg_path) if svg_path else None,
            json_path=str(json_path) if json_path else None,
            subformula_results=subformula_results,
            output_path=str(pdf_path),
            png_path=str(png_path) if png_path else None
        )
        print(f"✓ PDF generado: {pdf_path}")
    except Exception as e:
        print(f"❌ Error al generar PDF: {e}")
        import traceback
        traceback.print_exc()
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print(f"Total de subfórmulas procesadas: {len(subformulas)}")
    if subformula_results:
        successful = sum(1 for r in subformula_results if 'error' not in r.get('alignment', {}))
        found = sum(1 for r in subformula_results 
                   if 'error' not in r.get('alignment', {}) 
                   and r.get('alignment', {}).get('span') != 'NO_ENCONTRADO')
        print(f"✓ Exitosas: {successful}")
        print(f"✓ Con span encontrado: {found}")
        print(f"❌ Fallidas: {len(subformula_results) - successful}")
        
        if found > 0:
            avg_confidence = sum(
                r.get('alignment', {}).get('confidence', 0)
                for r in subformula_results
                if 'error' not in r.get('alignment', {})
                and r.get('alignment', {}).get('span') != 'NO_ENCONTRADO'
            ) / found
            print(f"Confianza promedio: {avg_confidence:.2f}")
    
    print(f"\nArchivos generados:")
    print(f"  - PDF: {pdf_path}")
    print(f"  - JSON: {json_output_file}")
    if svg_path:
        print(f"  - SVG: {svg_path}")
    print("=" * 80)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Procesar TODAS las subfórmulas del ejemplo 329')
    parser.add_argument('--provider', choices=['openai', 'openrouter'], default='openrouter',
                       help='Proveedor de LLM (default: openrouter)')
    parser.add_argument('--model', type=str, default=None,
                       help='Modelo específico (ej: "deepseek-r1", "glm-4.5-air", "kimi-vl-a3b-thinking", "openai/gpt-4o-mini")')
    parser.add_argument('--reasoning-effort', choices=['medium', 'high'], default='medium',
                       help='Nivel de esfuerzo de reasoning (default: medium). Solo aplica a modelos con reasoning.')
    
    args = parser.parse_args()
    
    process_all_subformulas_329(
        provider=args.provider,
        model=args.model,
        reasoning_effort=args.reasoning_effort
    )

