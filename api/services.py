import requests
import pandas as pd

HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }


class ColdChainService:

    def __init__(self):
        pass

    async def post_temperature(self, temperature: float, timestamp: str):
        # TODO: Implement temperature posting logic
        return {}

    async def get_advise_for_food_item(self, barcode: str):


        table = pd.read_excel("./manuel_correspondance.xlsx")

        # Get food data from API
        food_data = self.get_food_data(barcode)
        
        # Extract category from the food data and get the first category if multiple exist
        category = food_data["Catégorie"].split(',')[0].strip()

        print(category)

        # Filter the table for matching category and get temperature
        matching_rows = table[table["catégorie"] == category]
        
        # Check if we found any matching categories
        if matching_rows.empty:
            return {"error": "No matching category found"}
            
        temperature = matching_rows["TEMPÉRATURE DE CONSERVATION"].iloc[0]
        return temperature

    @staticmethod  # Add staticmethod decorator since this doesn't use self
    def get_food_data(barcode: str):  # Add barcode parameter
        """Récupère les informations d'un aliment à partir de son code-barres via l'API Open Food Facts."""
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("status") == 1:  # Produit trouvé
                    product = data.get("product", {})
                    return {
                        "Nom": product.get("product_name", "Non disponible"),
                        #"Marque": product.get("brands", "Non disponible"),
                        "Catégorie": product.get("pnns_groups_1", "Non disponible")
                        #"Ingrédients": product.get("ingredients_text", "Non disponible"),
                        #"Énergie (kcal)": product.get("nutriments", {}).get("energy-kcal_100g", "Non disponible"),
                        #"Conservation": product.get("conservation_conditions", "Non disponible"),
                        #"URL": product.get("url", "Non disponible")
                    }
                else:
                    return {"Erreur": "Produit non trouvé"}
            except requests.exceptions.JSONDecodeError:
                return {"Erreur": "Réponse JSON invalide"}
        else:
            return {"Erreur": f"Échec de la requête (statut {response.status_code})"}