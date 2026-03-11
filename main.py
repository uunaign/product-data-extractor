import json
from openai import OpenAI
import rich
import rich.console
import rich.table
import rich.panel
import rich.box
import os
import time

console = rich.console.Console()

client = OpenAI(
    base_url="https://hermes.ai.unturf.com/v1",
    api_key="uncloseai"
)

def get_product_stats(enlace):
    model_id = "adamo1139/Hermes-3-Llama-3.1-8B-FP8-Dynamic"
    
    prompt = f'''Actúa como un experto en extracción de datos y análisis de productos. Tu objetivo es buscar y analizar el siguiente producto/enlace: {enlace}.

Instrucciones de formato (ESTRICTO): Responde exclusivamente con un objeto JSON válido. Sin texto extra.
{{
  "item_nombre": "Nombre completo y modelo del producto",
  "metadatos": {{
    "categoria": "Categoría específica",
    "moneda": "EUR",
    "fuentes_verificadas": 0
  }},
  "detalles_tecnicos": {{
    "Llave_en_Snake_Case": "Valor descriptivo"
  }},
  "valor_comercial": 0.00
}}

Reglas:
1. Extrae detalles técnicos reales (batería, dimensiones, materiales, sensores).
2. Usa snake_case para las llaves.
3. Convierte el precio a EUR (float) o null si no existe.
4. Si no conoces un dato, no lo inventes, omite la llave.'''

    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "Eres un extractor de datos que solo habla en JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        raw_content = response.choices[0].message.content
        
        clean_json = raw_content.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)

    except Exception as e:
        return {"error": f"Error en la solicitud: {str(e)}"}



def render_product_data(data):
    if not data or "error" in data:
        console.print(f"ERROR_LOG: {data.get('error', 'DATA_NULL')}", style="bold red")
        return

    console.print("\n")
    console.print(rich.panel.Panel(
        f"[bold]{data['item_nombre'].upper()}[/bold]",
        subtitle=f"CAT: {data['metadatos']['categoria'].upper()}",
        subtitle_align="left",
        border_style="white",
        expand=True
    ))

    price = data.get('valor_comercial')
    currency = data['metadatos'].get('moneda', 'EUR')
    val_str = f"{price} {currency}" if price else "N/A"
    console.print(f" MARKET_VALUE: {val_str}")

    table = rich.table.Table(
        box=rich.box.ASCII2,
        show_header=True,
        header_style="bold white",
        expand=True,
        padding=(0, 1)
    )
    
    table.add_column("SPECIFICATION_ID", style="dim")
    table.add_column("DATA_VALUE")

    tech_specs = data.get("detalles_tecnicos", {})
    for key, value in tech_specs.items():
        table.add_row(key.replace("_", " ").upper(), str(value))

    console.print(table)

# ---- MAIN CODIGO ----
enlace_usuario = input("Introduce nombre o enlace del producto: ")
print("Consultando...")
time.sleep(2)

response = get_product_stats(enlace_usuario)
time.sleep(2)
print("Resultados encontrados...")
time.sleep(1)
print("Cargando resultados")
time.sleep(2)
os.system('cls' if os.name == 'nt' else 'clear')
render_product_data(response)