"""
Módulo para alinear subfórmulas FOL con texto natural usando LLMs.

Soporta OpenAI y OpenRouter APIs.
"""

import json
import os
import re
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

try:
    from .fol_parser import FOLASTNode
except ImportError:
    from fol_parser import FOLASTNode


def ast_node_to_fol_string(node: FOLASTNode) -> str:
    """
    Convierte un nodo AST a su representación FOL string.
    
    Args:
        node: Nodo del AST
        
    Returns:
        String con la fórmula FOL
    """
    if node.node_type == "PREDICATE":
        if node.children:
            terms = ", ".join([
                child.value if isinstance(child, FOLASTNode) and hasattr(child, 'value') 
                else str(child.value) if hasattr(child, 'value') else str(child)
                for child in node.children
            ])
            return f"{node.value}({terms})"
        return str(node.value)
    
    elif node.node_type == "ATOM":
        return str(node.value)
    
    elif node.node_type == "TERM":
        return str(node.value)
    
    elif node.node_type == "NOT":
        if not node.children:
            return "¬"
        child_str = ast_node_to_fol_string(node.children[0])
        # Evitar doble negación visual
        if child_str.startswith("¬"):
            return f"¬({child_str})"
        return f"¬{child_str}"
    
    elif node.node_type == "AND":
        if len(node.children) == 0:
            return ""
        if len(node.children) == 1:
            return ast_node_to_fol_string(node.children[0])
        parts = [ast_node_to_fol_string(child) for child in node.children]
        # Agregar paréntesis solo si es necesario
        return " ∧ ".join(f"({p})" if any(op in p for op in ['→', '↔', '∨', '⊕']) else p for p in parts)
    
    elif node.node_type == "OR":
        if len(node.children) == 0:
            return ""
        if len(node.children) == 1:
            return ast_node_to_fol_string(node.children[0])
        parts = [ast_node_to_fol_string(child) for child in node.children]
        return " ∨ ".join(f"({p})" if any(op in p for op in ['→', '↔']) else p for p in parts)
    
    elif node.node_type == "XOR":
        if len(node.children) == 0:
            return ""
        if len(node.children) == 1:
            return ast_node_to_fol_string(node.children[0])
        parts = [ast_node_to_fol_string(child) for child in node.children]
        return " ⊕ ".join(f"({p})" if any(op in p for op in ['→', '↔', '∨', '∧']) else p for p in parts)
    
    elif node.node_type == "IMPLIES":
        if len(node.children) != 2:
            return str(node)
        left = ast_node_to_fol_string(node.children[0])
        right = ast_node_to_fol_string(node.children[1])
        return f"({left}) → ({right})"
    
    elif node.node_type == "BICOND":
        if len(node.children) != 2:
            return str(node)
        left = ast_node_to_fol_string(node.children[0])
        right = ast_node_to_fol_string(node.children[1])
        return f"({left}) ↔ ({right})"
    
    elif node.node_type == "FORALL":
        var = node.value if node.value else "x"
        if not node.children:
            return f"∀{var}"
        scope = ast_node_to_fol_string(node.children[0])
        return f"∀{var} ({scope})"
    
    elif node.node_type == "EXISTS":
        var = node.value if node.value else "x"
        if not node.children:
            return f"∃{var}"
        scope = ast_node_to_fol_string(node.children[0])
        return f"∃{var} ({scope})"
    
    elif node.node_type == "EQUALS":
        if len(node.children) == 2:
            left = ast_node_to_fol_string(node.children[0])
            right = ast_node_to_fol_string(node.children[1])
            return f"{left} = {right}"
        return str(node)
    
    elif node.node_type == "TERM_LIST":
        if node.children:
            return ", ".join([ast_node_to_fol_string(child) for child in node.children])
        return ""
    
    # Fallback
    return str(node)


def extract_all_subformulas(ast: FOLASTNode) -> List[Tuple[str, FOLASTNode, Dict]]:
    """
    Extrae todas las subfórmulas del AST con su representación FOL.
    
    Args:
        ast: Nodo raíz del AST
        
    Returns:
        Lista de tuplas (formula_fol_string, ast_node, metadata)
    """
    subformulas = []
    
    def traverse(node: FOLASTNode, depth: int = 0):
        # Tipos que representan subfórmulas (no solo términos)
        formula_types = {
            'AND', 'OR', 'XOR', 'IMPLIES', 'BICOND', 'NOT',
            'FORALL', 'EXISTS', 'PREDICATE', 'ATOM', 'EQUALS'
        }
        
        if node.node_type in formula_types:
            try:
                formula_str = ast_node_to_fol_string(node)
                metadata = {
                    'node_type': node.node_type,
                    'depth': depth,
                    'num_children': len(node.children),
                    'has_value': node.value is not None
                }
                subformulas.append((formula_str, node, metadata))
            except Exception as e:
                # Si falla la conversión, aún así incluir el nodo
                metadata = {
                    'node_type': node.node_type,
                    'depth': depth,
                    'num_children': len(node.children),
                    'conversion_error': str(e)
                }
                subformulas.append((str(node), node, metadata))
        
        for child in node.children:
            if isinstance(child, FOLASTNode):
                traverse(child, depth + 1)
    
    traverse(ast)
    return subformulas


