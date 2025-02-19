import requests
import pandas as pd
import os
import json
from datetime import datetime

HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }


class ColdChainService:

    def __init__(self):
        pass

    async def post_temperature(self, temperature: float, timestamp: str, captorId: str):
        # Fonction helper pour obtenir le prochain ID de coupure
        def get_next_coupure_id():
            if os.path.exists('log_coupure.csv') and os.path.getsize('log_coupure.csv') > 0:
                coupures_df = pd.read_csv('log_coupure.csv')
                if len(coupures_df) > 0:
                    return max([int(id.split('_')[1]) for id in coupures_df['coupureID']]) + 1
            return 1


        # Gestion du fichier de température
        if os.path.exists('log_temperature.csv') and os.path.getsize('log_temperature.csv') > 0:
            existing_df = pd.read_csv('log_temperature.csv')
            
            # Vérifier si la ligne existe déjà
            duplicate = existing_df[
                (existing_df['capteurID'] == captorId) & 
                (existing_df['temperature'] == temperature) & 
                (existing_df['timestamp'] == timestamp)
            ].empty == False
            
            if not duplicate:
                new_row = pd.DataFrame({
                    'capteurID': [captorId],
                    'temperature': [temperature],
                    'timestamp': [timestamp]
                })
                existing_df = pd.concat([existing_df, new_row], ignore_index=True)
                existing_df.to_csv('log_temperature.csv', index=False)
        else:
            new_df = pd.DataFrame({
                'capteurID': [captorId],
                'temperature': [temperature],
                'timestamp': [timestamp]
            })
            new_df.to_csv('log_temperature.csv', index=False)

        # Gestion des coupures
        # Créer le fichier s'il n'existe pas
        if not os.path.exists('log_coupure.csv'):
            pd.DataFrame(columns=['coupureID', 'capteurID', 'timestamp_debut', 'timestamp_fin']).to_csv('log_coupure.csv', index=False)

        coupures_df = pd.read_csv('log_coupure.csv')

        # Vérifier s'il y a une coupure en cours pour ce capteur
        coupure_en_cours = coupures_df[
            (coupures_df['capteurID'] == captorId) & 
            (coupures_df['timestamp_fin'].isna())
        ]

        if len(coupure_en_cours) > 0:
            # Il y a une coupure en cours
            if temperature <= 4.0:
                # La température est redevenue normale, on met à jour la fin de la coupure
                coupures_df.loc[coupure_en_cours.index, 'timestamp_fin'] = timestamp
                coupures_df.to_csv('log_coupure.csv', index=False)
        else:
            # Pas de coupure en cours
            if temperature > 4.0:
                # Nouvelle coupure détectée
                new_coupure = pd.DataFrame({
                    'coupureID': [f'COUP_{get_next_coupure_id()}'],
                    'capteurID': [captorId],
                    'timestamp_debut': [timestamp],
                    'timestamp_fin': [None]
                })
                coupures_df = pd.concat([coupures_df, new_coupure], ignore_index=True)
                coupures_df.to_csv('log_coupure.csv', index=False)

        return {"message": "Données traitées avec succès"}

    async def get_advise_for_food_item(self, barcode: str, capteurID: str):
        import pandas as pd
        import os

        # Vérifier d'abord si le capteur a une coupure en cours
        if os.path.exists('log_coupure.csv') and os.path.getsize('log_coupure.csv') > 0:
            coupures_df = pd.read_csv('log_coupure.csv')
            coupure_en_cours = coupures_df[
                (coupures_df['capteurID'] == capteurID) & 
                (coupures_df['timestamp_fin'].isna())
            ]
            has_active_coupure = 1 if len(coupure_en_cours) > 0 else 0
        else:
            has_active_coupure = 0

        # Lecture de la table de correspondance
        table = pd.read_excel("./manuel_correspondance.xlsx")

        # Get food data from API
        food_data = self.get_food_data(barcode)
        
        # Extract category from the food data and get the first category if multiple exist
        category = food_data["Catégorie"].split(',')[0].strip()

        # Filter the table for matching category and get temperature
        matching_rows = table[table["catégorie"] == category]
        
        # Check if we found any matching categories
        if matching_rows.empty:
            return {
                "error": "No matching category found",
                "has_active_coupure": has_active_coupure
            }
            
        temperature = matching_rows["TEMPÉRATURE DE CONSERVATION"].iloc[0]

        return {
            "temperature": temperature,
            "has_active_coupure": has_active_coupure
        }

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