def align_subformula_with_openai(subformula_fol: str,
                                  natural_premises: List[str],
                                  natural_conclusion: str,
                                  model: str = "gpt-4o-mini") -> Dict:
    """
    Usa OpenAI API para encontrar el span correspondiente en texto natural.
    
    Args:
        subformula_fol: Subfórmula FOL a alinear
        natural_premises: Lista de premisas en texto natural
        natural_conclusion: Conclusión en texto natural
        model: Modelo a usar (gpt-4o-mini, gpt-4, etc.)
    
    Returns:
        Dict con información de alineación
    """
    try:
        from openai import OpenAI
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {
                "error": "OPENAI_API_KEY no configurada en .env",
                "span": None,
                "location": "ERROR",
                "confidence": 0.0
            }
        
        client = OpenAI(api_key=api_key)
        
        # Construir contexto
        context_parts = []
        for i, premise in enumerate(natural_premises):
            context_parts.append(f"Premisa {i+1}: {premise}")
        context_parts.append(f"Conclusión: {natural_conclusion}")
        context = "\n".join(context_parts)
        
        # Prompt optimizado
        prompt = f"""Eres un experto en lógica formal y lenguaje natural. Tu tarea es encontrar qué segmento del texto natural corresponde a una subfórmula FOL específica.

TEXTO NATURAL:
{context}

SUBFÓRMULA FOL A IDENTIFICAR:
{subformula_fol}

INSTRUCCIONES:
1. Identifica el segmento exacto del texto natural que expresa el mismo significado que la subfórmula FOL
2. El segmento puede estar en una premisa o en la conclusión
3. Si la subfórmula es parte de una premisa/conclusión más grande, identifica solo la parte relevante
4. Si no encuentras correspondencia clara, indica "NO_ENCONTRADO"

Responde SOLO en formato JSON válido (sin texto adicional):
{{
    "span": "segmento exacto del texto natural",
    "location": "premise_1" | "premise_2" | ... | "conclusion" | "NO_ENCONTRADO",
    "premise_index": 0,
    "confidence": 0.95,
    "explanation": "breve explicación de por qué este segmento corresponde"
}}
"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un experto en mapear fórmulas lógicas a lenguaje natural. Responde solo en JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except ImportError:
        return {
            "error": "openai package no instalado. Instala con: pip install openai",
            "span": None,
            "location": "ERROR",
            "confidence": 0.0
        }
    except Exception as e:
        return {
            "error": str(e),
            "span": None,
            "location": "ERROR",
            "confidence": 0.0
        }


def align_subformula_with_openrouter(subformula_fol: str,
                                       natural_premises: List[str],
                                       natural_conclusion: str,
                                       model: str = "openai/gpt-4o-mini",
                                       reasoning_effort: str = "medium") -> Dict:
    """
    Usa OpenRouter API para encontrar el span correspondiente en texto natural.
    
    Args:
        subformula_fol: Subfórmula FOL a alinear
        natural_premises: Lista de premisas en texto natural
        natural_conclusion: Conclusión en texto natural
        model: Modelo a usar (formato: "provider/model", ej: "openai/gpt-4o-mini", "anthropic/claude-3-haiku")
        reasoning_effort: Nivel de esfuerzo de reasoning ("medium" o "high", default: "medium")
    
    Returns:
        Dict con información de alineación
    """
    try:
        import requests
        
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            return {
                "error": "OPENROUTER_API_KEY no configurada en .env",
                "span": None,
                "location": "ERROR",
                "confidence": 0.0
            }
        
        # Construir contexto
        context_parts = []
        for i, premise in enumerate(natural_premises):
            context_parts.append(f"Premisa {i+1}: {premise}")
        context_parts.append(f"Conclusión: {natural_conclusion}")
        context = "\n".join(context_parts)
        
        # Prompt
        prompt = f"""Eres un experto en lógica formal y lenguaje natural. Tu tarea es encontrar qué segmento del texto natural corresponde a una subfórmula FOL específica.

TEXTO NATURAL:
{context}

SUBFÓRMULA FOL A IDENTIFICAR:
{subformula_fol}

INSTRUCCIONES:
1. Identifica el segmento exacto del texto natural que expresa el mismo significado que la subfórmula FOL
2. El segmento puede estar en una premisa o en la conclusión
3. Si la subfórmula es parte de una premisa/conclusión más grande, identifica solo la parte relevante
4. Si no encuentras correspondencia clara, indica "NO_ENCONTRADO"

Responde SOLO en formato JSON válido (sin texto adicional):
{{
    "span": "segmento exacto del texto natural",
    "location": "premise_1" | "premise_2" | ... | "conclusion" | "NO_ENCONTRADO",
    "premise_index": 0,
    "confidence": 0.95,
    "explanation": "breve explicación de por qué este segmento corresponde"
}}
"""
        
        # Construir payload base
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Eres un experto en mapear fórmulas lógicas a lenguaje natural. Responde solo en JSON válido."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        
        # Agregar reasoning para modelos que lo soportan
        # Modelos con reasoning: deepseek-r1, glm-4.5-air, kimi-vl-a3b-thinking
        reasoning_models = ["deepseek-r1", "glm-4.5-air", "kimi-vl-a3b-thinking"]
        if any(r_model in model.lower() for r_model in reasoning_models):
            # Validar effort
            if reasoning_effort not in ["medium", "high"]:
                reasoning_effort = "medium"  # Default a medium si no es válido
            payload["reasoning"] = {
                "enabled": True,
                "effort": reasoning_effort
            }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://github.com/your-repo",  # Opcional
                "X-Title": "FOL Subformula Alignment"  # Opcional
            },
            json=payload
        )
        
        response.raise_for_status()
        result = response.json()
        
        content = result['choices'][0]['message']['content']
        
        # Intentar parsear JSON
        try:
            alignment_result = json.loads(content)
            return alignment_result
        except json.JSONDecodeError:
            # Si no es JSON válido, intentar extraer JSON del texto
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "error": "No se pudo parsear respuesta JSON",
                    "raw_response": content,
                    "span": None,
                    "location": "ERROR",
                    "confidence": 0.0
                }
        
    except ImportError:
        return {
            "error": "requests package no instalado. Instala con: pip install requests",
            "span": None,
            "location": "ERROR",
            "confidence": 0.0
        }
    except Exception as e:
        return {
            "error": str(e),
            "span": None,
            "location": "ERROR",
            "confidence": 0.0
        }


# Modelos gratuitos disponibles en OpenRouter
FREE_MODELS = {
    "deepseek-r1": "deepseek/deepseek-r1",
    "qwen": "qwen/qwen-2.5-72b-instruct",  # Verificar modelo exacto en OpenRouter
    "qwen-free": "qwen/qwen-2.5-7b-instruct",  # Versión más pequeña
    "deepseek-chat": "deepseek/deepseek-chat",
    "glm-4.5-air": "z-ai/glm-4.5-air:free",
    "kimi-vl-a3b-thinking": "moonshotai/kimi-vl-a3b-thinking:free",
}


def align_subformula(subformula_fol: str,
                     natural_premises: List[str],
                     natural_conclusion: str,
                     provider: str = "openrouter",
                     model: Optional[str] = None,
                     reasoning_effort: str = "medium") -> Dict:
    """
    Función unificada para alinear subfórmulas usando diferentes proveedores.
    
    Args:
        subformula_fol: Subfórmula FOL a alinear
        natural_premises: Lista de premisas en texto natural
        natural_conclusion: Conclusión en texto natural
        provider: "openai" o "openrouter"
        model: Modelo específico (opcional, usa defaults si None)
               Puedes usar alias como "deepseek-r1" o "qwen" para modelos gratuitos
        reasoning_effort: Nivel de esfuerzo de reasoning ("medium" o "high", default: "medium")
                         Solo aplica a modelos con reasoning (deepseek-r1, glm-4.5-air, kimi-vl-a3b-thinking)
    
    Returns:
        Dict con información de alineación
    """
    if provider == "openai":
        model = model or "gpt-4o-mini"
        return align_subformula_with_openai(subformula_fol, natural_premises, natural_conclusion, model)
    elif provider == "openrouter":
        # Si el modelo es un alias de modelo gratuito, expandirlo
        if model and model.lower() in FREE_MODELS:
            model = FREE_MODELS[model.lower()]
        else:
            model = model or "openai/gpt-4o-mini"
        return align_subformula_with_openrouter(subformula_fol, natural_premises, natural_conclusion, model, reasoning_effort)
    else:
        return {
            "error": f"Proveedor desconocido: {provider}. Usa 'openai' o 'openrouter'",
            "span": None,
            "location": "ERROR",
            "confidence": 0.0
        }

